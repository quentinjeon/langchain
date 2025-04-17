from fastapi import APIRouter, Depends
from pydantic import BaseModel
from ..chains.qa_chain import build_chain
from ..deps import get_mongo

router = APIRouter()
chain = build_chain()

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/chat")
def chat(req: ChatRequest, db = Depends(get_mongo)):
    history = db.history.find_one({"_id": req.session_id}) or {"messages": []}
    response = chain({"question": req.message,
                      "chat_history": history["messages"]})
    history["messages"].append((req.message, response["answer"]))
    db.history.update_one({"_id": req.session_id},
                          {"$set": history}, upsert=True)
    return {"answer": response["answer"]} 