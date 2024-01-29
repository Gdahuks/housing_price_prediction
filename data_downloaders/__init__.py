import asyncio
import json
import os

from azure.storage.blob.aio import ContainerClient

CONTAINER_URL = os.getenv("CONTAINER_URL")
if CONTAINER_URL is None:
    raise ValueError("CONTAINER_URL env variable not set. Import after loading .env file")


async def get_blobs_names() -> list[str]:
    async with ContainerClient.from_container_url(CONTAINER_URL) as container_client:
        result = []
        async for blob in container_client.list_blobs():
            result.append(blob.name)
    return result


async def download_blob(blob_name: str, _container_client: ContainerClient | None = None) -> str:
    container_client = _container_client or ContainerClient.from_container_url(CONTAINER_URL)
    async with container_client.get_blob_client(blob_name) as blob_client:
        blob_data = await blob_client.download_blob(encoding="utf-8")
    data = await blob_data.readall()
    if _container_client is None:
        await container_client.close()
    return data


async def download_all_blobs() -> list[str]:
    blobs_names = await get_blobs_names()
    async with ContainerClient.from_container_url(CONTAINER_URL) as container_client:
        blobs_data = await asyncio.gather(*(download_blob(blob_name, container_client) for blob_name in blobs_names))
    return blobs_data


def remove_duplicates(data: list[dict]) -> list[dict]:
    results = {item["id"]: item for item in data}.values()
    return list(results)


def get_data_from_all_blobs() -> list[dict]:
    blobs_data = asyncio.run(download_all_blobs())
    data_in_json = [json.loads(blob_data) for blob_data in blobs_data]
    flatten_data = [item for sublist in data_in_json for item in sublist]
    return remove_duplicates(flatten_data)
