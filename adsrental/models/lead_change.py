from __future__ import unicode_literals

from django.db import models


class LeadChange(models.Model):
    '''
    Stores a single change for :model:`adsrental.Lead`, like status.
    '''
    lead = models.ForeignKey('adsrental.Lead', on_delete=models.CASCADE)
    field = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    old_value = models.CharField(max_length=255, null=True, blank=True)
    # data = models.TextField(null=True, blank=True)
    edited_by = models.ForeignKey('adsrental.User', null=True, blank=True, on_delete=models.SET_NULL)
    created = models.DateTimeField(auto_now_add=True)
