
import torch
import os
from pathlib import Path
from huggingface_hub import HfApi
from diffusers.utils import load_image
from PIL import Image
import numpy as np
from controlnet_aux import MLSDdetector
from diffusers import (
    ControlNetModel,
    StableDiffusionControlNetPipeline,
    UniPCMultistepScheduler,
)
from flask import Flask, request ,jsonify
import traceback
import logging
from datetime import datetime

app = Flask(__name__)

initialization_done = False

# Initialize MLSD detector and ControlNet only once
def initialize_models():
    global initialization_done

    if not initialization_done:
        global processor, pipe, generator
        # MLSD detector
        processor = MLSDdetector.from_pretrained('lllyasviel/ControlNet')

        # ControlNet
        checkpoint = "lllyasviel/control_v11p_sd15_mlsd"
        controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
        pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
        )

        # Getting image back from model
        pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
        pipe.enable_model_cpu_offload()

        generator = torch.manual_seed(0)
        initialization_done = True

@app.before_request
def load_user():
    initialize_models()
   

@app.route('/generate_image', methods=['POST'])
def generate_image():

    try:
        # Parse request data (e.g., image URL and prompt)
        image_url = request.json['image_url']
        prompt = request.json['prompt']

        print("image_url:", image_url)
        logging.debug("image_url: %s", image_url)
        print("prompt:", prompt)
        logging.debug("image_url: %s", prompt)
        
        image = load_image(image_url)
        control_image = processor(image)
        # Continue with the rest of the code
        generated_image = pipe(prompt, num_inference_steps=30, generator=generator, image=control_image).images[0]

        # Save generated image
        # generated_image_path = "image_out_web01.png"  # Relative path
        base_path = r"C:\Users\AhmedHassan.Ali\Downloads\RenderPlus\RenderPlus\BIMRenderPlus.extension\RenderPlus.tab\Tool.panel\ShowWPF.pushbutton"
        # generated_image_filename = "image_out_web01.png"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        generated_image_filename = f"image_out_web01_{timestamp}.png"
        
        generated_image_path = os.path.join(base_path, generated_image_filename)
        generated_image.save(generated_image_path)

        return jsonify({'generated_image_path': generated_image_path}), 200

    except KeyError:
        return jsonify({'error': 'Missing image_url or prompt in request body'}), 400

    except Exception as e:
        # Capture the traceback
        error_traceback = traceback.format_exc()
        
        # Create a detailed error response
        error_response = {
            'error': {
                'message': str(e),
                'type': type(e).__name__,
                'traceback': error_traceback
            }
        }
        
        # Return the detailed error response with status code 500
        return jsonify(error_response), 500


@app.route('/')
def index():
    return 'Welcome to the image generation service'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)












# @app.route('/generate_image', methods=['POST'])
# def generate_image():
#     try:
#         # Parse request data (e.g., image URL and prompt)
#         image_url = request.json['image_url']
#         prompt = request.json['prompt']
        
#         # MLSD detector
#         processor = MLSDdetector.from_pretrained('lllyasviel/ControlNet')
#         image = load_image(image_url)
#         control_image = processor(image)

#         # ControlNet
#         checkpoint = "lllyasviel/control_v11p_sd15_mlsd"
#         controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
#         pipe = StableDiffusionControlNetPipeline.from_pretrained(
#             "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
#         )

#         # Getting image back from model
#         pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
#         pipe.enable_model_cpu_offload()

#         generator = torch.manual_seed(0)
#         generated_image = pipe(prompt, num_inference_steps=30, generator=generator, image=control_image).images[0]

#         # Save generated image
#         # generated_image_path = "image_out_web01.png"  # Relative path
#         generated_image_path = r"C:\Users\AhmedHassan.Ali\Downloads\RenderPlus\RenderPlus\BIMRenderPlus.extension\RenderPlus.tab\Tool.panel\ShowWPF.pushbutton\image_out_web01.png"
#         generated_image.save(generated_image_path)

#         return jsonify({'generated_image_path': generated_image_path}), 200

#     except KeyError:
#         return jsonify({'error': 'Missing image_url or prompt in request body'}), 400

#     except Exception as e:
#         return jsonify({'error': str(e)}), 500
 






# checkpoint = "lllyasviel/control_v11p_sd15_mlsd"

# #inputs 
# image = load_image(
#     "https://huggingface.co/lllyasviel/control_v11p_sd15_mlsd/resolve/main/images/input.png"
# )
# prompt = "royal chamber with fancy bed"

# #MLSD dectector
# processor = MLSDdetector.from_pretrained('lllyasviel/ControlNet')
# control_image = processor(image)

# control_image.save(r"C:\Users\AhmedHassan.Ali\Desktop\Render+\results\03\images_room_mlsd_.png")

# #controlnet
# controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
# pipe = StableDiffusionControlNetPipeline.from_pretrained(
#     "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
# )

# try:
#     # getting image back from model 
#     pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
#     pipe.enable_model_cpu_offload()
    
#     generator = torch.manual_seed(0)
#     image = pipe(prompt, num_inference_steps=30, generator=generator, image=control_image).images[0]
#     #save image
#     image.save(r'C:\Users\AhmedHassan.Ali\Desktop\Render+\results\03\image_out_.png')
# except Exception as e:
#     print("An error occurred:", e)















# def generate_image(prompt ,image_url=None):
#     # MLSD detector
#     processor = MLSDdetector.from_pretrained('lllyasviel/ControlNet')
#     image = load_image(
#     "https://huggingface.co/lllyasviel/control_v11p_sd15_mlsd/resolve/main/images/input.png"
#     )

#     # image = load_image(image_url)
#     control_image = processor(image)

#     # ControlNet
#     checkpoint = "lllyasviel/control_v11p_sd15_mlsd"
#     controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
#     pipe = StableDiffusionControlNetPipeline.from_pretrained(
#         "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
#     )

#     try:
#         # Getting image back from model
#         pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
#         pipe.enable_model_cpu_offload()

#         generator = torch.manual_seed(0)
#         generated_image = pipe(prompt, num_inference_steps=30, generator=generator, image=control_image).images[0]

#         return generated_image
#     except Exception as e:
#         print("An error occurred:", e)

# prompt = "royal chamber with fancy bed"
# generated_image = generate_image(prompt)
# generated_image.save(r"C:\Users\AhmedHassan.Ali\Desktop\Render+\results\03\image_out_04.png")






# @app.route('/generate_image', methods=['POST'])
# def generate_image():
#     # Parse request data (e.g., image URL and prompt)
#     image_url = request.json['image_url']
#     prompt = request.json['prompt']
    
#     # MLSD detector
#     processor = MLSDdetector.from_pretrained('lllyasviel/ControlNet')
#     image = load_image(
#     "https://huggingface.co/lllyasviel/control_v11p_sd15_mlsd/resolve/main/images/input.png"
#     )

#     # image = load_image(image_url)
#     control_image = processor(image)

#     # ControlNet
#     checkpoint = "lllyasviel/control_v11p_sd15_mlsd"
#     controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
#     pipe = StableDiffusionControlNetPipeline.from_pretrained(
#         "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
#     )

#     try:
#         # Getting image back from model
#         pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
#         pipe.enable_model_cpu_offload()

#         generator = torch.manual_seed(0)
#         generated_image = pipe(prompt, num_inference_steps=30, generator=generator, image=control_image).images[0]

#         generated_image_path = r"C:\Users\AhmedHassan.Ali\Desktop\Render+\results\03\image_out_web.png"
#         generated_image.save(generated_image_path)

#     except Exception as e:
#         print("An error occurred:", e)

#     return {'generated_image_path': generated_image_path}

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000)














