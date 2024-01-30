from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, APIRouter, Response
from fastapi.responses import JSONResponse
from fastapi_utilities import repeat_every
import uvicorn
import pickle

from data_loaders import collect_and_upload_data
from data_downloaders import get_data_from_all_blobs
from models import get_trained_model
from enums import ModelEnum

load_dotenv()

TWO_DAYS = 172_800  # 2 days (48h) in seconds
MODEL_PATH = "./models_bin/model.sav"

app = FastAPI()
version_1_0 = APIRouter(prefix="/v1.0", tags=["v1.0"])


def _save_model(model) -> None:
    pickle.dump(model, open(MODEL_PATH, "wb"))


# @version_1_0.on_event("startup") # uncoment to run on every system's start
# @repeat_every(seconds=TWO_DAYS) # recurrent scraping can be turned on by uncommenting this line
@version_1_0.post(
    "/run-crawler",
    description="This will scrape housing listings from supported websites and save it into Azure Blob Storage in a JSON format.",
)
def run_crawler() -> JSONResponse:
    try:
        collect_and_upload_data()
        return {"resp": "Successfully scraped and uploaded data to Azure Blob Storage."}
    except Exception as ex:
        return HTTPException(500, detail=str(ex))


@version_1_0.post(
    "/train",
)
def train() -> JSONResponse:
    data = get_data_from_all_blobs()
    model, r2_test, r2_train = get_trained_model(ModelEnum.KNN, data)  # todo: model type could be moved to param
    _save_model(model)

    return {"r2_score_test": r2_test, "r2_score_train": r2_train, "model_params": model.get_params()}


app.include_router(version_1_0)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug")
