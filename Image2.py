
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

# MLSD detector
processor = MLSDdetector.from_pretrained('lllyasviel/ControlNet')
image = load_image(
"https://huggingface.co/lllyasviel/control_v11p_sd15_mlsd/resolve/main/images/input.png"
)
prompt = "royal chamber with fancy bed"


control_image = processor(image)
# ControlNet
checkpoint = "lllyasviel/control_v11p_sd15_mlsd"
controlnet = ControlNetModel.from_pretrained(checkpoint, torch_dtype=torch.float16)
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", controlnet=controlnet, torch_dtype=torch.float16
)
try:
    # Getting image back from model
    pipe.scheduler = UniPCMultistepScheduler.from_config(pipe.scheduler.config)
    pipe.enable_model_cpu_offload()
    generator = torch.manual_seed(0)
    generated_image = pipe(prompt, num_inference_steps=30, generator=generator, image=control_image).images[0]
    
    # Get the directory of the current Python script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the relative path for the generated image
    relative_path = os.path.join(current_dir, "image_out_locall__.png")
    generated_image.save(relative_path)
    
except Exception as e:
    print("An error occurred:", e)