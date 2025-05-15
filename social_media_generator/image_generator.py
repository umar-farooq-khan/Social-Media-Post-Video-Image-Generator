from openai import OpenAI


# image_prompt = f"""Generate a photorealistic image of a locket for men on a blue background with ripples of ocean,
# labeled 'for this summers' in a handwriting-like font,
# containing the style of the image given as a reference."""

client = OpenAI(api_key='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')

# Generate a new image if no image was uploaded
# result = client.images.generate(
#     model="gpt-image-1",
#     prompt=image_prompt,
#     size="1024x1024",
# )
prompt = """Generate a photorealistic image of similar image which is given as a reference on a white background 
labeled 'Peak Antenna'"""
result = client.images.edit(
    model="gpt-image-1",
    image=open(r"C:\Users\ProBook\Downloads\fuji5g01.png", "rb"),
    prompt=prompt
)


# Get the image URL from the response
#generated_image_url = result.data[0].url
from openai import OpenAI
import base64
image_base64 = result.data[0].b64_json
image_bytes = base64.b64decode(image_base64)

# Save the image to a file
with open("similarimage_antenna.png", "wb") as f:
    f.write(image_bytes)
