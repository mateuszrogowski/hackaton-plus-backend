# from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets  # , permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from datetime import datetime

from apps.ticket import ticket_utils
from apps.ticket.models import Ticket
from apps.ticket.serializers import TicketFileUploadSerializer, TicketModelSerializer, TicketListSerializer
from apps.ticket.vagon_train_data import VagonInformation
from .calendar_ics import GoogleCalendarICS

open_hours = {
    'W-wa Zach.': [],
    'W-wa Wsch.': ["04:00", "17:00"],
    'Kraków Gł.': ["02:00", "23:00"],
    'Elbląg': ["04:00", "17:00"],
    'Warszawa C.': [],
    'Mońki': ["06:00", "17:00"],
    'Białystok': ["04:00", "17:00"],
    'Warszawa Wsch.': ["04:00", "17:00"]
}

def generate_ics(request, ticket_id):
    """
    Generates ICS file for Google Calendar.
    """

    ics = GoogleCalendarICS(ticket_id=ticket_id)

    ics_data = ics.generate_ics(request=request)

    ticket_filename = 'ticket_{ticket_id}.ics'.format(ticket_id=ticket_id)

    response = HttpResponse(
        content=ics_data.to_ical(),
        content_type='text/calendar'
    )

    response['Content-Disposition'] = 'attachment; filename={}'.format(ticket_filename)

    return response


class TicketViewSet(viewsets.GenericViewSet):
    """
    Endpoint for getting result's names from uploaded images.
    """
    # http_method_names = ["POST"]
    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = (permissions.IsAuthenticated,)
    serializer_class = TicketModelSerializer
    serializer_class_post = TicketFileUploadSerializer
    serializer_class_list = TicketListSerializer

    def _check_file_type(self, file: InMemoryUploadedFile):
        r = Response(
            {
                'exception': "InvalidFileFormat",
                'error_message': "Format wysłanego pliku nie jest wspierany. Wyślij plik PDF"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        image_formats = ['application/pdf']

        if file.content_type in image_formats:
            return None

        else:
            return r

    def get_queryset(self):
        return Ticket.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class_post(data=request.data)
        if serializer.is_valid() and 'multipart/form-data' in request.content_type:

            err = self._check_file_type(serializer.validated_data['ticket'])
            if err:
                return err

            ticket_file = serializer.validated_data['ticket']

            # process file
            data_from_ticket = ticket_utils.process_ticket(ticket_file)

            try:
                qr_code = ticket_utils.extract_qr_code(ticket_file)
                base64_encoded_qr_code_str = ticket_utils.pil_image_to_base64(qr_code)
            except ValueError:
                base64_encoded_qr_code_str = None

            car_info = VagonInformation(train_number=data_from_ticket['train_number'])
            data_from_ticket['car_info'] = car_info.final_data

            data_from_ticket['qr_code'] = base64_encoded_qr_code_str

            closed_station_at_arrival = data_from_ticket["finish_time"].time() > datetime.strptime("23:00", "%H:%M").time()
            # arrival_station_open_hours = open_hours[data_from_ticket["finish_place"]]
            # if not arrival_station_open_hours:
            #     open_end = datetime.strptime(arrival_station_open_hours[1], "%H:%M")
            #     closed_station_at_arrival = open_end.time() < data_from_ticket["finish_time"].time()
            data_from_ticket['closed_station_at_arrival'] = closed_station_at_arrival

            ticket = Ticket(**data_from_ticket)
            ticket.save()

            return Response(self.serializer_class(ticket).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        serializer = self.serializer_class
        print("Retrieve", pk)
        ticket = get_object_or_404(Ticket, id=pk)

        return Response(serializer(ticket).data, status=status.HTTP_200_OK)

    def list(self, request):
        serializer = self.serializer_class_list

        tickets = self.get_queryset().order_by('-start_time')

        return Response(serializer(tickets).data, status=status.HTTP_200_OK)
