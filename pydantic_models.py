from pydantic import BaseModel


class HouseListing(BaseModel):
    area: float
    rooms: int
    floor: int
    year: int
