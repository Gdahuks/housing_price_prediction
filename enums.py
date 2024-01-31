from __future__ import annotations

from enum import Enum

from models.knn import k_neighbors_regressor
from models.random_forest import random_forest_regressor


class ModelEnum(Enum):
    KNN = k_neighbors_regressor
    RANDOM_FOREST = random_forest_regressor

    @staticmethod
    def get_default() -> ModelEnum:
        return ModelEnum.RANDOM_FOREST


ModelNameEnum = Enum("ModelNameEnum", {e.name.upper(): e.name.lower() for e in ModelEnum}, type=str)  # type: ignore
