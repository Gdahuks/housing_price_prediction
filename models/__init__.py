import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

from enums import ModelEnum

FEATURES = ["price_per_m2", "area", "rooms", "floor", "year"]
TARGET = "full_price"

TEST_SIZE = 0.2


def process_json_data(data: list[dict]) -> tuple[np.array, np.array, np.array, np.array]:
    df = pd.DataFrame(data)
    df = df[[*FEATURES, TARGET]]
    df = df.dropna()

    features = df[FEATURES]
    target = df[TARGET].astype(float)
    features = features.apply(pd.to_numeric, errors="coerce")

    X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=TEST_SIZE)

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test


def get_trained_model(type: ModelEnum, data) -> None:
    model = type.value

    X_train, X_test, y_train, y_test = process_json_data(data)

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_pred_train = model.predict(X_train)

    r2_test = r2_score(y_test, y_pred)
    r2_train = r2_score(y_train, y_pred_train)

    return model, r2_test, r2_train
