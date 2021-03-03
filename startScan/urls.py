from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    # path(
    #     'history/',
    #     views.scan_history,
    #     name="scan_history"),
    path('details/<int:id>', views.detail_scan, name='detail_scan'),
    path('history/', views.scan_history, name="scan_hist"),
    path('history/<int:host_id>', views.scan_history, name="scan_history"),
    path('api/', include('startScan.api.urls', 'scan_host_api'))


    # path(
    #     'export/subdomains/<int:scan_id>',
    #     views.export_subdomains,
    #     name='export_subdomains'),
    # path(
    #     'export/endpoints/<int:scan_id>',
    #     views.export_endpoints,
    #     name='export_endpoints'),
    # path(
    #     'export/urls/<int:scan_id>',
    #     views.export_urls,
    #     name='export_http_urls'),
    # path(
    #     'stop/scan/<str:id>',
    #     views.stop_scan,
    #     name='stop_scan'),
    # path(
    #     'target/',
    #     include('targetApp.urls')),
    
]
