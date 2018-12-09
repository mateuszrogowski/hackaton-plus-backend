# -*- coding: utf-8 -*-

import requests
from dateutil.parser import parse
from django.urls import reverse
from icalendar import Calendar, Event
from user_agent import generate_user_agent


class GoogleCalendarICS:
    def __init__(self, ticket_id):
        self.ticket_id = ticket_id

    def generate_ics(self):
        """
        Generates ICS file for train ticket object based on given ID.
        """

        with requests.Session() as s:
            s.headers.update(**{
                'User-Agent': generate_user_agent()
            })

            url = reverse('ticket-detail', kwargs={'pk': self.ticket_id})

            response = s.get(url).json()

            purchase_date = response.get('purchase_date')

            train_start = response.get('start_time')
            train_end = response.get('finish_time')

            start_place = response.get('start_place')
            finish_place = response.get('finish_place')

            vagon_number = response.get('car_number')
            train_number = response.get('train_number')
            passenger_seats = response.get('seats')
            distance = response.get('total_length')

            cal = Calendar()
            event = Event()

            general_summary = '[{train_number}] {start_place} - {finish_place} [{distance} km]'.format(
                train_number=train_number,
                start_place=start_place,
                finish_place=finish_place,
                distance=distance
            )

            additional_info = 'Numer wagonu: {vagon_number}, miejsce: {passenger_seats}, relacja: {start_place} - {finish_place}'.format(
                vagon_number=vagon_number,
                passenger_seats=''.join(passenger_seats),
                start_place=start_place,
                finish_place=finish_place
            )

            event.add('summary', general_summary)
            event.add('dtstart', parse(train_start))
            event.add('dtend', parse(train_end))
            event.add('dtstamp', parse(purchase_date))
            event.add('priority', 5)
            event.add('description', additional_info)
            #             event.add('location', location)
            #             event.add('url', location)

            cal.add_component(event)

            return cal