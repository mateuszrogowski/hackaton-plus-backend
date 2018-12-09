# -*- coding: utf-8 -*-

import urllib
from urllib.parse import urljoin

import requests
from user_agent import generate_user_agent

from .ticket_utils import GetXMLEtree


class VagonInformation:
    def __init__(self, train_number):
        self.train_number = train_number

        self.headers = {
            'User-Agent': generate_user_agent(),
            'Accept-Language': 'pl-PL,pl;q=0.5'
        }

        self.company = None
        self.cislo_number = None
        self.final_data = None

        self.get_cislo_number()
        self.get_train_detailed_info()

    def get_cislo_number(self):
        """
        Return cislo number and company name.
        """

        params = {
            'jmeno': self.train_number,
            'rok': '2018'
        }

        params = urllib.parse.urlencode(params)

        url = r'https://www.vagonweb.cz/razeni/json_vlaky.php?'

        r = requests.get(
            url=url,
            headers=self.headers,
            params=params
        )

        if r.status_code == 200 and '[]' not in r.text.strip():
            self.company = r.json()[0].get('zeme').strip()
            self.cislo_number = r.json()[0].get('cislo').strip()

    def get_train_detailed_info(self):
        """
        Returns detailed train data info.
        """

        final_data = {
        }

        params = {
            'zeme': self.company,
            'cislo': self.cislo_number,
            'rok': '2019',
            'lang': 'pl',
            'styl': 's'
        }

        params = urllib.parse.urlencode(params)

        url = 'https://www.vagonweb.cz/razeni/vlak.php?'

        r = requests.get(
            url=url,
            params=params,
            headers=self.headers
        )

        if r.status_code == 200:
            g = GetXMLEtree(response_data=r.text)

            train_info_table_xpath = './/tr[@class="bunka_vozu"]'

            train_info_table_data = list(set([x for x in g.xml_etree.xpath(train_info_table_xpath)]))

            final_data['cars'] = {}

            for index, row in enumerate(train_info_table_data):
                current_key = 'key_{}'.format(index+1)
                vagon_data = {}

                for value in row:
                    if value.xpath('@id')[0].startswith('trida1_'):
                        vagon_data['number'] = ''.join(value.xpath('.//span/text()'))

                    elif value.xpath('@id')[0].startswith('trida1a_'):
                        partial_url = value.xpath('.//img/@src')[0].split('..')[1].strip()

                        full_url = urljoin('https://www.vagonweb.cz', partial_url)

                        vagon_data['vagon_img'] = full_url

                    elif value.xpath('@id')[0].startswith('trida1b_'):
                        continue

                    elif value.xpath('@id')[0].startswith('trida2_'):
                        icons = value.xpath('.//span[@class="tab-pocmist"]')

                        for item in icons:
                            vagon_data['titles_imgs_urls'] = list(
                                        zip(item.xpath('.//img/@src'), item.xpath('.//img/@title')))

                    elif value.xpath('@id')[0].startswith('trida2a_'):
                        continue

                    elif value.xpath('@id')[0].startswith('trida2b_'):
                        continue

                    elif value.xpath('@id')[0].startswith('trida2c_'):
                        continue

                if vagon_data.get('number'):
                    final_data['cars'][current_key] = vagon_data
                else:
                    final_data['train_info'] = vagon_data

            vagon_mapping = {int(val['number']): key for key, val in final_data['cars'].items()}
            final_data['car_mapping'] = vagon_mapping

        self.final_data = final_data
