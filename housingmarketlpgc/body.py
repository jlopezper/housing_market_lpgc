from email import header
from operator import index
from housingmarketlpgc.gmail import list_messages, get_email_details
from bs4 import BeautifulSoup
import re
import pandas as pd
from datetime import date
from housingmarketlpgc.config import config
from functools import partial, reduce
import os
import logging
from housingmarketlpgc.utils import init_logger

# from housingmarketlpgc import utils

logger = init_logger()


def get_flat_data(body_email):
    all_flat_data = [
        img_tag.get("alt")
        for img_tag in body_email["body"].find_all("img")
        if img_tag.get("alt")
    ]
    return all_flat_data


def get_flat_type(body_email):
    all_flat_data = get_flat_data(body_email)
    flat_type = [i.split()[0] for i in all_flat_data]
    return flat_type


def get_flat_price(body_email):
    price = [
        int(item.text.strip().replace(".", "").replace("€/mes", ""))
        for item in body_email["body"].find_all("span")
        if not item.text.startswith(" ") and "€/mes" in item.text
    ]
    return price


def get_flat_details(body_email):
    flat_details = [
        item.text.strip()
        for item in body_email["body"].find_all("td")
        if "m²" in item.text and "€" not in item.text
    ]
    return flat_details


def get_flat_url(body_email):
    url = [
        a["href"].split("/?xts")[0]
        for a in body_email["body"].find_all("a", href=True)
        if a.text and "inmueble" in a["href"]
    ]
    url = list(sorted(set(url), key=url.index))
    return url


def build_flat_details(service, msg_id):
    body_email = get_email_details(service=service, msg_id=msg_id)
    flat_type = get_flat_type(body_email=body_email)
    price = get_flat_price(body_email=body_email)
    flat_details = get_flat_details(body_email=body_email)
    m_squared = [int(re.findall("\d+", item)[0]) for item in flat_details]
    url = get_flat_url(body_email=body_email)
    id = [item.split("/")[-1] for item in url]

    # rooms = [int(re.findall('\d+', item)[1]) for item in flat_details]

    dict_all = {
        "id": id,
        "msg_id": [msg_id] * len(flat_type),
        "address": get_flat_data(body_email=body_email),
        "flat_type": flat_type,
        "price": price,
        "flat_details": flat_details,
        "area": m_squared,
        "url": url,
        "processed_date": [date.today().strftime("%Y-%m-%d")] * len(flat_type),
    }

    return dict_all


def msgs_to_be_processed(service):
    msgs = list_messages(
        service=service,
        user_id="me",
        label="Idealista",
        query="subject:(Nuevos anuncios hoy)",
    )
    try:
        df = pd.read_csv(config.DATASET_DIR / "data.csv")
        to_be_processed = [
            item["id"] for item in msgs if item["id"] not in df["msg_id"].unique()
        ]
    except:
        to_be_processed = [item["id"] for item in msgs if item["id"]]
    return to_be_processed


def process_messages(service):
    msgs = msgs_to_be_processed(service=service)
    dict_res = []
    for msg in msgs:
        d = build_flat_details(service=service, msg_id=msg)
        dict_res.append(d)

    df = pd.concat(map(pd.DataFrame, dict_res), axis=0)
    return df


def save_data(df):
    logger.info("Saving data")
    path_file = config.DATASET_DIR / "data.csv"
    if not os.path.exists(path_file):
        df.to_csv(path_file, index=False, header=True)
    else:
        df.to_csv(path_file, mode="a", header=False, index=False)
