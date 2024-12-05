import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit.forms import WPFWindow
from System.Collections.Generic import List
from System.Collections.Generic import List
from Autodesk.Revit.DB import ElementId, BuiltInCategory, FilteredElementCollector, XYZ
import requests
import json
import clr
import sys
clr.AddReference("System.Drawing")
import inspect
import csv
import os
import re


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
        # select_small_rooms(doc, uidoc, area_threshold=10)
        # create_room_schedule(doc, schedule_name="Room Schedule__")
        # highlight_rooms_without_doors(doc, uidoc)
        # check_and_create_csv("D:\Revit_and\test_room_content")
        # export_elements_inside_rooms_to_csv(doc, "D:\\Revit_and\\test_room_content\\test_room_content.csv")

        # export_elements_inside_rooms(doc)



        # Call the server API with the prompt
        call_server_api(self.prompt)

    def addTextBtn_Click(self, sender, e):
        # Process the input from the TextBox
        self.process_input(sender, e)

#get the function calling result from the response 
def call_server_api_(prompt):
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

#get the actions and innputs not function calling of api but custom prompt React
def call_server_api(prompt):
    """
    Sends a prompt to the server API, parses the response, and executes the corresponding function(s).

    Args:
        prompt (str): The user input to be sent to the server.
    """
    endpoint = "http://localhost:5000/revit/"  # Update with the actual server URL if different
    data = {'prompt': prompt}
    
    try:
        response = requests.post(endpoint, json=data)  # Example API call
        if response.status_code == 200:
            response_json = response.json()
            print("Server Response: ", response_json)

            # Extract actions from the response
            actions = extract_actions_from_content(response_json)
            print("actions is ", actions)

            if actions:
                for action in actions:
                    function_name = action.get("action")
                    arguments = action.get("action_input", {})
                    status = action.get("status", "success")  # Assuming status is part of the response

                    if status == "success":
                        print("Executing function '{0}' with arguments: {1}".format(function_name, arguments))
                        try:
                            execute_function(function_name, **arguments)
                        except Exception as e:
                            print("Error executing function {0}: {1}".format(function_name, str(e)))
                    elif status == "error":
                        error_message = action.get("error", "Unknown error")
                        print("Error in server-side function '{0}': {1}".format(function_name, error_message))
            else:
                print("No actions returned by the server.")
        else:
            # Handle HTTP error responses
            print("Error from server: {0} - {1}".format(response.status_code, response.text))
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        print("Error connecting to server: {0}".format(str(e)))

#get all the actions and actions inputs from the server response
def extract_actions_from_content(server_response):
    """
    Extracts actions and their inputs from the ai_response content in the server response.

    Args:
        server_response (dict): The JSON response from the server.

    Returns:
        list: A list of dictionaries containing action details (action and input).
    """
    # Navigate to the 'content' field in the response
    try:
        content = (
            server_response.get('ai_response', {})
            .get('choices', [])[0]
            .get('message', {})
            .get('content', "")
        )
    except (IndexError, AttributeError):
        return []

    # Regex pattern to extract actions and their inputs
    action_pattern = r"Action: (.*?)\nAction Input: (.*?)\n"

    # Find all matches
    matches = re.findall(action_pattern, content, re.DOTALL)

    # Parse and store results
    extracted_actions = []
    for action, action_input in matches:
        try:
            # Try to parse the action input as JSON
            action_input = json.loads(action_input.strip())
        except json.JSONDecodeError:
            action_input = action_input.strip()  # Keep as string if JSON parsing fails

        extracted_actions.append({"action": action.strip(), "action_input": action_input})

    return extracted_actions

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
        "select_small_rooms": (select_small_rooms, 3),
        "create_room_schedule": (create_room_schedule, 2),
        "highlight_rooms_without_doors": (highlight_rooms_without_doors, 2),
        
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
            # print(*args, **kwargs)
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

def execute_function(function_name, *args, **kwargs):
    """
    Executes the specified function with dynamic arguments.

    Args:
        function_name (str): The name of the function to execute.
        *args: Positional arguments for the function.
        **kwargs: Keyword arguments for the function.
    """
    # Define a mapping of function names to their required arguments
    function_mapping = {
        "toggle_category_visibility": (toggle_category_visibility, True),  # Needs doc, uidoc
        "select_elements_by_category": (select_elements_by_category, True),  # Needs doc, uidoc
        "get_elements_by_category": (get_elements_by_category, False),  # Needs only doc
        "create_room_schedule": (create_room_schedule, False),  # Needs only doc
        "highlight_rooms_without_doors": (highlight_rooms_without_doors, True),  # Needs doc, uidoc
        "export_elements_inside_rooms": (export_elements_inside_rooms, False)
    }

    if function_name in function_mapping:
        try:
            func, needs_uidoc = function_mapping[function_name]

            # Base arguments
            base_args = [doc]
            if needs_uidoc:
                base_args.append(uidoc)

            # Add additional arguments
            all_args = base_args + list(args)

            # Execute the function
            result = func(*all_args, **kwargs)
            print("Result from {0}: {1}".format(function_name, result))

        except Exception as e:
            print("Error executing {0}: {1}".format(function_name, e))
    else:
        print("Invalid function name: {0}".format(function_name))

#region tools

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

def get_all_rooms(doc):
    """
    Collect all rooms in the Revit document.

    Args:
        doc: The Revit document.
    
    Returns:
        List of room elements.
    """
    try:
        rooms = FilteredElementCollector(doc) \
            .OfCategory(BuiltInCategory.OST_Rooms) \
            .WhereElementIsNotElementType() \
            .ToElements()
        return rooms
    except Exception as e:
        print("Error collecting rooms: {0}".format(e))
        return []

def get_room_area(room):
    """
    Get the area of the room and convert it from square feet to square meters.

    Args:
        room: The Revit room element.
    
    Returns:
        Area of the room in square meters.
    """
    try:
        area_param = room.get_Parameter(BuiltInParameter.ROOM_AREA)
        if area_param:
            area_in_sqft = area_param.AsDouble()
            area_in_m2 = area_in_sqft * 0.092903  # Convert from sqft to sqm
            return area_in_m2
        else:
            print("Room '{0}' does not have an area parameter.".format(room.name))
            return None
    except Exception as e:
        print("Error getting room area: {0}".format(e))
        return None
    
def filter_small_rooms(rooms, area_threshold):
    """
    Filter rooms that have an area below the specified threshold.

    Args:
        rooms: List of Revit room elements.
        area_threshold: The area threshold for selection in square meters.
    
    Returns:
        List of ElementId for rooms below the threshold area.
    """
    try:
        small_room_ids = List[ElementId]()
        for room in rooms:
            area_in_m2 = get_room_area(room)
            if area_in_m2 and area_in_m2 < area_threshold:
                small_room_ids.Add(room.Id)
        return small_room_ids
    except Exception as e:
        print("Error filtering small rooms: {0}".format(e))
        return List[ElementId]()

def select_rooms(uidoc, small_room_ids):
    """
    Select rooms in the Revit UI based on their ElementId.

    Args:
        uidoc: The Revit UI document.
        small_room_ids: List of ElementIds for rooms to select.
    """
    try:
        if small_room_ids.Count > 0:
            uidoc.Selection.SetElementIds(small_room_ids)
            print("Successfully selected  rooms.")
        else:
            print("No rooms found below the area threshold.")
    except Exception as e:
        print("Error selecting rooms: {0}".format(e))

def select_small_rooms(doc, uidoc, area_threshold=10):
    """
    Select rooms with an area below the specified threshold.

    Args:
        doc: The Revit document.
        uidoc: The Revit UI document.
        area_threshold: The area threshold for room selection (default is 10m).
    """
    try:
        # Step 1: Get all rooms in the document
        rooms = get_all_rooms(doc)

        # Step 2: Filter rooms with area below the threshold
        small_room_ids = filter_small_rooms(rooms, area_threshold)

        # Step 3: Select the filtered rooms in the UI
        select_rooms(uidoc, small_room_ids)

    except Exception as e:
        print("Error in selecting small rooms: {0}".format(e))

#### create room schedule
def create_room_schedule(doc, schedule_name="Room Schedule_,"):
    """
    Create a new room schedule in the Revit project.

    Args:
        doc: The Revit document.
        schedule_name: Name of the schedule to be created.
    """
    try:
        # Check if a schedule with the given name already exists
        existing_schedule = None
        for schedule in FilteredElementCollector(doc).OfClass(ViewSchedule):
            if schedule.Name == schedule_name:
                existing_schedule = schedule
                break

        if existing_schedule:
            print("A schedule named '{0}' already exists.".format(schedule_name))
            return existing_schedule

        # Create a new schedule for rooms
        room_category = Category.GetCategory(doc, BuiltInCategory.OST_Rooms)
        if not room_category:
            raise Exception("Room category not found in the project.")

        with Transaction(doc, "Create Room Schedule") as t:
            t.Start()
            room_schedule = ViewSchedule.CreateSchedule(doc, room_category.Id)

            # Set the name of the schedule
            room_schedule.Name = schedule_name

            # Add fields to the schedule
            add_schedule_field(room_schedule, BuiltInParameter.ROOM_NAME)
            add_schedule_field(room_schedule, BuiltInParameter.ROOM_LEVEL_ID)
            add_schedule_field(room_schedule, BuiltInParameter.ROOM_AREA)

            t.Commit()

        print("Room schedule '{0}' created successfully.".format(schedule_name))
        return room_schedule

    except Exception as e:
        print("Error creating room schedule: {0}".format(e))
        return None

def add_schedule_field(schedule, built_in_param):
    """
    Add a field to the specified schedule.

    Args:
        schedule: The ViewSchedule object.
        built_in_param: BuiltInParameter corresponding to the field.
    """
    try:
        field_id = ElementId(built_in_param)
        schedule_field = schedule.Definition.AddField(ScheduleFieldType.Instance, field_id)
        print("Field with parameter '{0}' added to the schedule.".format(built_in_param))
        return schedule_field
    except Exception as e:
        print("Error adding field with parameter '{0}': {1}".format(built_in_param,e))
        return None

#### 
def highlight_rooms_without_doors(doc, uidoc):
    """
    Highlight rooms in the model that do not have any doors.

    Args:
        doc: The Revit document.
        uidoc: The Revit UI document.
    """
    try:
        # Step 1: Retrieve all rooms
        rooms = get_all_rooms(doc)

        # Step 2: Identify rooms without doors
        room_ids_without_doors = find_rooms_without_doors(doc, rooms)

        # Step 3: Convert to ICollection[ElementId]
        ids_to_highlight = List[ElementId]()
        for room_id in room_ids_without_doors:
            ids_to_highlight.Add(room_id)

        # Step 4: Highlight rooms in the UI
        uidoc.Selection.SetElementIds(ids_to_highlight)
        print("Highlighted {} rooms without doors.".format(len(room_ids_without_doors)))

    except Exception as e:
        print("Error highlighting rooms without doors: {}".format(e))

def find_rooms_without_doors(doc, rooms):
    """
    Identify rooms without doors.

    Args:
        doc: The Revit document.
        rooms: List of room elements.

    Returns:
        List of ElementIds for rooms without doors.
    """
    rooms_without_doors = []
    for room in rooms:
        try:
            # Get the room's bounding box
            room_bbox = room.get_BoundingBox(None)
            if not room_bbox:
                continue

            # Collect doors in the bounding box
            doors_in_room = []
            door_collector = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Doors).WhereElementIsNotElementType()
            for door in door_collector:
                if door.Location and door.Location.Point:
                    door_point = door.Location.Point
                    if is_point_in_bbox(door_point, room_bbox):
                        doors_in_room.append(door)

            # Check if no doors exist in the room
            if not doors_in_room:
                rooms_without_doors.append(room.Id)
        except Exception as e:
            print("Error processing room with ID {}: {}".format(room.Id.IntegerValue, e))

    return rooms_without_doors

def is_point_in_bbox(point, bbox):
    """
    Check if a point is within a bounding box.

    Args:
        point: The XYZ point to check.
        bbox: The BoundingBoxXYZ to test against.

    Returns:
        True if the point is inside the bounding box; otherwise, False.
    """
    if bbox is None:
        # print("Error: Bounding box is None.")
        return False

    min_point = bbox.Min
    max_point = bbox.Max

    return (min_point.X <= point.X <= max_point.X and
            min_point.Y <= point.Y <= max_point.Y and
            min_point.Z <= point.Z <= max_point.Z)

# #####

def get_elements_inside_room(doc, room):
    """
    Retrieve furniture elements inside a given room based on bounding box intersection.

    Args:
        doc: The Revit document.
        room: The room element to check.

    Returns:
        List of element names inside the room.
    """
    try:
        # Get the bounding box of the room
        room_bbox = room.get_BoundingBox(None)

        # Collect all furniture elements in the document
        furniture_category_filter = ElementCategoryFilter(BuiltInCategory.OST_Furniture)
        elements = FilteredElementCollector(doc).WherePasses(furniture_category_filter).WhereElementIsNotElementType().ToElements()
        elements_inside_room = []

        for element in elements:
            # Get the element's bounding box
            element_bbox = element.get_BoundingBox(None)
            if element_bbox is None:
                continue

            # Check if the element's bounding box intersects with the room's bounding box
            if is_point_in_bbox(element_bbox.Min, room_bbox) or is_point_in_bbox(element_bbox.Max, room_bbox):
                elements_inside_room.append(element)

        return elements_inside_room

    except Exception as e:
        print("Error retrieving elements inside room: {}".format(e))
        return []

def get_element_name(element):
    """
    Safely retrieve the name of an element (Family Name or Type Name). 
    If not available, return a fallback name.
    
    Args:
        element: The Revit element to get the name from.

    Returns:
        The Family Name or Type Name of the element or a fallback name if not available.
    """
    try:
        # If element has a Family property, use the Family Name (this is typical for furniture)
        if hasattr(element, 'Family') and element.Family is not None:
            return element.Family.Name
        # Otherwise, use the Type Name (this will work for many other element types)
        elif hasattr(element, 'Name') and element.Name is not None:
            return element.Name
        # If element has a Type property, we may use its Name
        elif hasattr(element, 'GetType') and element.GetType() is not None:
            type_name = element.GetType().Name
            return type_name
        else:
            return "Unnamed Element"
    except Exception as e:
        print("Error retrieving element name: {}".format(e))
        return "Unnamed Element"

def export_elements_inside_rooms(doc):
    """
    Export all furniture elements inside rooms to a CSV file.

    Args:
        doc: The Revit document.
        uidoc: The Revit UI document.
    """
    try:
        
        # Determine the Revit file's directory
        revit_file_path = doc.PathName
        if not revit_file_path:
            raise Exception("The document must be saved before exporting room contents.")
        
        revit_directory = os.path.dirname(revit_file_path)
        # excel_file_path = os.path.join(revit_directory, "RoomContents.xlsx")

        # Set the file path for the CSV
        file_path = os.path.join(revit_directory, "furniture_elements_inside_rooms.csv")

        # Open the file and write headers if the file doesn't exist
        with open(file_path, mode='w') as file:  # Removed 'newline' argument here
            writer = csv.writer(file)
            writer.writerow(['Room Name', 'Element Name', 'Element ID'])

            # Retrieve all rooms (SpatialElement is the correct class for rooms)
            rooms = FilteredElementCollector(doc).OfClass(SpatialElement).ToElements()

            # For each room, get the elements inside it
            for room in rooms:
                # room_name = room.Name
                
                # Get the room name via get_Parameter
                room_name_param = room.get_Parameter(BuiltInParameter.ROOM_NAME)
                if room_name_param and room_name_param.HasValue:
                    room_name = room_name_param.AsString()
                else:
                    room_name = "Unnamed Room"  # Default if no name is found


                elements_inside_room = get_elements_inside_room(doc, room)

                # Write the room and elements' details to the CSV
                for element in elements_inside_room:
                    element_name = get_element_name(element)
                    writer.writerow([room_name, element_name, element.Id.IntegerValue])

        # TaskDialog.Show("Export Complete", "Furniture elements inside rooms have been exported to {}".format(file_path))

    except Exception as e:
        print("Error exporting elements inside rooms: {}".format(e))
        # TaskDialog.Show("Error", "An error occurred while exporting: {}".format(e))

def get_element_bounding_box(element):
    """
    Get the bounding box of the element.

    Args:
        element: The Revit element to retrieve the bounding box for.

    Returns:
        BoundingBoxXYZ object or None if bounding box is not available.
    """
    try:
        # Get the bounding box of the element
        bbox = element.get_BoundingBox(None)
        
        if bbox is None:
            print("Warning: Element does not have a valid bounding box.")
            return None
        
        return bbox
    except Exception as e:
        print("Error retrieving bounding box for element: {}".format(e))
        return None
      

#endregion

# Main Logic
args = getattr(sys, "argv", [])
if len(args) < 2:
    # Launch WPF ModalForm if no command-line arguments are provided
    print("Launching WPF ModalForm...")
    form = ModalForm('TextBox.xaml')

