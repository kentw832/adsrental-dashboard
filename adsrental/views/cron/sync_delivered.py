'Sync delivered status from ShippingAPI'
import datetime
from multiprocessing.pool import ThreadPool

from django.views import View
from django.http import JsonResponse
from django.utils import timezone
from django_bulk_update.helper import bulk_update

from adsrental.models.lead import Lead
from adsrental.utils import CustomerIOClient


class SyncDeliveredView(View):
    '''
    Get data from *https://secure.shippingapis.com/ShippingAPI.dll* and update *pi_delivered* field in :model:`adsrental.Lead.`
    Run by cron hourly.

    Parameters:

    * all - if 'true' runs through all leads including delivered. this can take a while.
    * test - if 'true' does not make any changes to DB or send customerIO events
    * days_ago - check only leads shipped N days ago. Default 31
    * threads - amount of threads to send requests to remote server. Default 10.
    '''
    def get_tracking_info(self, lead):
        'Miltithreding func to build array fo results'
        tracking_info_xml = lead.get_shippingapis_tracking_info()
        return [lead.email, tracking_info_xml]

    def get(self, request):
        'Get endpoint'
        leads = []
        delivered = []
        not_delivered = []
        errors = []
        changed = []
        process_all = request.GET.get('all') == 'true'
        test = request.GET.get('test') == 'true'
        threads = int(request.GET.get('threads', 10))
        days_ago = int(request.GET.get('days_ago', 31))
        if process_all:
            leads = Lead.objects.filter(
                status__in=Lead.STATUSES_ACTIVE,
                usps_tracking_code__isnull=False,
                ship_date__gte=timezone.now() - datetime.timedelta(days=days_ago),
            ).prefetch_related('raspberry_pi')
        else:
            leads = Lead.objects.filter(
                status__in=Lead.STATUSES_ACTIVE,
                usps_tracking_code__isnull=False,
                pi_delivered=False,
                ship_date__gte=timezone.now() - datetime.timedelta(days=days_ago),
            ).prefetch_related('raspberry_pi')
        pool = ThreadPool(processes=threads)
        results = pool.map(self.get_tracking_info, leads)
        results_map = dict(results)
        for lead in leads:
            label = lead.raspberry_pi.rpid if lead.raspberry_pi else lead.email
            tracking_info_xml = results_map.get(lead.email)
            pi_delivered = lead.get_pi_delivered_from_xml(tracking_info_xml)
            if pi_delivered is None:
                errors.append(label)
                continue
            lead.tracking_info = tracking_info_xml
            if pi_delivered is not None and pi_delivered != lead.pi_delivered:
                changed.append(label)
                if not test and pi_delivered:
                    CustomerIOClient().send_lead_event(lead, CustomerIOClient.EVENT_DELIVERED, tracking_code=lead.usps_tracking_code)
            lead.update_pi_delivered(pi_delivered, tracking_info_xml)

            if pi_delivered:
                delivered.append(label)
            else:
                not_delivered.append(label)

        if not test:
            bulk_update(leads, update_fields=['tracking_info', 'pi_delivered', 'delivery_date'])
        else:
            bulk_update(leads, update_fields=['tracking_info', ])

        return JsonResponse({
            'all': process_all,
            'result': True,
            'changed': changed,
            'delivered': delivered,
            'not_delivered': not_delivered,
            'errors': errors,
        })
