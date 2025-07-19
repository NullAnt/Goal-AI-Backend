# goal_ai/langchain_engine.py

from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import json
import re

# Initialize Ollama LLM
llm = Ollama(model="gemma3:4b")

# Prompt template with escaped curly braces for JSON example
prompt_template = (
    "Create a Routine for the goal. "
    "Strictly only return a JSON array where each object has a key 'time' (stores time) and a key 'message' (stores what message to display at that time). "
    "Example: [{{\"time\": \"8:00 AM\", \"message\": \"Wake up!\"}}, {{\"time\": \"8:30 AM\", \"message\": \"Breakfast\"}}, {{\"time\": \"9:00 AM\", \"message\": \"Start working on goal\"}}]. "
    "Goal: {goal}"
)

# LangChain prompt wrapper (optional, for structure)
template = PromptTemplate.from_template(prompt_template)

def clean_json_output(raw_output: str) -> str:
    """Remove markdown code fences and trim output."""
    raw_output = raw_output.strip()

    # Remove triple backticks and optional `json` label
    raw_output = re.sub(r"^```(?:json)?\s*", "", raw_output)
    raw_output = re.sub(r"\s*```$", "", raw_output)
    
    return raw_output.strip()

def generate_and_store_routine(user_goal: str, user_email: str = None) -> list | str:
    """
    Generate a routine from the user's goal using LangChain+Ollama.
    Returns either a parsed list of routines or raw output if parsing fails.
    """
    print(f"Generating routine for goal: {user_goal}")
    
    # Format the prompt
    prompt = prompt_template.format(goal=user_goal)
    
    # Call the LLM
    try:
        raw_output = llm.invoke(prompt)
    except Exception as e:
        print(f"LLM error: {e}")
        return "Failed to generate routine."

    print("Raw LLM output:")
    print(raw_output)

    # Clean and parse
    cleaned_output = clean_json_output(raw_output)

    try:
        routine = json.loads(cleaned_output)
        print("\n✅ Parsed Routine:")
        for item in routine:
            print(f"{item['time']}: {item['message']}")

        print()
        print(routine)
        return routine
    except json.JSONDecodeError:
        print("\n❌ Failed to parse JSON. Returning raw output.")
        return cleaned_output
