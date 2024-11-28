import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit.forms import WPFWindow
from System.Collections.Generic import List
import requests
import json
import clr
import sys
clr.AddReference("System.Drawing")
import inspect

doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument
# from langchain_core.tools import tool

# ModalForm class for WPF interaction
class ModalForm(WPFWindow):
    def __init__(self, xaml_file_name):
        WPFWindow.__init__(self, xaml_file_name)
        self.prompt = None
        self.ShowDialog()

    def process_input(self, sender, e):
        # Get the text input from the TextBox
        self.prompt = self.textBox.Text
        print(self.prompt)

        #here to test new function 
        # toggle_wall_visibility(doc,uidoc)
        # override_window_graphics(doc)
        # toggle_category_visibility(doc, uidoc, "walls")
        # select_elements_by_category(doc, uidoc, "walls")
        # get_elements_by_category(doc,  "walls")


        # Call the server API with the prompt
        call_server_api(self.prompt)

    def addTextBtn_Click(self, sender, e):
        # Process the input from the TextBox
        self.process_input(sender, e)

def call_server_api(prompt):
    """
    Sends a prompt to the server API, parses the response, and executes the corresponding function.

    Args:
        prompt (str): The user input to be sent to the server.
    """
    endpoint = "http://localhost:5000/revit/"  # Update with the actual server URL if different
    data = {'prompt': prompt}
    
    try:
        # Send POST request to the server
        response = requests.post(endpoint, json=data)
        
        if response.status_code == 200:
            print("Server processed the input successfully.")
            
            # Parse the JSON response
            response_json = response.json()
            print("Server Response: ", response_json)
            
            # Extract function name and arguments
            function_call = response_json.get('ai_response', {}).get('choices', [{}])[0].get('message', {}).get('function_call')
            
            if function_call:
                function_name = function_call.get("name")
                arguments = json.loads(function_call.get("arguments", "{}"))
                
                if function_name:
                    print("Executing function: {0} with arguments: {1}".format(function_name, arguments))
                    
                    # Pass extracted arguments dynamically
                    # execute_function(function_name, *arguments.values())
                    # execute_function(function_name, doc, uidoc, **arguments)
                    execute_function(function_name, **arguments)
                else:
                    print("No function name found in the server response.")
            else:
                print("No function call detected in AI response.")
        else:
            # Handle HTTP error responses
            print("Error from server: {0} - {1}".format(response.status_code, response.text))
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        print("Error connecting to server: {0}".format(e))

# Function to extract the function name from the server response
def extract_function_name(response_json):
    # Assuming response structure has a field 'function_call' with the 'name'
    # function_name = response_json.get('ai_response', {}).get('choices', [{}])[0].get('message', {}).get('function_call', {}).get('name')
    # print("Extracted function name: {0}".format(function_name))
    # return function_name
    try:
        function_name = response_json.get('ai_response', {}).get('choices', [{}])[0].get('message', {}).get('function_call', {}).get('name', None)
        
        if function_name is None:
            print("Function name is None or not found in the response.")
        else:
            print("Extracted function name: {0}".format(function_name))
        
        return function_name
    except Exception as e:
        print("Error extracting function name: {0}".format(e))
        return None

#region 
# Functions to retrieve Revit elements
def get_all_windows(doc):
    """Get all windows in the Revit project."""
    windows = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_Windows) \
        .WhereElementIsNotElementType() \
        .ToElements()

    window_list = [window.Name for window in windows]
    return window_list

def get_all_doors(doc):
    """Get all doors in the Revit project."""
    doors = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_Doors) \
        .WhereElementIsNotElementType() \
        .ToElements()

    door_list = [door.Name for door in doors]
    return door_list

def get_all_rooms(doc):
    """Get all rooms in the Revit project."""
    rooms = FilteredElementCollector(doc) \
        .OfCategory(BuiltInCategory.OST_Rooms) \
        .WhereElementIsNotElementType() \
        .ToElements()

    room_list = [room.Name for room in rooms]
    return room_list

def select_all_windows(doc, uidoc):
    """Select all windows in the Revit project."""
    try:
        # Collect all windows
        windows = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_Windows) \
            .WhereElementIsNotElementType() \
            .ToElementIds()

        # Create a .NET List of ElementId for selection
        window_ids = List[ElementId]()
        for window_id in windows:
            window_ids.Add(window_id)

        # Set the selection in the UI
        uidoc.Selection.SetElementIds(window_ids)
        print("Successfully selected {len(window_ids)} windows.")
    except Exception as e:
        print("Error selecting windows: {0}".format(e))

def toggle_wall_visibility(doc, uidoc):
    """Toggle visibility of walls in the active view."""
    try:
        active_view = uidoc.ActiveView

        # Check if the active view allows graphics overrides
        if not active_view.IsValidObject or not isinstance(active_view, (ViewPlan, View3D)):
            print("Error: The active view does not support graphics overrides.")
            return

        # Get wall category
        wall_category = doc.Settings.Categories.get_Item(BuiltInCategory.OST_Walls)
        category_id = wall_category.Id

        # Get the current visibility for walls
        visibility = active_view.GetCategoryHidden(category_id)

        # Start a transaction
        t = Transaction(doc, "Toggle Wall Visibility")
        t.Start()

        # Toggle visibility
        new_visibility = not visibility
        active_view.SetCategoryHidden(category_id, new_visibility)

        # Commit the transaction
        t.Commit()

        # Confirm action
        print("Wall visibility toggled. Walls are now {0}.".format("hidden" if new_visibility else "visible"))
    except Exception as e:
        print("Error toggling wall visibility: {0}".format(e))
# Logic to execute based on the context

def execute_function_(function_name, *args, **kwargs):
    """
    Executes the specified function with dynamic arguments.

    Args:
        function_name (str): The name of the function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    """
    function_mapping = {
        # "get_all_windows": (get_all_windows, 1),
        # "get_all_doors": (get_all_doors, 1),
        # "get_all_rooms": (get_all_rooms, 1),
        "toggle_category_visibility": (toggle_category_visibility, 3),
        "select_elements_by_category": (select_elements_by_category, 3),
        "get_elements_by_category": (get_elements_by_category, 2),
        # "select_all_windows": (select_all_windows, 2),
    }

    if function_name in function_mapping:
        try:
            func, param_count = function_mapping[function_name]
            
            # Check for the number of expected arguments
            if len(args) + len(kwargs) == param_count:
                result = func(*args, **kwargs)
                print(result)
            else:
                 raise ValueError(
                    "{0} expects {1} arguments, but {2} were given.".format(
                        function_name, param_count, len(args) + len(kwargs)
                    ))
        except Exception as e:
            print("Error executing {0}: {1}".format(function_name, e))
    else:
        print("Invalid function name: {0}".format(function_name))

def execute_function(function_name, *args, **kwargs):
    """
    Executes the specified function with dynamic arguments.

    Args:
        function_name (str): The name of the function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    """
    function_mapping = {
        # "get_all_windows": (get_all_windows, 1),
        # "get_all_doors": (get_all_doors, 1),
        # "get_all_rooms": (get_all_rooms, 1),
        "toggle_category_visibility": (toggle_category_visibility, 3),
        "select_elements_by_category": (select_elements_by_category, 3),
        "get_elements_by_category": (get_elements_by_category, 2),
        # "select_all_windows": (select_all_windows, 2),
    }

    if function_name in function_mapping:
        try:
            func, param_count = function_mapping[function_name]
            
            # Dynamically prepare arguments based on the expected count
            provided_args = [doc, uidoc]  # Base arguments
            if param_count <= len(provided_args):
                provided_args = provided_args[:param_count]  # Trim if fewer args are needed
            
            # Include kwargs if necessary
            total_args = len(provided_args) + len(kwargs)
            if total_args == param_count:
                result = func(*provided_args, **kwargs)
                print("Result from {0}: {1}".format(function_name, result))
            else:
                raise ValueError(
                    "{0} expects {1} arguments, but {2} were given.".format(function_name, param_count, total_args)
                )
        except Exception as e:
            print("Error executing {0}: {1}".format(function_name, e))
    else:
        print("Invalid function name: {0}".format(function_name))

#endregion


#make hide more generic dependig on the user inputs 
def toggle_category_visibility(doc, uidoc, category_name):
    """Toggle visibility for a given category in the active view."""
    try:
        # Map category name to BuiltInCategory
        category_enum = map_user_input_to_category(category_name)
        if not category_enum:
            print("Error: Invalid category name.")
            return "Invalid category"

        # Get the active view
        active_view = uidoc.ActiveView
        if not active_view.IsValidObject:
            print("Error: Active view is not valid.")
            return "Invalid active view"

        # Get category from Revit settings
        category = doc.Settings.Categories.get_Item(category_enum)
        if not category:
            print("Error: Category '{0}' not found in the model.".format(category_name))
            return "Category '{0}' not found".format(category_name)

        # Get current visibility status
        category_id = category.Id
        visibility = active_view.GetCategoryHidden(category_id)

        # Start a transaction
        with Transaction(doc, "Toggle Category Visibility") as t:
            t.Start()
            active_view.SetCategoryHidden(category_id, not visibility)
            t.Commit()

        # Report success
        new_state = "hidden" if not visibility else "visible"
        print("Category '{0}' is now {1}.".format(category_name, new_state))
        return "Category '{0}' is now {1}".format(category_name, new_state)
    except Exception as e:
        print("Error toggling category visibility: {0}".format(e))
        return "Error: {0}".format(e)

#make the selection more generic 
def select_elements_by_category(doc, uidoc, category_name):
    """
    Select all elements in the specified category by name.

    Args:
        doc: The Revit document.
        uidoc: The Revit UI document.
        category_name: The name of the category (e.g., "windows", "doors").
    """
    try:
        # Use the mapping function to get the BuiltInCategory
        category = map_user_input_to_category(category_name)

        if not category:
            raise ValueError(
                "Invalid category name: '{0}'. Supported categories are: {1}".format(
                    category_name, ", ".join(map_user_input_to_category("").keys())
                )
            )

        # Collect all elements in the specified category
        elements = FilteredElementCollector(doc) \
            .OfCategory(category) \
            .WhereElementIsNotElementType() \
            .ToElementIds()

        # Create a .NET List of ElementId for selection
        element_ids = List[ElementId]()
        for element_id in elements:
            element_ids.Add(element_id)

        # Set the selection in the UI
        uidoc.Selection.SetElementIds(element_ids)
        print("Successfully selected {0} elements from category '{1}'.".format(len(element_ids), category_name))
    except Exception as e:
        print("Error selecting elements from category '{0}': {1}".format(category_name, e))

def get_elements_by_category(doc,  category_name):
    """
    Retrieve all elements of a specified category.

    Parameters:
        doc: The Revit document.
        category_name: The name of the category (e.g., 'windows', 'doors').
    
    Returns:
        List of element names in the specified category.
    """
    try:
        # Use the mapping function to get the BuiltInCategory
        category = map_user_input_to_category(category_name)

        if not category:
            raise ValueError(
                "Invalid category name: '{0}'. Supported categories are: {1}".format(
                    category_name, ", ".join(map_user_input_to_category("").keys())
                )
            )
        
        # Collect elements of the specified category
        elements = FilteredElementCollector(doc) \
            .OfCategory(category) \
            .WhereElementIsNotElementType() \
            .ToElements()
        
        # Print the IDs of the elements
        element_ids = [element.Id.IntegerValue for element in elements]
        print("Element IDs in category '{}':".format(category_name))
        for element_id in element_ids:
            print(element_id)
        
        # Extract and return element names
        element_list = [element.Name for element in elements]
        print(element_list)
        return element_list
    except Exception as e:
        print("Error retrieving elements for category '{0}': {1}".format(category_name, e))
        return []

def map_user_input_to_category(user_input):
    """Map user input to a BuiltInCategory."""
    CATEGORY_MAPPING = {
        "walls": BuiltInCategory.OST_Walls,
        "doors": BuiltInCategory.OST_Doors,
        "windows": BuiltInCategory.OST_Windows,
        "rooms": BuiltInCategory.OST_Rooms,
        "floors": BuiltInCategory.OST_Floors,
    }
    return CATEGORY_MAPPING.get(user_input.lower())



# Main Logic
args = getattr(sys, "argv", [])
if len(args) < 2:
    # Launch WPF ModalForm if no command-line arguments are provided
    print("Launching WPF ModalForm...")
    form = ModalForm('TextBox.xaml')

