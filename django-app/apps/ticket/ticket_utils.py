import base64
import io
import json
import os
import re
from datetime import datetime

import PyPDF2
import lxml.html as html
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from lxml import etree
from lxml.etree import XMLSyntaxError, ParserError
from tika import parser


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


def process_ticket(ticket_file: InMemoryUploadedFile) -> dict:
    parsedPDF = parser.from_buffer(ticket_file)

    parsed_info = {}

    content = parsedPDF["content"]
    content = re.sub("\n+", "\n", content)

    content_one_line = content.replace("\n", " ")

    parsed_info["tickets"] = list(
        map(
            str.strip,
            re.search("( [A-Z]-)(.*?)(¦)", content_one_line)[2].replace("A-Cena bazowa:", "").split(',')
        )
    )

    purchase_date = re.search("Data wydruku:.*", content)[0].replace("Data wydruku:", "").strip()
    parsed_info["purchase_date"] = datetime.strptime(purchase_date, "%Y-%m-%d %H:%M:%S")
    year = parsed_info["purchase_date"].year
    parsed_info["carrier"] = re.search("Przewoźnik:.*", content)[0].replace("Przewoźnik:", "").strip()

    basic_info = list(map(str.strip, re.search("(KL./CL.)(.*)( SUMA )", content_one_line)[2].split(" * ")))

    time_format = "%Y.%d.%m %H:%M"
    start_time = "{y}.{d} {t}".format(y=year, d=basic_info[0], t=basic_info[1])
    parsed_info["start_time"] = datetime.strptime(start_time, time_format)

    finish_time = "{y}.{d} {t}".format(y=year, d=basic_info[4], t=basic_info[5])
    parsed_info["finish_time"] = datetime.strptime(finish_time, time_format)

    parsed_info["start_place"] = basic_info[2]
    parsed_info["finish_place"] = basic_info[3]
    parsed_info["car_class"] = int(basic_info[6])
    parsed_info["stops"] = list(map(str.strip, re.search("(PRZEZ:)(.*)( SUMA )", content_one_line)[2].split(" * ")))
    parsed_info["cost"] = re.search("(SUMA PLN:)(.*?)( zł )", content_one_line)[2].strip().replace(",", ".")

    car_info_text = re.search(
        "(\d\d.\d\d)(.*)(zł)",
        re.search("(o podróży:)(.*?)(zł)", content_one_line)[0]
    )[0]

    car_info = car_info_text.split(" ")

    train_number = car_info[4] + " " + car_info[5]
    total_length = car_info[7]

    parsed_info["seats"] = list(
        map(
            str.strip,
            re.search(
                "({})(.*)(\d m\.)".format(total_length),
                car_info_text
            )[2].split(",")
        )
    )

    parsed_info["train_number"] = train_number
    parsed_info["car_number"] = car_info[6]
    parsed_info["total_length"] = total_length

    return parsed_info


def extract_qr_code(ticket_file: InMemoryUploadedFile):
    ticket = PyPDF2.PdfFileReader(ticket_file)
    page = ticket.getPage(0)
    xObject = page['/Resources']['/XObject'].getObject()
    img = None

    for obj in xObject:
        if xObject[obj]['/Subtype'] == '/Image':
            if xObject[obj]['/Width'] == 150 and xObject[obj]['/Height'] == 150:
                img = Image.frombytes(
                    mode="RGB",
                    size=(xObject[obj]['/Width'], xObject[obj]['/Height']),
                    data=xObject[obj].getData()
                )
    if img is None:
        raise ValueError("QRCode not found.")

    return img


def pil_image_to_base64(image: Image) -> str:
    qr_code_mem_file = io.BytesIO()
    image.save(qr_code_mem_file, format="PNG")
    # reset file pointer to start
    qr_code_mem_file.seek(0)
    img_bytes = qr_code_mem_file.read()

    base64_encoded_qr_code_bytes = base64.b64encode(img_bytes)
    base64_encoded_qr_code_str = base64_encoded_qr_code_bytes.decode('ascii')
    return base64_encoded_qr_code_str


def pull_connection_current_info(train_number, start_time, start_place):
    base_path = os.path.join(settings.BASE_DIR, 'apps/ticket/resources/')
    late_trains_json = os.path.join(base_path, 'late_trains.json')

    with open(late_trains_json, 'rt') as f:
        late_trains = json.load(f)

    return {
        "status": late_trains["Status"].get(train_number, ""),
        "late": late_trains["Opóźnienie"].get(train_number, ""),
        "late_reason": late_trains["Przyczyna opóźnienia"].get(train_number, "")
    }


def load_accessibility():
    base_path = os.path.join(settings.BASE_DIR, 'apps/ticket/resources/')
    accessibility_json = os.path.join(base_path, 'dostepnosc_dworcow.json')

    with open(accessibility_json, 'rt') as f:
        accesibility = json.load(f)

    return accesibility

ACCESIBILITY_DICT = load_accessibility()
