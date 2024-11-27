import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit.forms import WPFWindow

import requests
import json
import clr
clr.AddReference("System.Drawing")
from System.Drawing import Bitmap, Image

import io
import os
from System.Windows.Media.Imaging import BitmapImage
from System import Uri
from System.IO import Path, FileNotFoundException
from System.Windows.Forms import  DialogResult
from Microsoft.Win32 import OpenFileDialog 

# Document object from the Revit environment
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument


class ModalForm(WPFWindow):
 
    def  __init__(self, xaml_file_name):
       
        WPFWindow.__init__(self, xaml_file_name)
        self.image_url = None
    
        self.ShowDialog()
           
    def generate_image(self, sender, e):

        self.prompt = self.textBox.Text #get text input from wpf
        prompt = self.prompt  #this is a prompt used 
        print(self.image_url)
        
        generated_image = trigger_image_generation(self.image_url, prompt)
        bitmap = BitmapImage()
        bitmap.BeginInit()
        bitmap.UriSource = Uri(Path.GetFullPath(generated_image))

        try:
            bitmap.EndInit()
        except FileNotFoundException as e:
            print(e.Message)
        else:
            self.canvas.Source = bitmap

    def addImageBtn_Click(self, sender, e):
        # Open a file dialog to select an image
        # file_dialog = OpenFileDialog()
        # file_dialog.Filter = "Image Files (*.png;*.jpg;*.jpeg;*.gif;*.bmp)|*.png;*.jpg;*.jpeg;*.gif;*.bmp|All Files (*.*)|*.*"
        # if file_dialog.ShowDialog() == DialogResult.OK:
        #     # Get the selected file path
        #     self.image_url = file_dialog.FileName

        # bitmap = BitmapImage()
        # bitmap.BeginInit()
        # bitmap.UriSource = Uri(Path.GetFullPath(file_dialog.FileName))
        # self.image_url = file_dialog.FileName

        # print(bitmap)
        # print(self.image_url)
        # try:
        #     bitmap.EndInit()
        # except FileNotFoundException as e:
        #     print(e.Message)
        # else:
        #     self.canvas.Source = bitmap

        apply_view_template(doc, "3D")

        return 

#function that call server to generate the image
def trigger_image_generation(image_url, prompt):
    endpoint = "http://localhost:5000/generate_image"
    data = {'image_url': image_url, 'prompt': prompt}
    print(data)
    # data_bytes = json.dumps(data).encode('utf-8')
    # Make a POST request to the external service
    print("prompt is ",prompt)
    try:
        response = requests.post(endpoint, json=data)
        print(response)

        # response = requests.post(endpoint, json=data_bytes)
        # Handle response (e.g., retrieve the path to the generated image)
        if response.status_code == 200:
            generated_image_path = response.json()['generated_image_path']
            print("Generated image saved att:", generated_image_path)
            return generated_image_path
        elif response.status_code == 500:
                print("Server error:", response.text)
        else:
                print("Unexpected status code:", response.status_code)
    except requests.exceptions.RequestException as e:
        print("Error:", e)

def apply_view_template(doc, template_name):
    """Apply a view template to the active view."""
    try:
        active_view = doc.ActiveView
        if not active_view:
            print("No active view found.")
            return

        # Find the view template by name
        view_templates = FilteredElementCollector(doc) \
            .OfClass(View) \
            .WhereElementIsNotElementType() \
            .ToElements()

        template = next((vt for vt in view_templates if vt.IsTemplate and vt.Name == template_name), None)
        if template:
            active_view.ApplyViewTemplateSettings(template.Id)
            print(f"View template '{template_name}' applied to the active view.")
        else:
            print(f"View template '{template_name}' not found.")
    except Exception as e:
        print(f"Error applying view template: {e}")


form = ModalForm('GenerateImagesUI.xaml')

