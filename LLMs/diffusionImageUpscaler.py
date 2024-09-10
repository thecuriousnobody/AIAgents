from diffusers import StableDiffusionInpaintPipeline
import torch
from PIL import Image

device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "runwayml/stable-diffusion-inpainting"
pipe = StableDiffusionInpaintPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
pipe = pipe.to(device)

# Load your local sketch image
sketch_image = Image.open("/Users/rajeevkumar/Downloads/Drawing 135.png")

# Upscale the image
upscaled_image = pipe(image=sketch_image, num_inference_steps=50, guidance_scale=7.5).images[0]

# Enhance the upscaled image to look 3D
enhanced_image = pipe(image=upscaled_image, prompt="A highly detailed, 3D, photorealistic sketch", num_inference_steps=50, guidance_scale=7.5).images[0]

# Save the enhanced image
enhanced_image.save("enhanced_sketch_image_135.jpg")