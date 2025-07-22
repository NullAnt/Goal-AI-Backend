from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_handler import generate_and_store_routine 


app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body model
class GoalInput(BaseModel):
    goal: str
    email: str

@app.post("/generate-routine")
async def generate(goal_input: GoalInput):
    try:
        result = generate_and_store_routine(goal_input.goal, goal_input.email)
        return {"routine": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/")
async def run_cornjob():
    return {"message": "Daily routine reminders sent successfully."}