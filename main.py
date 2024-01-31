# pylint: disable=wrong-import-position

from typing import Any

import pickle  # nosec

from dotenv.main import load_dotenv

load_dotenv()
from fastapi import FastAPI, HTTPException, APIRouter, Query
from fastapi.responses import JSONResponse
import uvicorn
import pandas as pd

from data_loaders import collect_and_upload_data
from data_downloaders import get_data_from_all_blobs
from models import get_trained_model
from enums import ModelEnum, ModelNameEnum
from pydantic_models import HouseListing, Train, Prediction

# from fastapi_utilities import repeat_every


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
    description="This will scrape housing listings from supported websites "
    "and save it into Azure Blob Storage in a JSON format.",
    status_code=201,
    responses={
        201: {"description": "Successfully scraped and uploaded data to Azure Blob Storage."},
        500: {"description": "Something went wrong."},
    },
)
def run_crawler() -> JSONResponse:
    try:
        collect_and_upload_data()
        return JSONResponse(
            status_code=201, content={"resp": "Successfully scraped and uploaded data to Azure Blob Storage."}
        )
    except Exception as ex:
        raise HTTPException(500, detail=str(ex)) from ex


@version_1_0.post(
    "/train",
    description="Trains model based on scraped data from Azure. Store model locally.",
    responses={
        200: {"model": Train},
        500: {"description": "Something went wrong."},
    },
)
def train(
    # fmt: off
    model: ModelNameEnum | None = Query(
        default=None,
        description=f"Model name to train. Default: {ModelEnum.get_default().name}"
    )
    # fmt: on
) -> JSONResponse:
    try:
        data = get_data_from_all_blobs()
        if model:
            model_type = ModelEnum.__getitem__(model.value.upper())
        else:
            model_type = ModelEnum.get_default()

        trained_model, r2_train = get_trained_model(model_type, data)  # model type could be moved to param
        _save_model(trained_model)
        return JSONResponse(
            status_code=200,
            content={
                "r2_score_train": r2_train,
                "model_used": model_type.name,
                "model_params": trained_model.get_params(),
            },
        )
    except Exception as ex:
        raise HTTPException(500, detail=str(ex)) from ex


@version_1_0.get(
    "/predict",
    description="Predicts full_price in PLN based on area, rooms, floors and year of constuction.",
    responses={
        200: {"model": Prediction},
        404: {"description": "Model not found. Please train model first."},
        500: {"description": "Something went wrong."},
    },
)
def predict(house_listing: HouseListing) -> JSONResponse:
    try:
        model = _load_model()
        x = pd.DataFrame([house_listing.dict()])
        return JSONResponse(status_code=200, content={"result": model.predict(x)[0]})
    except FileNotFoundError as ex:
        raise HTTPException(404, detail="Model not found. Please train model first.") from ex
    except Exception as ex:
        raise HTTPException(500, detail=str(ex)) from ex


app.include_router(version_1_0)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)  # nosec
