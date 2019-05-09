import html

from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Value
from django.db.models.functions import Concat

from adsrental.models.lead_change import LeadChange

from adsrental.admin.list_filters import AbstractUIDListFilter, AbstractIntIDListFilter, EditedByListFilter
from adsrental.admin.base import ReadOnlyModelAdmin


class LeadLeadidListFilter(AbstractUIDListFilter):
    parameter_name = 'lead__leadid'
    title = 'Lead ID'


class LeadAccountIDListFilter(AbstractIntIDListFilter):
    parameter_name = 'lead_account_id'
    title = 'LeadAccount ID'


class LeadChangeAdmin(ReadOnlyModelAdmin):
    model = LeadChange
    list_display = (
        'id',
        'lead_link',
        'lead_account_field',
        'field',
        'value_field',
        'old_value_field',
        'edited_by',
        'created',
    )
    list_select_related = ('lead', 'lead_account', )
    list_filter = (
        'field',
        EditedByListFilter,
        LeadLeadidListFilter,
        LeadAccountIDListFilter,
    )
    search_fields = ('lead__email', 'lead__raspberry_pi__rpid', )

    def value_field(self, obj):
        if obj.value == 'False':
            return mark_safe('<img src="/static/admin/img/icon-no.svg" title="False" alt="False">')
        if obj.value == 'True':
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" title="True" alt="True">')

        return obj.value

    def old_value_field(self, obj):
        if obj.old_value == 'False':
            return mark_safe('<img src="/static/admin/img/icon-no.svg" title="False" alt="False">')
        if obj.old_value == 'True':
            return mark_safe('<img src="/static/admin/img/icon-yes.svg" title="True" alt="True">')

        return obj.old_value

    def lead_link(self, obj):
        lead = obj.lead
        if not lead:
            return None
        return mark_safe('<a href="{url}?leadid={q}">{text}</a>{note}'.format(
            url=reverse('admin:adsrental_lead_changelist'),
            text=lead.name(),
            q=lead.leadid,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(lead.note)}" alt="?">' if lead.note else '',
        ))

    def lead_account_field(self, obj):
        lead_account = obj.lead_account
        if not lead_account:
            return None
        return mark_safe('<a href="{url}?id={id}">{type} {username}</a>{note}'.format(
            url=reverse('admin:adsrental_leadaccount_changelist'),
            type=lead_account.get_account_type_display(),
            username=lead_account.username,
            id=lead_account.id,
            note=f' <img src="/static/admin/img/icon-unknown.svg" title="{html.escape(lead_account.note)}" alt="?">' if lead_account.note else '',
        ))

    lead_link.short_description = 'Lead'
    lead_link.admin_order_field = Concat('lead__first_name', Value(' '), 'lead__last_name')

    lead_account_field.short_description = 'Lead Account'
    lead_account_field.admin_order_field = 'lead_account__username'

    value_field.short_description = 'Value'
    old_value_field.short_description = 'Old Value'
