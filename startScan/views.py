from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect, HttpResponse
from django.urls import reverse
from startScan.models import ScanHistory, ScannedHost, ScanActivity, WayBackEndPoint
from targetApp.models import Domain
from django.utils import timezone
from django.conf import settings
from datetime import datetime
from reconMaster.tasks import doScan
import os
import requests


# Create your views here.

def scan_history(request, host_id=None):
    if host_id:
        domain = get_object_or_404(Domain, id=host_id)
        scan_history_id = create_scan_object(host_id)
        celery_task = doScan.apply_async(args=(host_id, scan_history_id))
        ScanHistory.objects.filter(id=scan_history_id).update(celery_id=celery_task.id)
    host = ScanHistory.objects.all().order_by('-last_scan_date')
    context = {
        'scan_history_active': 'true', 
        'scan_history': host,
        'title':'History'
        }
    return render(request, 'startScan/history.html', context)


def detail_scan(request, id=None):
    if id:
        subdomains = ScannedHost.objects.filter(scan_history__id=id).exclude(http_status__exact=0)
        context = {
            'subdomains': subdomains,
            'title': 'Detail Scan'
            }
    else:
        context = {}
    return render(request, 'startScan/detail_scan.html', context)

# def detail_scan(request, id=None):
#     subdomain_count = ScannedHost.objects.filter(scan_history__id=id).count()
#     alive_count = ScannedHost.objects.filter(scan_history__id=id).exclude(http_status__exact=0).count()
#     scan_activity = ScanActivity.objects.filter(scan_of__id=id).order_by('time')
#     endpoint_count = WayBackEndPoint.objects.filter(url_of__id=id).count()
#     endpoint_alive_count = WayBackEndPoint.objects.filter(url_of__id=id, http_status__exact=200).count()
#     history = get_object_or_404(ScanHistory, id=id)
#     context = {
#         'scan_history_active': 'true',
#         'scan_activity': scan_activity,
#         'alive_count': alive_count,
#         'scan_history_id': id,
#         'subdomain_count': subdomain_count,
#         'endpoint_count': endpoint_count,
#         'endpoint_alive_count': endpoint_alive_count,
#         'history': history 
#     }

#     return render(request, 'startScan/detail_scan.html', context)



def start_scan_ui(request, host_id):
    domain = get_object_or_404(Domain, id=host_id)
    scan_history_id = create_scan_object(host_id)
    # start the celery task
    celery_task = doScan.apply_async(
        args=(host_id, scan_history_id))
    ScanHistory.objects.filter(
        id=scan_history_id).update(
        celery_id=celery_task.id)
    messages.add_message(
        request,
        messages.INFO,
        'Scan Started for ' +
        domain.domain_name)
    return HttpResponseRedirect(reverse('scan_history'))





# def export_subdomains(request, scan_id):
#     subdomain_list = ScannedHost.objects.filter(scan_history__id=scan_id)
#     domain_results = ScanHistory.objects.get(id=scan_id)
#     response_body = ""
#     for subdomain in subdomain_list:
#         response_body = response_body + subdomain.subdomain + "\n"
#     response = HttpResponse(response_body, content_type='text/plain')
#     response['Content-Disposition'] = 'attachment; filename="subdomains_' + \
#         domain_results.domain_name.domain_name + '_' + \
#         str(domain_results.last_scan_date.date()) + '.txt"'
#     return response


# def export_endpoints(request, scan_id):
#     endpoint_list = WayBackEndPoint.objects.filter(url_of__id=scan_id)
#     domain_results = ScanHistory.objects.get(id=scan_id)
#     response_body = ""
#     for endpoint in endpoint_list:
#         response_body = response_body + endpoint.http_url + "\n"
#     response = HttpResponse(response_body, content_type='text/plain')
#     response['Content-Disposition'] = 'attachment; filename="endpoints_' + \
#         domain_results.domain_name.domain_name + '_' + \
#         str(domain_results.last_scan_date.date()) + '.txt"'
#     return response


# def export_urls(request, scan_id):
#     urls_list = ScannedHost.objects.filter(scan_history__id=scan_id)
#     domain_results = ScanHistory.objects.get(id=scan_id)
#     response_body = ""
#     for url in urls_list:
#         if url.http_url:
#             response_body = response_body + url.http_url + "\n"
#     response = HttpResponse(response_body, content_type='text/plain')
#     response['Content-Disposition'] = 'attachment; filename="urls_' + \
#         domain_results.domain_name.domain_name + '_' + \
#         str(domain_results.last_scan_date.date()) + '.txt"'
#     return response


def create_scan_object(host_id):
    '''
    create task with pending status so that celery task will execute when
    threads are free
    '''
    # get current time
    current_scan_time = timezone.now()
    domain = Domain.objects.get(pk=host_id)
    task = ScanHistory()
    task.scan_status = -1
    task.domain_name = domain
    task.last_scan_date = current_scan_time
    task.save()
    # save last scan date for domain model
    domain.last_scan_date = current_scan_time
    domain.save()
    return task.id