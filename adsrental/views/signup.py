import uuid
import json

from django.views import View
from django.shortcuts import render, redirect
from django.shortcuts import Http404
from django.conf import settings
import django.db

from adsrental.forms import SignupForm, SafeSignupForm
from adsrental.models.lead import Lead
from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler import Bundler
from adsrental.utils import CustomerIOClient


class SignupView(View):
    form_class = SafeSignupForm if settings.LOCAL else SignupForm

    def get(self, request):
        if 'utm_source' in request.GET:
            utm_source = request.GET.get('utm_source')
            request.session['utm_source'] = utm_source

        utm_source = request.session.get('utm_source')
        if not utm_source:
            raise Http404

        bundler = Bundler.objects.filter(utm_source=utm_source, is_active=True).first()
        if not bundler:
            raise Http404

        landing_form_data = {}
        landing_form_data_raw = request.session.get('landing_form_data')
        if landing_form_data_raw:
            landing_form_data = json.loads(landing_form_data_raw)
            request.session['landing_form_data'] = None

        form_initial_data = {
            'utm_source': utm_source,
            'age_check': True,
        }
        form_initial_data.update(landing_form_data)

        return render(request, 'signup.html', dict(
            user=request.user,
            utm_source=request.GET.get('utm_source'),
            isp='',
            remote_addr=request.META.get('REMOTE_ADDR'),
            form=self.form_class(initial=form_initial_data),
        ))

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if not form.is_valid():
            # raise ValueError(form.errors)
            form_errors = []
            for error_list in form.errors.values():
                for error in error_list:
                    form_errors.append(error)
            return render(request, 'signup.html', dict(
                user=request.user,
                isp='',
                form_errors=form_errors,
                remote_addr=request.META.get('REMOTE_ADDR'),
                form=form,
            ))

        data = form.cleaned_data

        lead = Lead.objects.filter(email=data['email']).first()
        if lead:
            return redirect('thankyou_email', leadid=lead.leadid)

        lead_id = str(uuid.uuid4()).replace('-', '')

        lead = Lead(
            leadid=lead_id,
            account_name='',
            first_name=data['first_name'],
            last_name=data['last_name'],
            status=Lead.STATUS_AVAILABLE,
            email=data['email'],
            phone=data['phone'],
            utm_source=data['utm_source'],
            bundler=Bundler.get_by_utm_source(data['utm_source']),
            # facebook_account=True,
            # facebook_account_status=Lead.STATUS_AVAILABLE,
            # fb_email=data['fb_email'],
            # fb_secret=data['fb_secret'],
            # fb_friends=data['fb_friends'],
            # fb_profile_url=data['facebook_profile_url'],
            apartment=data.get('apartment'),
            street=data['street'],
            company=Lead.COMPANY_FBM,
            city=data['city'],
            state=data['state'],
            postal_code=data['postal_code'],
            country='United States',
            photo_id=data['photo_id'],
            extra_photo_id=data['extra_photo_id'],
        )
        try:
            lead.save()
        except django.db.Error:
            form_errors = ['This account is already registered']
            return render(request, 'signup.html', dict(
                user=request.user,
                isp='',
                form_errors=form_errors,
                remote_addr=request.META.get('REMOTE_ADDR'),
                form=form,
            ))

        account_type = LeadAccount.ACCOUNT_TYPE_FACEBOOK
        if data['apply_type'] == SignupForm.APPLY_TYPE_SCREENSHOT:
            account_type = LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT

        lead_account = LeadAccount(
            lead=lead,
            username=data['fb_email'],
            password=data['fb_secret'],
            friends=data['fb_friends'],
            account_url=data['facebook_profile_url'],
            status=LeadAccount.STATUS_AVAILABLE,
            primary=True,
            account_type=account_type,
        )
        lead_account.save()
        # lead.send_web_to_lead()

        customerio_client = CustomerIOClient()
        customerio_client.send_lead(lead)
        customerio_client.send_lead_event(lead, CustomerIOClient.EVENT_APPROVED, account_type='facebook')
        if account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
            return redirect('thankyou_screenshot')
        return redirect('thankyou_email', leadid=lead.leadid)
