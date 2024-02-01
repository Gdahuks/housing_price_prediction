from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

from enums import ModelEnum

FEATURES = ["area", "rooms", "floor", "year"]
TARGET = "full_price"


def process_json_data(data: list[dict]) -> tuple[np.array, np.array]:
    df = pd.DataFrame(data)
    df = df[[*FEATURES, TARGET]]
    df = df.dropna()

    features = df[FEATURES]
    x = np.array(features.apply(pd.to_numeric, errors="coerce"))
    y = np.array(df[TARGET].astype(float))

    return x, y


def get_trained_model(model_type: ModelEnum, data: list[dict]) -> tuple[Any, float]:
    model = model_type.value

    x, y = process_json_data(data)

    model.fit(x, y)

    y_pred_train = model.predict(x)
    r2_train = r2_score(y, y_pred_train).astype(float)

    return model, r2_train
