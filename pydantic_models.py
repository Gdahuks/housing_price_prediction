from pydantic import BaseModel, Field


class HouseListing(BaseModel):
    area: float = Field(..., gt=0, description="Area of the house in m2.")
    rooms: int = Field(..., gt=0, description="Number of rooms in the house.")
    floor: int = Field(..., ge=0, description="Floor number of the house.")
    year: int = Field(..., description="Year of construction of the house.")


class Train(BaseModel):
    r2_score_train: float = Field(..., description="R2 score of the trained model on dataset it was trained.")
    model_used: str = Field(..., description="Model used for training.")
    model_params: dict = Field(..., description="Model parameters.")


class Prediction(BaseModel):
    result: float = Field(..., description="Predicted full price in PLN.")
