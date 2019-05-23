from django.views import View
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from adsrental.forms import UserLoginForm
from adsrental.models.lead import Lead
from adsrental.models.user import User


class UserLoginView(View):
    def get(self, request):
        form = UserLoginForm()
        return render(request, 'user/login.html', dict(
            form=form,
        ))

    def post(self, request):
        form = UserLoginForm(request.POST)
        if not form.is_valid():
            return render(request, 'user/login.html', dict(
                form=form,
            ))

        lead = form.get_lead(form.cleaned_data)

        request.session['leadid'] = lead.leadid
        return redirect('user_stats')


class UserStatsView(View):
    def get(self, request):
        leadid = request.session.get('leadid')
        lead = Lead.objects.filter(leadid=leadid).first()
        if not lead:
            return redirect('user_login')

        return render(request, 'user/stats.html', dict(
            lead=lead,
        ))


class UserSecretKeyView(View):
    def get(self, request):
        email = request.GET.get('email')
        lead = Lead.objects.filter(email=email).first()

        if not lead:
            res = { 'success': False, 'msg': 'Such user does not exist' }
            return JsonResponse(res, safe=False)

        secret_key = User.objects.make_random_password()
        lead.secret_key = make_password(secret_key)
        lead.save()

        subject = 'ADS INC Secret Key'
        html_content = render_to_string('email/base.html', {})
        text_content = strip_tags(html_content)

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, email.split(','))
        msg.attach_alternative(html_content, 'text/html')
        # msg.send()

        res = { 'success': True, 'msg': 'Secret key sent to your email' }
        return JsonResponse(res, safe=False)
