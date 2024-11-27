# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import openai

# from Autodesk.Revit.DB import FilteredElementCollector, BuiltInCategory, ElementCategoryFilter, FamilySymbol
# from Autodesk.Revit.DB import Element

# # Initialize FastAPI
# app = FastAPI()

# # OpenAI API Key
# openai.api_key = "your-api-key"


# def get_all_windows(doc):
#     # Get all windows in the Revit project
#     windows = FilteredElementCollector(doc) \
#         .OfCategory(BuiltInCategory.OST_Windows) \
#         .WhereElementIsNotElementType() \
#         .ToElements()

#     window_list = []
#     for window in windows:
#         window_list.append(window.Name)
    
#     return window_list

# def get_all_doors(doc):
#     # Get all doors in the Revit project
#     doors = FilteredElementCollector(doc) \
#         .OfCategory(BuiltInCategory.OST_Doors) \
#         .WhereElementIsNotElementType() \
#         .ToElements()

#     door_list = []
#     for door in doors:
#         door_list.append(door.Name)
    
#     return door_list


# # Load Revit Document (Stub)
# def load_revit_document(doc_path):
#     # Placeholder for loading a Revit document
#     return f"RevitDocument({doc_path})"

# # Define OpenAI function definitions
# function_definition = [
#     {
#         'type': 'function',
#         'function': {
#             'name': 'get_all_windows',
#             'description': 'Retrieve all window names from the Revit project.',
#             'parameters': {
#                 'type': 'object',
#                 'properties': {
#                     'doc_path': {
#                         'type': 'string',
#                         'description': 'The file path to the Revit document.'
#                     }
#                 },
#                 'required': ['doc_path']
#             }
#         }
#     },
#     {
#         'type': 'function',
#         'function': {
#             'name': 'get_all_doors',
#             'description': 'Retrieve all door names from the Revit project.',
#             'parameters': {
#                 'type': 'object',
#                 'properties': {
#                     'doc_path': {
#                         'type': 'string',
#                         'description': 'The file path to the Revit document.'
#                     }
#                 },
#                 'required': ['doc_path']
#             }
#         }
#     }
# ]

# # Request model for the API
# class RevitRequest(BaseModel):
#     doc_path: str
#     function_name: str

# # OpenAI Function Calling
# def openai_function_calling(messages, function_definitions):
#     try:
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=messages,
#             tools=function_definitions,
#             tool_choice="auto"  # Let OpenAI decide the tool
#         )
#         return response
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")

# # FastAPI Route
# @app.post("/revit/")
# async def interact_with_revit(request: RevitRequest):
#     # Load the Revit document
#     doc = load_revit_document(request.doc_path)
    
#     # Call the appropriate function based on user input
#     if request.function_name == "get_all_windows":
#         result = get_all_windows(doc)
#     elif request.function_name == "get_all_doors":
#         result = get_all_doors(doc)
#     else:
#         raise HTTPException(status_code=400, detail="Invalid function name.")
    
#     # Prepare OpenAI messages
#     messages = [
#         {"role": "system", "content": "You are an assistant that interacts with Revit projects."},
#         {"role": "user", "content": f"Can you get the {request.function_name} for this project?"},
#         {"role": "function", "content": f"Result: {result}"}
#     ]
    
#     # Call OpenAI function
#     response = openai_function_calling(messages, function_definition)
    
#     return {"revit_result": result, "openai_response": response}


#region

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import subprocess
import uvicorn
from openai import OpenAI
import os
from dotenv import load_dotenv


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
        {
            "name": "get_all_windows",
            "description": "Retrieve all windows from the Revit model.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_all_doors",
            "description": "Retrieve all doors from the Revit model.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "get_all_walls",
            "description": "Retrieve all walls from the Revit model.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
        {
            "name": "select_all_windows",
            "description": "make a selection to all windows from the Revit model.",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
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

#endregion


