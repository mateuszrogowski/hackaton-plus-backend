from rest_framework import serializers

from apps.ticket.models import Ticket


class TicketFileUploadSerializer(serializers.Serializer):
    ticket = serializers.FileField()


class TicketModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = '__all__'


class TicketListSerializer(serializers.ListSerializer):
    child = TicketModelSerializer()
