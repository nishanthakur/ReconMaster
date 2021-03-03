from rest_framework import serializers
from startScan.models import ScanHistory, ScannedHost, WayBackEndPoint

class ScanHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScannedHost
        fields = '__all__'

class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        model = WayBackEndPoint
        fields = '__all__'	