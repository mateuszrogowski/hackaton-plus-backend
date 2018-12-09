# from PIL import Image

from django.core.files.uploadedfile import InMemoryUploadedFile
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets  # , permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from apps.ticket import ticket_utils
from apps.ticket.models import Ticket
from apps.ticket.serializers import TicketFileUploadSerializer, TicketModelSerializer, TicketListSerializer

CONTACT_PHONES = {"PKP Intercity (Grupa PKP)": "703 200 200", "PKP TLK": "703 200 200", "PKP IC": "703 200 200",
                  "PKP Szybka Kolej Miejska w Trójmieście (Grupa PKP)": "(58) 721 21 70",
                  "Przewozy Regionalne": "703 20 20 20", "Koleje Mazowieckie": "(22) 364 44 44",
                  "Koleje Dolnośląskie": "(76) 753 52 05", "Koleje Wielkopolskie": "(61) 279 27 78",
                  "Koleje Śląskie": "(32) 428 88 88", "Arriva": "801 081 515", "Szybka Kolej Miejska": "801 044 484",
                  "Warszawska Kolej Dojazdowa": "(22) 758 00 12", "Łódzka Kolej Aglomeracyjna": "(42) 205 55 15",
                  "Koleje Małopolskie": "703 20 20 25"}


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
                'error_message': "Format of submitted file is invalid. Accepted file formats are jpg, jpeg, gif and png"
            },
            status=status.HTTP_400_BAD_REQUEST
        )
        image_formats = ['application/pdf'] #, 'image/jpeg', 'image/gif', 'image/png']

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

            data_from_ticket['qr_code'] = base64_encoded_qr_code_str
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
