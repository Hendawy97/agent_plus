from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv
import openai
import subprocess
import uvicorn
import os
from langchain import hub
from langchain_openai import ChatOpenAI

from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition
from langgraph.prebuilt import ToolNode
from IPython.display import Image, display


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
                
                # {f"""role": "system", "content": "Answer the following questions as best you can. You have access to the following tools:in the {function_definitions}
                #  Use the following format:

                #     Question: the input question you must answer

                #     Thought: you should always think about what to do

                #     Action: the action to take, should be one of {function_definitions}

                #     Action Input: the input to the action

                #     Observation: the result of the action

                #     ... (this Thought/Action/Action Input/Observation can repeat N times)

                #     Thought: I now know the final answer

                #     Final Answer: the final answer to the original input question

                #     Begin!

                #     Question: {prompt}

                 
                #  """
                #  }
                
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
        },
            {
        "name": "select_small_rooms",
        "description": "Select rooms with an area below a specified threshold.",
        "parameters": {
            "type": "object",
            "properties": {
                "area_threshold": {
                    "type": "number",
                    "description": "The maximum room area (in square meters) to qualify for selection.",
                    "default": 10
                },
            },
            "required": ["area_threshold"]
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

