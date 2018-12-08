# from PIL import Image
from django.conf import settings

from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import permissions
from rest_framework import status, viewsets  # , permissions
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.ticket import ticket_utils
from apps.ticket.models import Ticket
from apps.ticket.serializers import TicketFileUploadSerializer, TicketModelSerializer, TicketListSerializer


class TicketViewSet(viewsets.GenericViewSet):
    """
    Endpoint for getting result's names from uploaded images.
    """
    # http_method_names = ["POST"]
    parser_classes = (MultiPartParser, FormParser)
    # permission_classes = (permissions.IsAuthenticated,)
    serializer_class_post = TicketFileUploadSerializer
    serializer_class_get = TicketModelSerializer
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

    def create(self, request, *args, **kwargs):

        serializer = self.serializer_class_post(data=request.data)
        if serializer.is_valid() and 'multipart/form-data' in request.content_type:

            err = self._check_file_type(serializer.validated_data['ticket'])
            if err:
                return err

            ticket_file = serializer.validated_data['ticket']

            # process file
            data_from_ticket = ticket_utils.process_ticket(ticket_file)

            ticket = Ticket(**data_from_ticket)
            ticket.save()

            # response_data = {
            #     'id': 0,
            # }
            # response_data.update(data_from_ticket)
            return Response(self.serializer_class_get(ticket).data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        serializer = self.serializer_class_get
        print("Retrieve", pk)
        ticket = get_object_or_404(Ticket, id=pk)

        return Response(serializer(ticket).data, status=status.HTTP_200_OK)

    def list(self, request):
        serializer = self.serializer_class_list

        tickets = Ticket.objects.all().order_by('-start_time')

        return Response(serializer(tickets).data, status=status.HTTP_200_OK)
