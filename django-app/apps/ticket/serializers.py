from rest_framework import serializers

from apps.ticket.models import Ticket
from apps.ticket.ticket_utils import ACCESIBILITY_DICT

CONTACT_PHONES = {"PKP Intercity (Grupa PKP)": "703 200 200", "PKP TLK": "703 200 200", "PKP IC": "703 200 200",
                  "PKP Szybka Kolej Miejska w Trójmieście (Grupa PKP)": "(58) 721 21 70",
                  "Przewozy Regionalne": "703 20 20 20", "Koleje Mazowieckie": "(22) 364 44 44",
                  "Koleje Dolnośląskie": "(76) 753 52 05", "Koleje Wielkopolskie": "(61) 279 27 78",
                  "Koleje Śląskie": "(32) 428 88 88", "Arriva": "801 081 515", "Szybka Kolej Miejska": "801 044 484",
                  "Warszawska Kolej Dojazdowa": "(22) 758 00 12", "Łódzka Kolej Aglomeracyjna": "(42) 205 55 15",
                  "Koleje Małopolskie": "703 20 20 25"}


class ConnectionInfoSerializer(serializers.Serializer):
    status = serializers.CharField()
    late = serializers.CharField()
    late_reason = serializers.CharField()


class TicketFileUploadSerializer(serializers.Serializer):
    ticket = serializers.FileField()


class TicketModelSerializer(serializers.ModelSerializer):
    carrier_contact_phone = serializers.SerializerMethodField()
    start_place_accessibility = serializers.SerializerMethodField()
    finish_place_accessibility = serializers.SerializerMethodField()

    connection_current_info = ConnectionInfoSerializer()

    car_info = serializers.JSONField()

    def get_carrier_contact_phone(self, obj: Ticket):
        carrier = obj.carrier

        return CONTACT_PHONES[carrier]

    def _get_place_accessibility(self, name):
        acc = ACCESIBILITY_DICT[name]
        return acc

    def get_start_place_accessibility(self, obj: Ticket):
        return self._get_place_accessibility(obj.start_place)

    def get_finish_place_accessibility(self, obj: Ticket):
        return self._get_place_accessibility(obj.finish_place)

    class Meta:
        model = Ticket
        fields = '__all__'


class TicketListSerializer(serializers.ListSerializer):
    child = TicketModelSerializer()

