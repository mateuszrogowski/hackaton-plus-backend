from rest_framework import serializers


class TicketFileUploadSerializer(serializers.Serializer):
    ticket = serializers.FileField()
