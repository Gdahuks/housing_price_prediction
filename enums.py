from enum import Enum

from models.knn import k_neighbors_regressor


class ModelEnum(Enum):
    KNN = k_neighbors_regressor
