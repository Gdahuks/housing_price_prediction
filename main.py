from typing import Any

import pickle  # nosec
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd

from data_loaders import collect_and_upload_data
from data_downloaders import get_data_from_all_blobs
from models import get_trained_model
from enums import ModelEnum
from pydantic_models import HouseListing

# from fastapi_utilities import repeat_every

load_dotenv()

TWO_DAYS = 172_800  # 2 days (48h) in seconds
MODEL_PATH = "./models_bin/model.sav"

app = FastAPI()
version_1_0 = APIRouter(prefix="/v1.0", tags=["v1.0"])


def _save_model(model: Any) -> None:
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)


def _load_model() -> Any:
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)  # nosec


# @version_1_0.on_event("startup") # uncoment to run on every system's start
# @repeat_every(seconds=TWO_DAYS) # recurrent scraping can be turned on by uncommenting this line
@version_1_0.post(
    "/run-crawler",
    description="""This will scrape housing listings from supported websites and save
    it into Azure Blob Storage in a JSON format.""",
)
def run_crawler() -> JSONResponse:
    try:
        collect_and_upload_data()
        return {"resp": "Successfully scraped and uploaded data to Azure Blob Storage."}
    except Exception as ex:
        return HTTPException(500, detail=str(ex))


@version_1_0.post("/train", description="Trains model based on scraped data from Azure. Store model locally.")
def train() -> JSONResponse:
    try:
        data = get_data_from_all_blobs()
        model_type = ModelEnum.RANDOM_FOREST

        trained_model, r2_train = get_trained_model(model_type, data)  # model type could be moved to param
        _save_model(trained_model)

        return {"r2_score_train": r2_train, "model_used": model_type.name, "model_params": trained_model.get_params()}
    except Exception as ex:
        return HTTPException(500, detail=str(ex))


@version_1_0.get(
    "/predict", description="Predicts full_price in PLN based on area, rooms, floors and year of constuction."
)
def predict(house_listing: HouseListing) -> JSONResponse:
    try:
        model = _load_model()
        x = pd.DataFrame(
            {
                "area": [house_listing.area],
                "rooms": [house_listing.rooms],
                "floor": [house_listing.floor],
                "year": [house_listing.year],
            }
        )
        return {"predicted_full_price_pln": model.predict(x)[0]}
    except Exception as ex:
        return HTTPException(500, detail=str(ex))


app.include_router(version_1_0)
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, log_level="debug", reload=True)
