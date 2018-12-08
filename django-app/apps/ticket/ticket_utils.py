from django.core.files.uploadedfile import InMemoryUploadedFile
import re
from tika import parser
from datetime import datetime


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
