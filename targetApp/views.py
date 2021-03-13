import validators
import csv
import io
import os
from django.shortcuts import render, get_object_or_404, redirect
from django import http
from .models import Domain
from startScan.models import ScanHistory
from django.contrib import messages
from targetApp.forms import AddTargetForm
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
import sweetify


def index(request):
    # TODO bring default target page
    return render(request, 'target/index.html')



def add_target_form(request):
    form = AddTargetForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            Domain.objects.create(
                **form.cleaned_data,
                insert_date=timezone.now())
            messages.success(request,'Target domain ' + form.cleaned_data['domain_name'] + ' added successfully')
            return redirect('list_target')
    context = {
        # "add_target_li": "active",
        # "target_data_active": "true",
        'form': form,
        'title' : 'Add-Target'
        }

    return render(request, 'targetApp/add.html', context)


def list_target(request):
    domains = Domain.objects.all().order_by('-insert_date')
    context = {
        # 'list_target_li': 'active',
        'target_data_active': 'true',
        'domains': domains,
        'title' : 'List Target'
        }
    return render(request, 'targetApp/list.html', context)



def delete_target(request, id):
    obj = get_object_or_404(Domain, id=id)
    domain_name=obj.domain_name
    os.system('rm -rf ' + settings.TOOL_LOCATION + 'scan_results/' + obj.domain_name + '*')
    obj.delete()
    responseData = {'status': 'true'}
    messages.add_message(
        request,
        messages.INFO,
        f'{domain_name} successfully deleted from the target list.')

    return redirect('list_target')



