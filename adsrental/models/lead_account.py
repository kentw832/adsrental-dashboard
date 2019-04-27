'LeadAccount model'
from __future__ import annotations

import decimal
import typing
import datetime

import requests
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.utils import dateformat
from django_bulk_update.query import BulkUpdateQuerySet
from django.contrib.contenttypes.fields import GenericRelation

from adsrental.models.mixins import FulltextSearchMixin
from adsrental.models.raspberry_pi import RaspberryPi
from adsrental.models.lead import Lead
from adsrental.models.comment import Comment
from adsrental.models.lead_change import LeadChange
from adsrental.models.bundler_payment import BundlerPayment
from adsrental.utils import CustomerIOClient, AdsdbClient

if typing.TYPE_CHECKING:
    from adsrental.models.user import User
    from adsrental.models.bundler import Bundler


class LeadAccountQuerySet(BulkUpdateQuerySet):
    def get_adsdb_data(self, **kwargs):
        adsdb_ids = tuple(filter(lambda x: x is not None, map(lambda x: x[0], self.values_list('adsdb_account_id'))))
        adsdb_accounts = AdsdbClient().get_accounts_by_ids(ids=adsdb_ids, **kwargs)
        adsdb_accounts_map = {}
        for adsdb_account in adsdb_accounts:
            adsdb_accounts_map[str(adsdb_account['id'])] = adsdb_account
        for lead_account in self:
            lead_account.adsdb_account = adsdb_accounts_map.get(lead_account.adsdb_account_id, None)

        return self

    def get_adsdb_data_safe(self, **kwargs):
        adsdb_accounts = AdsdbClient().get_accounts(**kwargs)
        adsdb_accounts_map = {}
        for adsdb_account in adsdb_accounts:
            adsdb_accounts_map[str(adsdb_account['id'])] = adsdb_account
        for lead_account in self:
            lead_account.adsdb_account = adsdb_accounts_map.get(lead_account.adsdb_account_id, None)

        return self


class LeadAccountManager(models.Manager.from_queryset(LeadAccountQuerySet)):
    pass


class LeadAccount(models.Model, FulltextSearchMixin):
    class Meta:
        unique_together = (
            ('username', 'account_type', 'lead', ),
            ('account_type', 'lead', ),
        )
        permissions = (
            ("view", "Can access lead account info"),
        )

    LAST_SECURITY_CHECKPOINT_REPORTED_HOURS_TTL = 48
    CHARGE_BACK_DAYS_OLD = 61
    AUTO_BAN_DAYS_WRONG_PASSWORD = 14
    AUTO_BAN_DAYS_OFFLINE = 14
    AUTO_BAN_DAYS_SEC_CHECKPOINT = 14
    AUTO_BAN_DAYS_NOT_USED = 14
    AUTO_BAN_DAYS_NO_ACTIVE_ACCOUNTS = 4
    MAX_WRONG_PASSWORD_CHANGE_COUNTER = 3

    STATUS_QUALIFIED = 'Qualified'
    STATUS_DISQUALIFIED = 'Disqualified'
    STATUS_SCREENSHOT_DISQUALIFIED = 'Screenshot Disqualified'
    STATUS_NEEDS_APPROVAL = 'Needs approval'
    STATUS_AVAILABLE = 'Available'
    STATUS_IN_PROGRESS = 'In-Progress'
    STATUS_BANNED = 'Banned'
    STATUS_ACTIVE = 'Active'
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, 'Available'),
        (STATUS_BANNED, 'Banned'),
        (STATUS_QUALIFIED, 'Qualified'),
        (STATUS_IN_PROGRESS, 'In-Progress'),
        (STATUS_DISQUALIFIED, 'Disqualified'),
        (STATUS_SCREENSHOT_DISQUALIFIED, 'Screenshot Disqualified'),
        (STATUS_NEEDS_APPROVAL, 'Needs approval'),
    ]

    STATUSES_ACTIVE = [STATUS_AVAILABLE, STATUS_QUALIFIED, STATUS_IN_PROGRESS, STATUS_NEEDS_APPROVAL]

    ACCOUNT_TYPE_FACEBOOK = 'Facebook'
    ACCOUNT_TYPE_FACEBOOK_SCREENSHOT = 'Facebook Screenshot'
    ACCOUNT_TYPE_GOOGLE = 'Google'
    ACCOUNT_TYPE_AMAZON = 'Amazon'
    ACCOUNT_TYPES_FACEBOOK = (ACCOUNT_TYPE_FACEBOOK, ACCOUNT_TYPE_FACEBOOK_SCREENSHOT)
    ACCOUNT_TYPE_CHOICES = [
        (ACCOUNT_TYPE_FACEBOOK, 'Facebook', ),
        (ACCOUNT_TYPE_FACEBOOK_SCREENSHOT, 'Facebook Screenshot', ),
        (ACCOUNT_TYPE_GOOGLE, 'Google', ),
        (ACCOUNT_TYPE_AMAZON, 'Amazon', ),
    ]
    ACCOUNT_TYPES_NEED_APPROVAL = (ACCOUNT_TYPE_FACEBOOK_SCREENSHOT, ACCOUNT_TYPE_GOOGLE)

    BAN_REASON_AUTO_OFFLINE = 'auto_offline'
    BAN_REASON_AUTO_WRONG_PASSWORD = 'auto_wrong_password'
    BAN_REASON_AUTO_CHECKPOINT = 'auto_checkpoint'
    BAN_REASON_AUTO_NOT_USED = 'auto_not_used'
    BAN_REASON_FACEBOOK_UNRESPONSIVE_USER = 'Facebook - Unresponsive User'
    BAN_REASON_GOOGLE_UNRESPONSIVE_USER = 'Google - Unresponsive User'
    BAN_REASON_GOOGLE_POLICY = 'Google - Policy'
    BAN_REASON_GOOGLE_BILLING = 'Google - Billing'
    BAN_REASON_FACEBOOK_POLICY = 'Facebook - Policy'
    BAN_REASON_FACEBOOK_SUSPICIOUS = 'Facebook - Suspicious'
    BAN_REASON_FACEBOOK_LOCKOUT = 'Facebook - Lockout'
    BAN_REASON_ADSDB = 'ADSDB'
    BAN_REASON_QUIT = 'Quit'
    BAN_REASON_BAD_AD_ACCOUNT = 'Bad ad account'
    BAN_REASON_DUPLICATE = 'Duplicate'
    BAN_REASON_OTHER = 'Other'

    POLICY_BAN_REASONS = (
        BAN_REASON_GOOGLE_POLICY,
        BAN_REASON_GOOGLE_BILLING,
        BAN_REASON_FACEBOOK_POLICY,
        BAN_REASON_FACEBOOK_SUSPICIOUS,
        BAN_REASON_FACEBOOK_LOCKOUT,
    )

    AUTO_BAN_REASONS = (
        BAN_REASON_AUTO_OFFLINE,
        BAN_REASON_AUTO_WRONG_PASSWORD,
        BAN_REASON_AUTO_CHECKPOINT,
        BAN_REASON_AUTO_NOT_USED,
    )

    BAN_REASON_CHOICES = (
        (BAN_REASON_GOOGLE_POLICY, 'Google - Policy', ),
        (BAN_REASON_GOOGLE_BILLING, 'Google - Billing', ),
        (BAN_REASON_GOOGLE_UNRESPONSIVE_USER, 'Google - Unresponsive User', ),
        (BAN_REASON_FACEBOOK_POLICY, 'Facebook - Policy', ),
        (BAN_REASON_FACEBOOK_SUSPICIOUS, 'Facebook - Suspicious', ),
        (BAN_REASON_FACEBOOK_LOCKOUT, 'Facebook - Lockout', ),
        (BAN_REASON_FACEBOOK_UNRESPONSIVE_USER, 'Facebook - Unresponsive User', ),
        (BAN_REASON_DUPLICATE, 'Duplicate', ),
        (BAN_REASON_BAD_AD_ACCOUNT, 'Bad ad account', ),
        (BAN_REASON_AUTO_OFFLINE, 'Auto: offline for 2 weeks', ),
        (BAN_REASON_AUTO_WRONG_PASSWORD, 'Auto: wrong password for 2 weeks', ),
        (BAN_REASON_AUTO_CHECKPOINT, 'Auto: reported security checkpoint for 2 weeks', ),
        (BAN_REASON_AUTO_NOT_USED, 'Auto: not used for 2 weeks after delivery', ),
        (BAN_REASON_ADSDB, 'Banned by Adsdb sync'),
        (BAN_REASON_QUIT, 'Quit'),
        (BAN_REASON_OTHER, 'Other', ),
    )

    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    note = models.TextField(blank=True, null=True, help_text='Not shown when you hover user name in admin interface.')
    comments = GenericRelation(Comment, blank=True)
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='lead_accounts', related_query_name='lead_account')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    old_status = models.CharField(max_length=50, choices=STATUS_CHOICES, null=True, blank=True, default=None, help_text='Used to restore previous status on Unban action')
    ban_reason = models.CharField(max_length=50, choices=BAN_REASON_CHOICES, null=True, blank=True, help_text='Populated from ban form')
    ban_note = models.TextField(null=True, blank=True, help_text='Populated from ban form')
    account_type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    friends = models.BigIntegerField(default=0)
    account_url = models.CharField(max_length=255, blank=True, null=True)
    wrong_password_date = models.DateTimeField(blank=True, null=True, help_text='Date when password was reported as wrong.')
    wrong_password_change_counter = models.IntegerField(default=0, help_text='How many times a password was changed by user.')
    qualified_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead was marked as qualified for the first time.')
    disqualified_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead was marked as disqualified for the last time.')
    in_progress_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead was marked as in-progress.')
    banned_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead was marked as qualified for the last time.')
    bundler_paid_date = models.DateField(blank=True, null=True, help_text='Date when bundler got his payment for this lead for the last time.')
    bundler_paid = models.BooleanField(default=False, help_text='Is revenue paid to bundler.')
    adsdb_account_id = models.CharField(max_length=255, unique=True, blank=True, null=True, help_text='Corresponding Account ID in Adsdb database. used for syncing between databases.')
    sync_with_adsdb = models.BooleanField(default=False)
    active = models.BooleanField(default=True, help_text='If false, entry considered as deleted')
    primary = models.BooleanField(default=False, help_text='First added account for this lead')
    billed = models.BooleanField(default=False, help_text='Did lead receive his payment.')
    last_touch_date = models.DateTimeField(blank=True, null=True, help_text='Date when lead account was touched for the last time.')
    touch_count = models.IntegerField(default=0, help_text='Increased every time you do Touch action for this lead account.')
    security_checkpoint_date = models.DateTimeField(blank=True, null=True, help_text='Date when security checkpoint has been reported.')
    last_security_checkpoint_reported = models.DateTimeField(blank=True, null=True, help_text='Date when security checkpoint notification was sent.')
    last_not_qualified_reported = models.DateTimeField(blank=True, null=True, help_text='Date whennot qualified notification was sent.')
    auto_ban_enabled = models.BooleanField(default=True, help_text='If true, lead account is banned after two weeks of offline or wrong password.')
    charge_back = models.BooleanField(default=False, help_text='Set to true on auto-ban. True if charge back should be billed to lead.')
    charge_back_billed = models.BooleanField(default=False, help_text='If change back on auto ban billed.')
    pay_check = models.BooleanField(default=True, help_text='User does not appear in check reports if turned off.')
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateTimeField(auto_now=True)

    objects = LeadAccountManager()

    def get_bundler(self) -> Bundler:
        return self.lead.bundler

    def get_adsdb_account(self, archive=False):
        if not self.adsdb_account_id:
            return None

        adsdb_accounts = AdsdbClient().get_accounts(ids=self.adsdb_account_id, archive=archive)
        if not adsdb_accounts:
            return None

        return adsdb_accounts[0]

    def get_active_timedelta(self):
        if not self.qualified_date or not self.banned_date:
            return None

        return self.banned_date - self.qualified_date

    def is_approval_needed(self):
        if self.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
            return True

        if self.primary and self.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
            return True

        return False

    def user_can_change_password(self) -> bool:
        return self.wrong_password_change_counter < LeadAccount.MAX_WRONG_PASSWORD_CHANGE_COUNTER

    def get_bundler_payment(self, bundler: Bundler) -> decimal.Decimal:
        result = decimal.Decimal('0.00')
        if self.status == LeadAccount.STATUS_IN_PROGRESS and self.lead.raspberry_pi and not self.bundler_paid:
            if self.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                result += bundler.facebook_payment
                result -= self.get_parent_bundler_payment(bundler)
                result -= self.get_second_parent_bundler_payment(bundler)
                result -= self.get_third_parent_bundler_payment(bundler)
            if self.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
                result += bundler.facebook_screenshot_payment
                result -= self.get_parent_bundler_payment(bundler)
                result -= self.get_second_parent_bundler_payment(bundler)
                result -= self.get_third_parent_bundler_payment(bundler)
            if self.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                result += bundler.google_payment
                result -= self.get_parent_bundler_payment(bundler)
                result -= self.get_second_parent_bundler_payment(bundler)
                result -= self.get_third_parent_bundler_payment(bundler)
            if self.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                result += bundler.amazon_payment
                result -= self.get_parent_bundler_payment(bundler)
                result -= self.get_second_parent_bundler_payment(bundler)
                result -= self.get_third_parent_bundler_payment(bundler)

        return result

    def get_bundler_chargeback(self, bundler: Bundler) -> decimal.Decimal:
        if not self.bundler_paid:
            return decimal.Decimal('0.00')

        if not bundler.enable_chargeback or not self.in_progress_date or not self.banned_date:
            return decimal.Decimal('0.00')

        if self.in_progress_date < self.banned_date - datetime.timedelta(days=self.CHARGE_BACK_DAYS_OLD):
            return decimal.Decimal('0.00')

        if self.ban_reason not in (
                LeadAccount.BAN_REASON_QUIT,
                LeadAccount.BAN_REASON_FACEBOOK_UNRESPONSIVE_USER,
                LeadAccount.BAN_REASON_GOOGLE_UNRESPONSIVE_USER,
                LeadAccount.BAN_REASON_AUTO_OFFLINE,
                LeadAccount.BAN_REASON_AUTO_WRONG_PASSWORD,
                LeadAccount.BAN_REASON_BAD_AD_ACCOUNT,
                LeadAccount.BAN_REASON_DUPLICATE,
        ):
            return decimal.Decimal('0.00')

        if not self.charge_back:
            self.charge_back = True
            self.save()

        if self.account_type in LeadAccount.ACCOUNT_TYPES_FACEBOOK and bundler.facebook_chargeback:
            return - bundler.facebook_chargeback
        if self.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE and bundler.google_chargeback:
            return - bundler.google_chargeback
        if self.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON and bundler.amazon_chargeback:
            return - bundler.amazon_chargeback

        return decimal.Decimal('0.00')

    def get_parent_bundler_payment(self, bundler: Bundler) -> decimal.Decimal:
        result = decimal.Decimal('0.00')
        if bundler.parent_bundler and self.status == LeadAccount.STATUS_IN_PROGRESS and not self.bundler_paid:
            if self.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK:
                result += bundler.facebook_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
                result += bundler.facebook_screenshot_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                result += bundler.google_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                result += bundler.amazon_parent_payment

        return result

    def get_second_parent_bundler_payment(self, bundler: Bundler) -> decimal.Decimal:
        result = decimal.Decimal('0.00')
        if bundler.second_parent_bundler and self.status == LeadAccount.STATUS_IN_PROGRESS and not self.bundler_paid:
            if self.account_type == self.ACCOUNT_TYPE_FACEBOOK:
                result += bundler.facebook_second_parent_payment
            if self.account_type == self.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
                result += bundler.facebook_screenshot_second_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                result += bundler.google_second_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                result += bundler.amazon_second_parent_payment

        return result

    def get_third_parent_bundler_payment(self, bundler: Bundler) -> decimal.Decimal:
        result = decimal.Decimal('0.00')
        if bundler.third_parent_bundler and self.status == LeadAccount.STATUS_IN_PROGRESS and not self.bundler_paid:
            if self.account_type == self.ACCOUNT_TYPE_FACEBOOK:
                result += bundler.facebook_third_parent_payment
            if self.account_type == self.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
                result += bundler.facebook_screenshot_third_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_GOOGLE:
                result += bundler.google_third_parent_payment
            if self.account_type == LeadAccount.ACCOUNT_TYPE_AMAZON:
                result += bundler.amazon_third_parent_payment

        return result

    def __str__(self) -> str:
        return '{} lead {}'.format(self.account_type, self.username)

    def get_lead(self) -> Lead:
        return self.lead

    def is_security_checkpoint_reported(self) -> bool:
        return self.security_checkpoint_date is not None

    def is_wrong_password(self) -> bool:
        'Is password reported as wrong now'
        return self.wrong_password_date is not None

    def _get_adsdb_api_id(self) -> int:
        if self.account_type in self.ACCOUNT_TYPES_FACEBOOK:
            return 146

        if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
            return 147

        raise ValueError()

    def sync_to_adsdb(self) -> typing.Tuple[typing.Optional[typing.Dict], typing.Dict]:
        'Send lead account info to ADSDB'

        lead = self.get_lead()
        # if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
        #     return False, {}
        if self.account_type == self.ACCOUNT_TYPE_AMAZON:
            return None, {}
        if self.status != self.STATUS_IN_PROGRESS:
            return None, {}
        if self.touch_count < lead.ADSDB_SYNC_MIN_TOUCH_COUNT and self.account_type in LeadAccount.ACCOUNT_TYPES_FACEBOOK:
            return None, {}

        bundler_adsdb_id = lead.bundler and lead.bundler.adsdb_id
        ec2_instance = lead.get_ec2_instance()
        data = dict(
            first_name=lead.first_name,
            last_name=lead.last_name,
            email=self.username,
            last_seen=dateformat.format(lead.raspberry_pi.last_seen, 'j E Y H:i') if lead.raspberry_pi and lead.raspberry_pi.last_seen else None,
            phone=lead.phone,
            ec2_hostname=ec2_instance.hostname if ec2_instance else None,
            utm_source_id=bundler_adsdb_id or settings.DEFAULT_ADSDB_BUNDLER_ID,
            rp_id=lead.raspberry_pi.rpid if lead.raspberry_pi else None,
            api_id=self._get_adsdb_api_id(),
            username=self.username,
        )

        if self.account_type in self.ACCOUNT_TYPES_FACEBOOK:
            data['fb_username'] = self.username
            data['fb_password'] = self.password
            data['category_id'] = 2
            data['ad_manager_type_2'] = 2
        if self.account_type == self.ACCOUNT_TYPE_GOOGLE:
            data['google_username'] = self.username
            data['google_password'] = self.password
            data['category_id'] = 1
            data['ad_manager_type_2'] = 7

        auth = requests.auth.HTTPBasicAuth(settings.ADSDB_USERNAME, settings.ADSDB_PASSWORD)

        if not self.adsdb_account_id:
            url = 'https://www.adsdb.io/api/v1/accounts/create-s'
            response = requests.post(
                url,
                json=[data],
                auth=auth,
            )
            try:
                response_json = response.json()
            except ValueError:
                return ({'error': True, 'url': url, 'data': [data], 'text': response.text, 'status': response.status_code}, data)
            if response.status_code == 200:
                adsdb_account_id = response_json.get('account_data')[0]['id']
                conflicting = LeadAccount.objects.filter(adsdb_account_id=adsdb_account_id).exclude(id=self.id)
                if not conflicting:
                    self.adsdb_account_id = adsdb_account_id
                    self.save()
            if response.status_code == 409:
                adsdb_account_id = response_json.get('account_data')[0]['conflict_id']
                conflicting = LeadAccount.objects.filter(adsdb_account_id=adsdb_account_id).exclude(id=self.id)
                if not conflicting:
                    self.adsdb_account_id = adsdb_account_id
                    self.save()
            return (response_json, data)

        request_data = {
            'account_id': int(self.adsdb_account_id),
            'data': data,
        }

        url = 'https://www.adsdb.io/api/v1/accounts/update-s'
        response = requests.post(
            url,
            json=request_data,
            auth=auth,
        )
        try:
            response_json = response.json()
        except ValueError:
            return ({'error': True, 'url': url, 'data': request_data, 'text': response.text, 'status': response.status_code}, request_data)

        return (response_json, request_data)

    def set_correct_password(self, new_password: str, edited_by: User) -> None:
        'Change password, marks as correct, create LeadChange instance.'
        old_value = self.password
        self.password = new_password
        user_email = edited_by.email if edited_by else 'user'
        if self.wrong_password_date:
            self.wrong_password_date = None
            if edited_by and not edited_by.is_superuser:
                self.wrong_password_change_counter = self.wrong_password_change_counter + 1

            self.add_comment(f'Wrong password fixed', edited_by)
            # self.insert_note(f'Wrong password fixed by {user_email}')
            # self.save()
            LeadChange(lead=self.lead, lead_account=self, field=LeadChange.FIELD_WRONG_PASSWORD_FIX, value=new_password, old_value=old_value, edited_by=edited_by).save()
            return

        self.add_comment(f'Password changed', edited_by)
        # self.insert_note(f'Password changed by {user_email}')
        # self.save()
        LeadChange(lead=self.lead, lead_account=self, field=LeadChange.FIELD_PASSWORD, value=new_password, old_value=old_value, edited_by=edited_by).save()

    def mark_wrong_password(self, edited_by: User) -> None:
        old_value = 'True' if self.wrong_password_date else 'False'
        self.wrong_password_date = timezone.now()
        self.add_comment(f'Wrong password reported', edited_by)
        # self.insert_note(f'Wrong password reported by {edited_by.email}')
        # self.save()
        LeadChange(lead=self.lead, lead_account=self, field=LeadChange.FIELD_WRONG_PASSWORD, value='True', old_value=old_value, edited_by=edited_by).save()

    def mark_security_checkpoint(self, edited_by: User) -> None:
        old_value = 'True' if self.security_checkpoint_date else 'False'
        self.security_checkpoint_date = timezone.now()
        self.add_comment(f'Security checkpoint reported', edited_by)
        # self.insert_note(f'Security checkpoint reported by {edited_by.email}')
        # self.save()
        LeadChange(lead=self.lead, lead_account=self, field=LeadChange.FIELD_SECURITY_CHECKPOINT, value='True', old_value=old_value, edited_by=edited_by).save()

    def resolve_security_checkpoint(self, edited_by: User) -> None:
        old_value = 'True' if self.security_checkpoint_date else 'False'
        self.security_checkpoint_date = None
        self.add_comment(f'Security checkpoint reported as resolved', edited_by)
        # self.insert_note(f'Security checkpoint reported as resolved by {edited_by.email}')
        # self.save()
        LeadChange(lead=self.lead, lead_account=self, field=LeadChange.FIELD_SECURITY_CHECKPOINT, value='False', old_value=old_value, edited_by=edited_by).save()

    def generate_payments(self):
        bundler = self.get_bundler()
        payment_datetime = self.in_progress_date or timezone.now()
        result = []
        payment = self.get_bundler_payment(bundler)
        if payment:
            entry, _ = BundlerPayment.objects.get_or_create(
                bundler=bundler,
                lead_account=self,
                payment_type=BundlerPayment.PAYMENT_TYPE_ACCOUNT_MAIN,
                defaults=dict(payment=payment)
            )
            entry.payment = payment
            entry.datetime = payment_datetime
            entry.save()
            result.append(entry)
        parent_payment = self.get_parent_bundler_payment(bundler)
        if parent_payment:
            parent_bundler = bundler.parent_bundler  # pylint: disable=no-member
            entry, _ = BundlerPayment.objects.get_or_create(
                bundler=parent_bundler,
                lead_account=self,
                payment_type=BundlerPayment.PAYMENT_TYPE_ACCOUNT_PARENT,
                defaults=dict(payment=parent_payment)
            )
            entry.payment = parent_payment
            entry.datetime = payment_datetime
            entry.save()
            result.append(entry)

        second_parent_payment = self.get_second_parent_bundler_payment(bundler)
        if second_parent_payment:
            second_parent_bundler = bundler.second_parent_bundler  # pylint: disable=no-member
            entry, _ = BundlerPayment.objects.get_or_create(
                bundler=second_parent_bundler,
                lead_account=self,
                payment_type=BundlerPayment.PAYMENT_TYPE_ACCOUNT_SECOND_PARENT,
                defaults=dict(payment=second_parent_payment)
            )
            entry.payment = second_parent_payment
            entry.datetime = payment_datetime
            entry.save()
            result.append(entry)

        third_parent_payment = self.get_third_parent_bundler_payment(bundler)
        if third_parent_payment:
            third_parent_bundler = bundler.third_parent_bundler  # pylint: disable=no-member
            entry, _ = BundlerPayment.objects.get_or_create(
                bundler=third_parent_bundler,
                lead_account=self,
                payment_type=BundlerPayment.PAYMENT_TYPE_ACCOUNT_THIRD_PARENT,
                defaults=dict(payment=second_parent_payment)
            )
            entry.payment = second_parent_payment
            entry.datetime = payment_datetime
            entry.save()
            result.append(entry)

        chargeback = self.get_bundler_chargeback(bundler)
        if chargeback:
            entry, _ = BundlerPayment.objects.get_or_create(
                bundler=bundler,
                lead_account=self,
                payment_type=BundlerPayment.PAYMENT_TYPE_ACCOUNT_CHARGEBACK,
                defaults=dict(payment=chargeback)
            )
            entry.payment = chargeback
            entry.datetime = self.banned_date
            entry.save()
            result.append(entry)

        return result

    def set_status(self, value: str, edited_by: User) -> bool:
        'Change status, create LeadChange instance.'
        if value not in dict(self.STATUS_CHOICES).keys():
            raise ValueError('Unknown status: {}'.format(value))
        if value == self.status:
            return False

        old_value = self.status

        if value == self.STATUS_QUALIFIED and old_value == self.STATUS_IN_PROGRESS:
            return False

        if self.status != Lead.STATUS_BANNED:
            self.old_status = self.status

        self.status = value

        self.add_comment(f'Status changed from {old_value} to {self.status}', edited_by)
        # self.insert_note(f'Status changed from {old_value} to {self.status} by {edited_by.email if edited_by else edited_by}')

        if self.status in (self.STATUS_IN_PROGRESS, self.STATUS_BANNED):
            self.generate_payments()
            self.add_comment(f'Bundler payments generated', edited_by)
            # self.insert_note(f'Bundler payments generated')

        self.save()
        LeadChange(lead=self.lead, lead_account=self, field=LeadChange.FIELD_STATUS, value=value, old_value=old_value, edited_by=edited_by).save()
        return True

    def ban(self, edited_by: User, reason: typing.Optional[str] = None, note: typing.Optional[str] = None) -> bool:
        'Mark lead account as banned, send cutomer.io event.'
        if self.status == LeadAccount.STATUS_BANNED:
            return False
        now = timezone.localtime(timezone.now())
        self.ban_reason = reason
        self.banned_date = now
        self.ban_note = note

        self.save()

        result = self.set_status(LeadAccount.STATUS_BANNED, edited_by)
        active_accounts = LeadAccount.get_active_lead_accounts(self.lead)

        if self.status == LeadAccount.STATUS_AVAILABLE:
            CustomerIOClient().send_lead_event(self.lead, CustomerIOClient.EVENT_AVAILABLE_BANNED, account_type=self.account_type)
        elif active_accounts:
            active_accounts_str = '{} account{}'.format(
                ' and '.join([i.account_type for i in active_accounts]),
                's' if len(active_accounts) > 1 else '',
            )
            CustomerIOClient().send_lead_event(self.lead, CustomerIOClient.EVENT_BANNED_HAS_ACCOUNTS, account_type=self.account_type, active_accounts=active_accounts_str)
        else:
            pass
            # CustomerIOClient().send_lead_event(self.lead, CustomerIOClient.EVENT_BANNED, account_type=self.account_type)

        # if not active_accounts:
        #     self.lead.ban(edited_by)
        return result

    def unban(self, edited_by: User) -> bool:
        'Restores lead account previous status before banned.'
        self.ban_reason = None
        self.ban_note = None
        self.save()
        result = self.set_status(self.old_status or LeadAccount.STATUS_QUALIFIED, edited_by)
        if result:
            self.lead.unban(edited_by)
        return result

    def disqualify(self, edited_by: User) -> bool:
        'Set lead account status as disqualified.'
        new_status = LeadAccount.STATUS_DISQUALIFIED
        if self.account_type == LeadAccount.ACCOUNT_TYPE_FACEBOOK_SCREENSHOT:
            new_status = LeadAccount.STATUS_SCREENSHOT_DISQUALIFIED
        result = self.set_status(new_status, edited_by)
        if result:
            self.disqualified_date = timezone.now()
            self.add_comment('Disqualified', edited_by)
            # self.insert_note('Disqualified')
            # self.save()
            if not LeadAccount.get_active_lead_accounts(self.lead):
                self.lead.disqualify(edited_by)
        return result

    def qualify(self, edited_by: User) -> bool:
        'Set lead account status as qualified.'
        new_status = LeadAccount.STATUS_QUALIFIED
        result = self.set_status(new_status, edited_by)
        if result:
            self.lead.qualify(edited_by)
            if not self.qualified_date:
                self.qualified_date = timezone.now()
                self.add_comment('Qualified', edited_by)
                # self.insert_note('Qualified')
            self.save()

        return result

    def is_active(self) -> bool:
        'Check if RaspberryPi is assigned and lead account is not banned.'
        return self.status in LeadAccount.STATUSES_ACTIVE and self.lead.raspberry_pi is not None

    def is_banned(self) -> bool:
        'Check if lead account is banned.'
        return self.status == LeadAccount.STATUS_BANNED

    @classmethod
    def get_lead_accounts(cls, lead: Lead) -> models.query.QuerySet:
        return cls.objects.filter(lead=lead, active=True)

    @classmethod
    def get_active_lead_accounts(cls, lead: Lead) -> models.query.QuerySet:
        return cls.objects.filter(lead=lead, active=True, status__in=cls.STATUSES_ACTIVE)

    def touch(self) -> None:
        'Update touch count and last touch date. Tries to sync to adsdb if conditions are met.'
        if self.account_type not in self.ACCOUNT_TYPES_FACEBOOK:
            return

        self.last_touch_date = timezone.now()
        self.touch_count += 1
        self.sync_to_adsdb()
        self.save()

    @classmethod
    def get_online_filter(cls) -> models.query.QuerySet:
        '''
        Get online condition ty use as a filter like

        Lead.objects.filter(Lead.get_online_filter())
        '''
        return cls.get_timedelta_filter('lead__raspberry_pi__last_seen__gt', minutes=-RaspberryPi.online_minutes_ttl)

    def add_comment(self, message, user=None):
        'Add a comment to the model'
        self.comments.create(user=user, text=message)

    def get_comments(self):
        return [f'{ii.created.strftime(settings.SYSTEM_DATETIME_FORMAT)} [{ii}] {ii.text}'
                for ii in self.comments.order_by('created')]

    def insert_note(self, message, event_datetime=None):
        'Add a text message to note field'
        if not event_datetime:
            event_datetime = timezone.localtime(timezone.now())

        line = f'{event_datetime.strftime(settings.SYSTEM_DATETIME_FORMAT)} {message}'

        if not self.note:
            self.note = line
        else:
            self.note = f'{self.note}\n{line}'


class ReportProxyLeadAccount(LeadAccount):
    'A proxy model to register LeadAccount in admin UI twice for Reports'
    class Meta:
        proxy = True
        verbose_name = 'Report LeadAccount'
        verbose_name_plural = 'Report LeadAccounts'


class ReadOnlyLeadAccount(LeadAccount):
    'Read only LeadAccount model'
    class Meta:
        proxy = True
        verbose_name = 'Read-only Lead Account'
        verbose_name_plural = 'Read-only Lead Accounts'
