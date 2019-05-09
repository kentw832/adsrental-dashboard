from django.contrib import admin, messages
from django.urls import reverse
from django.utils import timezone
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils.safestring import mark_safe
from django.db.models import Value
from django.db.models.functions import Concat

from adsrental.models.ec2_instance import EC2Instance
from adsrental.admin.list_filters import LeadRaspberryPiOnlineListFilter, LeadRaspberryPiVersionListFilter, LeadStatusListFilter, LastTroubleshootListFilter, TunnelUpListFilter
from adsrental.utils import BotoResource, PingCacheHelper


class EC2InstanceAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/custom_admin.css',)
        }

    model = EC2Instance
    list_display = (
        'id',
        'hostname',
        'instance_type',
        'browser_type',
        'lead_link',
        'lead_status',
        'raspberry_pi_link',
        'version',
        'raspberry_pi_version',
        'status',
        'last_rdp_session',
        'last_seen',
        'last_troubleshoot_field',
        'tunnel_up_date_field',
        'links',
        'raspberry_pi_online',
    )
    list_filter = (
        'status',
        'instance_type',
        'browser_type',
        'is_essential',
        TunnelUpListFilter,
        LeadStatusListFilter,
        LeadRaspberryPiOnlineListFilter,
        LeadRaspberryPiVersionListFilter,
        LastTroubleshootListFilter,
    )
    readonly_fields = ('created', 'updated', )
    search_fields = ('instance_id', 'email', 'rpid', 'lead__leadid', 'essential_key', )
    list_select_related = ('lead', 'lead__raspberry_pi', )
    actions = (
        'update_ec2_tags',
        'get_currect_state',
        'start',
        'stop',
        'restart_raspberry_pi',
        'clear_ping_cache',
        'terminate',
        'update_password',
        'upgrade_to_large',
        'launch_essential_ec2',
        'check_status',
    )
    raw_id_fields = ('lead', )

    def lead_link(self, obj):
        if obj.lead is None:
            return obj.email
        return mark_safe('<a href="{url}?leadid={q}">{lead}</a>'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            lead=obj.lead.email,
            q=obj.lead.leadid,
        ))

    def lead_status(self, obj):
        return obj.lead and obj.lead.status

    def raspberry_pi_link(self, obj):
        if obj.lead is None or obj.lead.raspberry_pi is None:
            return obj.rpid
        return mark_safe('<a href="{url}?rpid={q}">{rpid}</a>'.format(
            url=reverse('admin:adsrental_raspberrypi_changelist'),
            rpid=obj.lead.raspberry_pi.rpid,
            q=obj.lead.raspberry_pi.rpid,
        ))

    def raspberry_pi_online(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.online()

    def raspberry_pi_version(self, obj):
        return obj.lead and obj.lead.raspberry_pi and obj.lead.raspberry_pi.version

    def last_seen(self, obj):
        raspberry_pi = obj.get_raspberry_pi()
        if not raspberry_pi:
            return None

        last_seen = raspberry_pi.get_last_seen()
        if not last_seen:
            return None

        return mark_safe(u'<span title="{}">{}</span>'.format(last_seen, naturaltime(last_seen)))

    def last_rdp_session(self, obj):
        if not obj.last_rdp_start:
            return None

        date = obj.last_rdp_start
        return mark_safe(u'<span title="{}">{}</span>'.format(date, naturaltime(date)))

    def last_troubleshoot_field(self, obj):
        if obj.last_troubleshoot is None:
            return 'Never'

        date = obj.last_troubleshoot
        return mark_safe(u'<span title="{}">{}</span>'.format(date, naturaltime(date)))

    def tunnel_up_date_field(self, obj):
        if obj.tunnel_up_date is None:
            return 'Never'

        date = obj.tunnel_up_date
        is_tunnel_up = obj.is_tunnel_up()
        return mark_safe(u'<span title="{}">{}</span>'.format(
            date,
            'Yes' if is_tunnel_up else naturaltime(date),
        ))

    def links(self, obj):
        links = []
        if obj.rpid:
            links.append('<a href="{url}">RDP</a>'.format(
                url=reverse('rdp_ec2_connect', kwargs=dict(rpid=obj.rpid)),
            ))
        if obj.lead:
            links.append('<a href="{url}">pi.conf</a>'.format(
                url=reverse('pi_config', kwargs=dict(rpid=obj.rpid)),
            ))
        if obj.lead and obj.lead.raspberry_pi:
            now = timezone.localtime(timezone.now())
            today_log_filename = '{}.log'.format(now.strftime(settings.LOG_DATE_FORMAT))
            links.append('<a href="{log_url}">Today log</a>'.format(
                log_url=reverse('show_log', kwargs={'rpid': obj.rpid, 'filename': today_log_filename}),
            ))
            links.append('<a href="{url}">Netstat</a>'.format(
                url=reverse('ec2_ssh_get_netstat', kwargs=dict(rpid=obj.rpid)),
            ))
            links.append('<a href="{url}">RTunnel</a>'.format(
                url=reverse('ec2_ssh_start_reverse_tunnel', kwargs=dict(rpid=obj.rpid)),
            ))

        links.append('<a href="#" title="ssh -o StrictHostKeyChecking=no -i ~/.ssh/farmbot Administrator@{hostname} -p 40594">Copy SSH</a>'.format(
            hostname=obj.hostname,
        ))
        return mark_safe(', '.join(links))

    def update_ec2_tags(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.set_ec2_tags()

    def get_currect_state(self, request, queryset):
        if queryset.count() > 10:
            boto_resource = BotoResource()
            for ec2_boto in boto_resource.get_resource('ec2').instances.all():
                ec2 = EC2Instance.objects.filter(instance_id=ec2_boto.id).first()
                if ec2:
                    ec2.update_from_boto(ec2_boto)

        for ec2_instance in queryset:
            ec2_instance.update_from_boto()

    def start(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.start()

    def stop(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.stop()

    def restart_raspberry_pi(self, request, queryset):
        for ec2_instance in queryset:
            if ec2_instance.lead and ec2_instance.lead.raspberry_pi:
                ec2_instance.lead.raspberry_pi.restart_required = True
                ec2_instance.lead.raspberry_pi.save()
                PingCacheHelper().delete(ec2_instance.rpid)

    def clear_ping_cache(self, request, queryset):
        for ec2_instance in queryset:
            PingCacheHelper().delete(ec2_instance.rpid)

    def terminate(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.terminate()

    def update_password(self, request, queryset):
        for ec2_instance in queryset:
            ec2_instance.change_password(ec2_instance.password)

    def upgrade_to_large(self, request, queryset):
        client = BotoResource().get_client('ec2')
        for ec2_instance in queryset:
            if ec2_instance.instance_type == EC2Instance.INSTANCE_TYPE_M5_LARGE:
                messages.warning(request, 'EC2 was already upgraded')
                continue
            ec2_instance.update_from_boto()
            if ec2_instance.status != EC2Instance.STATUS_STOPPED:
                messages.success(request, 'EC2 should be stopped first')
                continue

            client.modify_instance_attribute(InstanceId=ec2_instance.instance_id, Attribute='instanceType', Value=EC2Instance.INSTANCE_TYPE_M5_LARGE)
            ec2_instance.instance_type = EC2Instance.INSTANCE_TYPE_M5_LARGE
            ec2_instance.save()
            messages.success(request, 'EC2 is upgraded successfully')

    def launch_essential_ec2(self, request, queryset):
        ec2_instance = EC2Instance.launch_essential()
        messages.success(request, 'Essential EC2 {} is started successfully'.format(ec2_instance.essential_key))

    def check_status(self, request, queryset):
        for ec2 in queryset:
            if not ec2.lead:
                continue

            ec2_client = BotoResource().get_client('ec2')
            statuses = ec2_client.describe_instance_status(
                InstanceIds=[ec2.instance_id],
                IncludeAllInstances=True
            )
            if statuses['InstanceStatuses'][0]['InstanceStatus']['Status'] == 'impaired':
                ec2.lead = None
                ec2.rpid = 'OLD:' + ec2.rpid
                ec2.save()
                ec2.set_ec2_tags()
                ec2.stop()
                messages.info(request, 'Essential EC2 {} status is stopped and unassigned: {}'.format(ec2.rpid, statuses))
            else:
                messages.success(request, 'Essential EC2 {} status is okay: {}'.format(ec2.rpid, statuses))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = Concat('lead__first_name', Value(' '), 'lead__last_name')

    raspberry_pi_link.short_description = 'RaspberryPi'

    raspberry_pi_version.short_description = 'RPi Version'

    raspberry_pi_online.boolean = True
    raspberry_pi_online.short_description = 'RPi Online'

    last_troubleshoot_field.short_description = 'Troubleshoot'
    last_troubleshoot_field.admin_order_field = 'last_troubleshoot'

    tunnel_up_date_field.short_description = 'Tunnel up'
    tunnel_up_date_field.admin_order_field = 'tunnel_up_date'

    last_seen.admin_order_field = 'lead__raspberry_pi__last_seen'

    clear_ping_cache.short_description = 'DEBUG: Clear ping cache'

    terminate.short_description = 'DEBUG: Terminate'

    upgrade_to_large.short_description = 'DEBUG: Upgrade to M5 Large instance'

    launch_essential_ec2.short_description = 'DEBUG: Launch essential EC2'

    check_status.short_description = 'DEBUG: Check status'
