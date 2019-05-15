import decimal
import datetime
from dateutil import parser

from django.views import View
from django.utils import timezone
from django.shortcuts import Http404, render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Count

from adsrental.models.lead_account import LeadAccount
from adsrental.models.bundler_payment import BundlerPayment


class AdminBundlerDailyBonusesView(View):
    @staticmethod
    def get_bonus(lead_accounts_count):
        for count, bonus in BundlerPayment.BONUSES:
            if lead_accounts_count >= count:
                return bonus

        return decimal.Decimal('0.00')

    @method_decorator(login_required)
    def get(self, request):
        if not request.user.is_superuser:
            raise Http404

        now = timezone.localtime(timezone.now())
        date_str = request.GET.get('date')
        if date_str:
            date = parser.parse(date_str).replace(tzinfo=timezone.get_current_timezone())
        else:
            date = now

        start_date = date.replace(hour=0, minute=0, second=0)
        end_date = start_date + datetime.timedelta(days=1)

        dates_list = []
        for i in range(-1, 2):
            if start_date + datetime.timedelta(days=i) < now:
                dates_list.append(dict(
                    start_date=start_date + datetime.timedelta(days=i),
                    end_date=end_date + datetime.timedelta(days=i) - datetime.timedelta(days=1),
                ))

        bundler_stats = LeadAccount.objects.filter(
            account_type__in=LeadAccount.ACCOUNT_TYPES_FACEBOOK,
            lead__bundler__isnull=False,
            primary=True,
            qualified_date__gt=start_date,
            qualified_date__lt=end_date,
        ).values(
            'lead__bundler_id',
            'lead__bundler__bonus_receiver_bundler_id',
            'lead__bundler__bonus_receiver_bundler__name',
            'lead__bundler__name',
        ).annotate(lead_accounts_count=Count('id')).order_by('-lead_accounts_count')
        # bundler_stats.sort(key=lambda x:x['lead_accounts_count'], reverse=True)

        final_bundler_stats = {}

        for bundler_stat in bundler_stats:
            bundler_id = bundler_stat['lead__bundler_id']
            bundler_name = bundler_stat['lead__bundler__name']
            bonus_lead_accounts = False
            if bundler_stat['lead__bundler__bonus_receiver_bundler_id']:
                bundler_id = bundler_stat['lead__bundler__bonus_receiver_bundler_id']
                bundler_name = bundler_stat['lead__bundler__bonus_receiver_bundler__name']
                bonus_lead_accounts = True

            if bundler_id not in final_bundler_stats:
                final_bundler_stats[bundler_id] = {
                    'bundler_id': bundler_id,
                    'bundler_name': bundler_name,
                    'lead_accounts_count': 0,
                    'bonus_lead_accounts_count': 0,
                    'own_lead_accounts_count': 0,
                    'bonus': decimal.Decimal('0.00'),
                }

            final_bundler_stats[bundler_id]['lead_accounts_count'] += bundler_stat['lead_accounts_count']
            if bonus_lead_accounts:
                final_bundler_stats[bundler_id]['bonus_lead_accounts_count'] += bundler_stat['lead_accounts_count']
            else:
                final_bundler_stats[bundler_id]['own_lead_accounts_count'] += bundler_stat['lead_accounts_count']

        final_bundler_stats = list(final_bundler_stats.values())
        final_bundler_stats.sort(key=lambda x: x['lead_accounts_count'], reverse=True)

        total_accounts = 0
        total_bonus = decimal.Decimal(0.00)
        for bundler_stat in final_bundler_stats:
            bundler_stat['bonus'] = self.get_bonus(bundler_stat['lead_accounts_count'])
            total_accounts += bundler_stat['lead_accounts_count']
            total_bonus += bundler_stat['bonus']

        return render(request, 'admin/bundler_daily_bonuses.html', dict(
            bundler_stats=bundler_stats,
            final_bundler_stats=final_bundler_stats,
            total_accounts=total_accounts,
            total_bonus=total_bonus,
            start_date=start_date,
            end_date=end_date - datetime.timedelta(days=1),
            dates_list=dates_list,
        ))
