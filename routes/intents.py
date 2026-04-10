from fastapi import APIRouter
from core.intents import intents_data

router = APIRouter()

@router.get("/intents")
def get_intents():
    return {
        "intents": [
            {"intent": intent["intent"], "examples": intent["examples"]}
            for intent in intents_data
        ]
    }