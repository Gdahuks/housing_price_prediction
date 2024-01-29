import json
import os
import uuid
from datetime import datetime
from typing import Iterator

from azure.storage.blob import ContainerClient
from loguru import logger

from scraper.ogloszenia_trojmiasto import OgloszeniaTrojmiasto
from scraper.tyszkiewicz import Tyszkiewicz

CONTAINER_URL = os.getenv("CONTAINER_URL")
if CONTAINER_URL is None:
    raise ValueError("CONTAINER_URL env variable not set. Import after loading .env file")


def collect_data() -> Iterator[dict]:
    scrapers = [
        Tyszkiewicz,
        OgloszeniaTrojmiasto,
    ]

    for scraper in scrapers:
        yield from scraper.run_crawler()


def convert_data_to_json(data: Iterator[dict]) -> str:
    return json.dumps(list(data), indent=2)


def upload_data_to_blob(data: str) -> None:
    container_client = ContainerClient.from_container_url(CONTAINER_URL)
    current_date = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    uid = uuid.uuid4()
    blob_name = f"{current_date}-{uid}.json"
    blob_client = container_client.get_blob_client(blob_name)
    logger.info(f"Uploading data to blob {blob_name}...")
    blob_client.upload_blob(data)
    logger.success(f"Successfully uploaded data to blob {blob_name}")


def collect_and_upload_data() -> None:
    data = collect_data()
    json_data = convert_data_to_json(data)
    upload_data_to_blob(json_data)
