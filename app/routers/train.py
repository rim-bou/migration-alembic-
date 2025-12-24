from fastapi import APIRouter
from ..ml.training import train_from_db
from ..schemas import TrainResponse

router = APIRouter(tags=["ml"])

@router.post("/train", response_model=TrainResponse)
def train():
    return train_from_db()
