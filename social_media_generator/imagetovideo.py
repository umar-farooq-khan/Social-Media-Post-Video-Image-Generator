from diffusers import StableVideoDiffusionPipeline
from PIL import Image
import torch

# Load the pipeline
pipe = StableVideoDiffusionPipeline.from_pretrained(
    "stabilityai/stable-video-diffusion-img2vid-xt",
    torch_dtype=torch.float16
)  # Use "cpu" if no GPU available, but slower

# Load an image (RGB and 1024x576 recommended)
image = Image.open(r"C:\Users\ProBook\Downloads\denaliwifi01.png").convert("RGB").resize((1024, 576))

# Run the pipeline (returns a list of PIL.Image frames)
frames = pipe(image, num_frames=14, motion_bucket_id=127, noise_aug_strength=0.02).frames[0]

# Save as video or GIF
frames[0].save("output.gif", save_all=True, append_images=frames[1:], duration=80, loop=0)
