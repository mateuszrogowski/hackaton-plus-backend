# -*- coding: utf-8 -*-

import itertools
import urllib
from urllib.parse import urljoin

import lxml.html as html
import requests
from lxml import etree
from lxml.etree import XMLSyntaxError, ParserError
from user_agent import generate_user_agent


class GetXMLEtree:
    def __init__(self, response_data):
        self.response_data = response_data
        self.xml_etree = self.get_xml_tree_object()

    def get_xml_tree_object(self):
        """
        General method to parse a request's response content and return xml tree object.
        """

        try:
            return html.fromstring(self.response_data)
        except ParserError:
            pass
        except XMLSyntaxError:
            return html.fromstring(
                self.response_data,
                parser=etree.XMLParser(
                    encoding='utf-8',
                    recover=True
                )
            )


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
                current_key = 'key_{}'.format(index + 1)
                vagon_data = {}

                for value in row:
                    if value.xpath('@id')[0].startswith('trida1_'):
                        vagon_data['number'] = ''.join(value.xpath('.//span/text()'))

                    elif value.xpath('@id')[0].startswith('trida1a_'):
                        continue

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

                    elif value.xpath('@id')[0].startswith('trida2d_'):
                        partial_urls = [x.xpath('@cb_href') for x in value.xpath('a')]

                        partial_url = list(itertools.chain.from_iterable(partial_urls))[0].split('..')[1]

                        if len(partial_url.split()) == 2:
                            partial_url = ''.join(partial_url.split())

                        if len(partial_url.split()) == 1:
                            partial_url = ''.join(partial_url)

                        full_vagon_img_url = urljoin('https://www.vagonweb.cz', partial_url)

                        r = requests.get(
                            url=full_vagon_img_url,
                            headers=self.headers
                        )

                        _g = GetXMLEtree(response_data=r.text)

                        full_vagon_img_xpath = '//img/@src'

                        full_vagon_img = sorted(list(set([x for x in _g.xml_etree.xpath(full_vagon_img_xpath)])))[-1]

                        vagon_data['vagon_img'] = full_vagon_img

                if vagon_data.get('number'):
                    final_data['cars'][current_key] = vagon_data
                else:
                    final_data['train_info'] = vagon_data

            vagon_mapping = {int(val['number']): key for key, val in final_data['cars'].items()}
            final_data['car_mapping'] = vagon_mapping

        self.final_data = final_data
