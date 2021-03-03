import os
import traceback
import json
import validators

from celery import shared_task
from reconMaster.celery import app
from startScan.models import ScanHistory, ScannedHost, ScanActivity, WayBackEndPoint
from targetApp.models import Domain
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import datetime


@app.task
def doScan(domain_id, scan_history_id):
    current_scan_time = timezone.now()
    domain = Domain.objects.get(pk=domain_id)
    task = ScanHistory()

    # Saving the last scan date.
    domain.last_scan_date = current_scan_time
    domain.save()

    # Saving the task status.
    task.domain_name = domain
    task.scan_status = 1
    task.last_scan_date = current_scan_time
    task.save()

    activity_id = create_scan_activity(task, "Scanning Started", 2)
    results_dir = settings.TOOL_LOCATION + 'scan_results/'
    os.chdir(results_dir)

    try:
        current_scan_dir = domain.domain_name + '_' + \
            str(datetime.strftime(timezone.now(), '%Y_%m_%d_%H_%M_%S'))
        os.mkdir(current_scan_dir)
    except Exception as exception:
        print('-'*30)
        print(exception)
        print('-'*30)
        # do something here
        scan_failed(task)

    activity_id = create_scan_activity(task, "Subdomain Scanning", 1)

    # Tools associated with subdomain discovery.
    tool1 = 'assetfinder'
    tool2 = 'subfinder'

    threads = 10

    # Code that performs subdomain discovery.
    os.system(settings.TOOL_LOCATION + 'get_subdomain.sh %s %s %s %s %s' %
              (threads, domain.domain_name, current_scan_dir, tool1, tool2))

    # Directory to store all the gathered
    subdomain_scan_results_file = results_dir + \
        current_scan_dir + '/sorted_subdomain_collection.txt'

    with open(subdomain_scan_results_file) as subdomain_list:
        for subdomain in subdomain_list:
            '''
            subfinder sometimes produces  long subdomain
            output which is likely to crash the scan, so validate
            subdomains before saving
            '''
            if validators.domain(subdomain.rstrip('\n')):
                scanned = ScannedHost()
                scanned.subdomain = subdomain.rstrip('\n')
                scanned.scan_history = task
                scanned.save()

    # Updating scan activity.
    update_last_activity(activity_id, 2)

    # Begining of the Port Scanning section
    activity_id = create_scan_activity(task, "Port Scanning", 1)
    port_results_file = results_dir + current_scan_dir + '/ports.json'
    nabbu_command = f"cat {subdomain_scan_results_file} | naabu -top-ports 100 -json -o {port_results_file}"
    os.system(nabbu_command)

    # writing port results
    try:
        with open(port_results_file, 'r') as port_json_result:
            lines = port_json_result.readlines()
            for line in lines:
                try:
                    each_line = json.loads(line.strip())
                except Exception as error:
                    print('-'*30)
                    print(error)
                    print('-'*30)
                    each_line = "{'host':'', 'port':''}"
                sub_domain = ScannedHost.objects.get(
                    scan_history=task, subdomain=each_line['host'])
                if sub_domain.open_ports:
                    sub_domain.open_ports = sub_domain.open_ports + \
                        ', ' + str(each_line['port'])
                else:
                    sub_domain.open_ports = str(each_line['port'])
                sub_domain.save()
    except BaseException as exception:
        print('-'*30)
        print(exception)
        print('-'*30)
        update_last_activity(activity_id, 0)

    update_last_activity(activity_id, 2)

    # Begining of HTTP Crawler and screenshot section.
    activity_id = create_scan_activity(task, "HTTP Crawler", 1)
    httpx_results_file = results_dir + current_scan_dir + '/httpx.json'
    httpx_command = f'cat {subdomain_scan_results_file} | httpx -json -cdn -o {httpx_results_file}'
    os.system(httpx_command)

    # alive subdomains from httpx.
    alive_file_location = results_dir + current_scan_dir + '/alive.txt'

    with open(alive_file_location, 'w') as alive_file:
        # writing httpx results
        with open(httpx_results_file, 'r') as httpx_json_result:
            lines = httpx_json_result.readlines()

            for line in lines:
                each_line = json.loads(line.strip())
                try:
                    sub_domain = ScannedHost.objects.get(
                        scan_history=task, subdomain=each_line['url'].split("//")[-1])
                    sub_domain.http_url = each_line['url']
                    sub_domain.http_status = each_line['status-code']
                    sub_domain.page_title = each_line['title']
                    sub_domain.content_length = each_line['content-length']
                    sub_domain.ip_address = each_line['ip']
                    if 'cdn' in each_line:
                        sub_domain.is_ip_cdn = each_line['cdn']
                    if 'cnames' in each_line:
                        cname_list = ', '.join(each_line['cnames'])
                        sub_domain.cname = cname_list
                    sub_domain.save()
                    alive_file.write(each_line['url'] + '\n')
                except Exception as error:
                    print('-'*30)
                    print(error)
                    print('-'*30)

    update_last_activity(activity_id, 2)

    # Running aquatone for visual identification.
    activity_id = create_scan_activity(task, "Running Aquatone", 1)
    with_protocol_path = results_dir + current_scan_dir + '/alive.txt'
    output_aquatone_path = results_dir + current_scan_dir + '/aquascreenshots'
    scan_port = 'xlarge'
    aquatone_dir = settings.TOOL_LOCATION + 'aquatone'
    threads = 10

    aquatone_command = 'cat {} | aquatone --threads {} -ports {} -out {}'.format(
        with_protocol_path, threads, scan_port, output_aquatone_path)
    os.system(aquatone_command)
    all_results_dir = settings.TOOL_LOCATION + 'scan_results/*'
    os.system(f'chmod -R 607 {all_results_dir}')
    aqua_json_path = output_aquatone_path + '/aquatone_session.json'

    try:
        with open(aqua_json_path, 'r') as json_file:
            data = json.load(json_file)
            for host in data['pages']:
                sub_domain = ScannedHost.objects.get(
                    scan_history__id=task.id,
                    subdomain=data['pages'][host]['hostname'])
                sub_domain.screenshot_path = current_scan_dir + \
                    '/aquascreenshots/' + data['pages'][host]['screenshotPath']
                sub_domain.http_header_path = current_scan_dir + \
                    '/aquascreenshots/' + data['pages'][host]['headersPath']
                tech_list = []
                if data['pages'][host]['tags'] is not None:
                    for tag in data['pages'][host]['tags']:
                        tech_list.append(tag['text'])
                tech_string = ','.join(tech_list)
                sub_domain.technology_stack = tech_string
                sub_domain.save()
    except Exception as exception:
        print('-'*30)
        print(exception)
        print('-'*30)
        update_last_activity(activity_id, 0)

    update_last_activity(activity_id, 2)

    # Now checking if subdomain takeover is possible or not.
    threads = 10
    subdomain_takeover_command = settings.TOOL_LOCATION + 'takeover.sh {} {}'.format(current_scan_dir, threads)
    os.system(subdomain_takeover_command)
    takeover_results_file = results_dir + current_scan_dir + '/takeover_result.json'

    try:
        with open(takeover_results_file) as f:
            takeover_data = json.load(f)

        for data in takeover_data:
            if data['vulnerable']:
                get_subdomain = ScannedHost.objects.get(
                    scan_history=task, subdomain=data['subdomain'])
                get_subdomain.takeover = "vulnerable"
                get_subdomain.save()
            else:
                get_subdomain = ScannedHost.objects.get(
                    scan_history=task, subdomain=data['subdomain'])
                get_subdomain.takeover = "not vulnerable"
                get_subdomain.save()
    except Exception as error:
        print('-'*30)
        print(error)
        print('-'*30)

    # Begining of the directory search section

    # alive_subdomains = ScannedHost.objects.filter(scan_history__id=task.id).exclude(http_url='')
    # dirs_results = current_scan_dir + '/dirs.json'
    # extensions = 'php,asp,aspx,txt,conf,db,sql,json'
    # threads = 100
    # wordlist_location = settings.TOOL_LOCATION + 'dirsearch/db/dicc.txt'

    # for subdomain in alive_subdomains:
    #     dirsearch_command = settings.TOOL_LOCATION + 'get_dirs.sh {} {} {} {} {}'.format(subdomain.http_url, wordlist_location, dirs_results, extensions, threads)
    #     os.system(dirsearch_command)
    #     try:
    #         with open(dirs_results, 'r') as json_file:
    #             json_string = json_file.read()
    #             scanned_host = ScannedHost.objects.get(scan_history__id=task.id, http_url=subdomain.http_url)
    #             scanned_host.directory_json = json_string
    #             scanned_host.save()
    #     except Exception as exception:
    #         print('-'*30)
    #         print(exception)
    #         print('-'*30)

    # Begining of the endpoint gathering section.
    activity_id = create_scan_activity(task, "Gathering Endpoints", 1)
    endpoint_results_file = results_dir + current_scan_dir + '/all_urls.json'
    tool3 = 'gau'
    tool4 = 'hakrawler'
    os.system(settings.TOOL_LOCATION + 'get_urls.sh {} {} {} {}'.format(
        domain.domain_name, current_scan_dir, tool3, tool4))

    with open(endpoint_results_file, 'r') as urls_json_result:
        lines = urls_json_result.readlines()
        for line in lines:
            each_line = json.loads(line.strip())
            endpoint = WayBackEndPoint()
            endpoint.url_of = task
            endpoint.http_url = each_line['url']
            endpoint.content_length = each_line['content-length']
            endpoint.http_status = each_line['status-code']
            endpoint.page_title = each_line['title']
            if 'content-type' in each_line:
                endpoint.content_type = each_line['content-type']
            endpoint.save()

    # Now the scan is completed, we need to save the task.
    task.scan_status = 2
    task.save()


# This function creates an ScanActivity object so that we can keep track of completed task.
def create_scan_activity(task, message, status):
    scan_activity = ScanActivity()
    scan_activity.scan_of = task
    scan_activity.title = message
    scan_activity.time = timezone.now()
    scan_activity.status = status
    scan_activity.save()
    return scan_activity.id


# This function helps us for updating the scan status.
def update_last_activity(id, activity_status):
    ScanActivity.objects.filter(id=id).update(
        status=activity_status, time=timezone.now())


# This function helps to terminate the scanning process if anything goes wrong.
def scan_failed(task):
    task.scan_status = 0
    task.save()


