from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import openai
import subprocess
import uvicorn
import os
from langchain import hub


# Initialize FastAPI app
app = FastAPI()

# Configure OpenAI API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Request model for API
class RevitRequest(BaseModel):
    prompt: str

# Function to call OpenAI API
def call_openai(prompt, function_definitions):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Revit assistant."},
                {"role": "user", "content": prompt},
            ],
            functions=function_definitions,
            function_call="auto",
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

# Function to call Revit-specific operations via script
def call_revit_script(function_name):
    try:
        # Replace `script.py` with the actual name of your script
        result = subprocess.check_output(
            ["python", "script.py", function_name], text=True
        )
        return result.strip()
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500, detail=f"Error calling script: {e.output}"
        )

# FastAPI endpoint
@app.post("/revit/")
async def interact_with_revit(request: RevitRequest):
    prompt = request.prompt

    # Define Revit function definitions for OpenAI
    function_definitions = [
        # {
        #     "name": "get_all_windows",
        #     "description": "Retrieve all windows from the Revit model.",
        #     "parameters": {"type": "object", "properties": {}, "required": []},
        # },
        # {
        #     "name": "get_all_doors",
        #     "description": "Retrieve all doors from the Revit model.",
        #     "parameters": {"type": "object", "properties": {}, "required": []},
        # },
        # {
        #     "name": "get_all_walls",
        #     "description": "Retrieve all walls from the Revit model.",
        #     "parameters": {"type": "object", "properties": {}, "required": []},
        # },
        # {
        #     "name": "select_all_windows",
        #     "description": "make a selection to all windows from the Revit model.",
        #     "parameters": {"type": "object", "properties": {}, "required": []},
        # },
        {
        "name": "toggle_category_visibility",
        "description": "Toggle visibility for a specific category in the active view.",
        "parameters": {
            "type": "object",
            "properties": {
                "category_name": {"type": "string", "description": "Category name (e.g., walls, doors, windows)"},
            },
            "required": ["category_name"],
        },
        },
        {
        "name": "select_elements_by_category",
        "description": "Select all elements in a specific category in the active view.",
        "parameters": {
            "type": "object",
            "properties": {
                "category_name": {
                    "type": "string",
                    "description": "Category name (e.g., walls, doors, windows)"
                },
            },
            "required": ["category_name"],
        },
        },
        {
            "name": "get_elements_by_category",
            "description": "Retrieve all elements in a specific category from the Revit document.",
            "parameters": {
                "type": "object",
                "properties": {
                    "category_name": {
                        "type": "string",
                        "description": "The name of the category to retrieve elements from (e.g., walls, doors, windows)."
                    }
                },
                "required": ["category_name"]
            }
        }
    ]

    # Call OpenAI API
    ai_response = call_openai(prompt, function_definitions)

    # choice = ai_response["choices"][0]["message"]
    choice = ai_response.choices[0].message
    # Determine function call
    if "function_call" in ai_response.choices[0].message:
        function_name = ai_response.choices[0].message["function_call"]["name"]
        arguments = eval(choice["function_call"]["arguments"])  # Safely parse arguments
        # result = call_revit_script(function_name)
        result = call_revit_script(function_name, arguments)
    else:
        result = f"No function selected. AI response: {ai_response}"

    return {"ai_response": ai_response, "revit_result": result}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")

