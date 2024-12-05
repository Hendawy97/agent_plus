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

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from pathlib import Path
from langchain_openai import ChatOpenAI
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import Image
# from langgraph.nodes.base import Node
# from langgraph.messages import MessagesState
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage


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
def call_openai_(prompt, function_definitions):
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


def call_openai(prompt, function_definitions):
    try:

        response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", 
                     "content": "You are a Revit assistant with access to the following tools: "
                        f"{[func['name'] for func in function_definitions]}.\n"
                        "Use the following format to solve the user's query:\n\n"
                        "Question: The input question you must answer.\n"
                        "Thought: Think about what to do.\n"
                        "Action: The action to take, should be one of the tools just select the same name provided in the function defention .\n"
                        "Action Input: The input to the action.\n"
                        "Observation: The result of the action.\n"
                        "...\n"
                        "Thought: I now know the final answer.\n"
                        "Final Answer: The final answer to the original input question.\n\n"
                        "Begin!\n\n"
                        f"Question: {prompt}"},
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
        },
        {
        "name": "create_room_schedule",
        "description": "Create a room schedule in Revit with room names and areas.",
        "parameters": {
            "type": "object",
            "properties": {
                
                "schedule_name": {"type": "string", "description": "The name of the schedule to create."}
            },
            "required": ["schedule_name"]
        },
        },
        {
        "name": "highlight_rooms_without_doors",
        "description": "Highlight rooms in the model that do not have any doors.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc": {"type": "object", "description": "The Revit document."},
                "uidoc": {"type": "object", "description": "The Revit UI document."}
            },
            "required": ["doc", "uidoc"]
        },
        },
        {
        "name": "export_elements_inside_rooms",
        "description": "Export the contents of each room (furniture elements) in the Revit model to an Excel file.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc": {"type": "object", "description": "The Revit document."}
            },
            "required": ["doc"]
        },
        }
    ]

    # Call OpenAI API
    ai_response = call_openai(prompt, function_definitions)

    # # choice = ai_response["choices"][0]["message"]
    # choice = ai_response.choices[0].message
    # # Determine function call
    # if "function_call" in ai_response.choices[0].message:
    #     function_name = ai_response.choices[0].message["function_call"]["name"]
    #     arguments = eval(choice["function_call"]["arguments"])  # Safely parse arguments
    #     # result = call_revit_script(function_name)
    #     result = call_revit_script(function_name, arguments)
    # else:
    #     result = f"No function selected. AI response: {ai_response}"

    # return {"ai_response": ai_response, "revit_result": result}
    return {"ai_response":ai_response}


@app.post("/revit/")
async def interact_with_revit_(request: RevitRequest):
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
        },
        {
        "name": "create_room_schedule",
        "description": "Create a room schedule in Revit with room names and areas.",
        "parameters": {
            "type": "object",
            "properties": {
                
                "schedule_name": {"type": "string", "description": "The name of the schedule to create."}
            },
            "required": ["schedule_name"]
        },
        },
        {
        "name": "highlight_rooms_without_doors",
        "description": "Highlight rooms in the model that do not have any doors.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc": {"type": "object", "description": "The Revit document."},
                "uidoc": {"type": "object", "description": "The Revit UI document."}
            },
            "required": ["doc", "uidoc"]
        },
        },
        {
        "name": "export_elements_inside_rooms",
        "description": "Export the contents of each room (furniture elements) in the Revit model to an Excel file.",
        "parameters": {
            "type": "object",
            "properties": {
                "doc": {"type": "object", "description": "The Revit document."}
            },
            "required": ["doc"]
        },
        }
    ]

    # Call OpenAI API
    ai_response = call_openai(prompt, function_definitions)

    choice = ai_response.choices[0].message

    # Prepare actions list
    actions = []

    try:
        # Check if AI generated function calls
        if "function_call" in choice:
            # Parse and process function calls
            function_call = choice["function_call"]
            function_name = function_call["name"]
            arguments = json.loads(function_call["arguments"])

            try:
                # Call the Revit script for the function
                result = call_revit_script(function_name, arguments)
                actions.append({
                    "function_name": function_name,
                    "arguments": arguments,
                    "status": "success",
                    "result": result
                })
            except Exception as e:
                actions.append({
                    "function_name": function_name,
                    "arguments": arguments,
                    "status": "error",
                    "error": str(e)
                })
        else:
            # Parse actions and inputs from content if no structured function calls are present
            content = choice["content"]
            lines = content.split("\n")
            for line in lines:
                if line.startswith("Action:"):
                    function_name = line.split(":", 1)[1].strip()
                elif line.startswith("Action Input:"):
                    arguments = json.loads(line.split(":", 1)[1].strip())
                    try:
                        # Call the Revit script for the parsed function
                        result = call_revit_script(function_name, arguments)
                        actions.append({
                            "function_name": function_name,
                            "arguments": arguments,
                            "status": "success",
                            "result": result
                        })
                    except Exception as e:
                        actions.append({
                            "function_name": function_name,
                            "arguments": arguments,
                            "status": "error",
                            "error": str(e)
                        })
    except Exception as e:
        actions.append({"status": "error", "error": f"Failed to process AI response: {str(e)}"})

    return {"ai_response": {"actions": actions}}


#region

# llm = ChatOpenAI(model="gpt-4o-mini")


# FUNCTION_MAP = {
#     "add": add,
#     "multiply": multiply,
#     "divide": divide,
#     "subtract":subtract
# }

# def get_tool_functions():
#     tools_config = [
#         {"function": "add", "description": "Adds two numbers"},
#         {"function": "multiply", "description": "Multiplies two numbers"},
#         {"function": "divide", "description": "Divides two numbers"},
#         {"function": "subtract", "description": "subtract two numbers"}
#     ]
#     tools = []
#     for tool in tools_config:
#         func_name = tool["function"]
#         description = tool["description"]
#         if func_name in FUNCTION_MAP:
#             func = FUNCTION_MAP[func_name]
#             if not func.__doc__:  # Dynamically set docstring if missing
#                 func.__doc__ = description
#             tools.append(func)
#         else:
#             raise ValueError(f"Function '{func_name}' not found in FUNCTION_MAP.")
#     return tools


# tools = get_tool_functions()
# llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

# # System message
# sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")

# # Node
# def assistant(state: MessagesState):
#    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}


# @app.post("/run")
# async def run_langgraph(inputs: Dict[str, Any]):
#     """Endpoint to execute a graph with LangGraph."""
#     try:
#         tools = get_tool_functions()
#         llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)
        
#         # Graph setup
#         builder = StateGraph(MessagesState)
#         builder.add_node("assistant", assistant)
#         builder.add_node("tools", ToolNode(tools))
#         builder.add_edge(START, "assistant")
#         builder.add_conditional_edges("assistant", tools_condition)
#         builder.add_edge("tools", "assistant")
#         react_graph = builder.compile()
        
#         # Add inputs and execute graph
#         output = react_graph.run(inputs)
#         return {"result": output}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


#endregion

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="debug")

