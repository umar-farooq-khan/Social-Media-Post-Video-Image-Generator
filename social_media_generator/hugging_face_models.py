import boto3
sts = boto3.client('sts')
print(sts.get_caller_identity())

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="hf-inference",
    api_key="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",
)

# output is a PIL.Image object
image = client.text_to_image(
    "Typical Irish homes in a street of Dublin with a guy riding a horse",
    model="stabilityai/stable-diffusion-3.5-large",
)
image.save("irishhomes.png")

# ✅ Display the image (opens with default image viewer)
image.show()



from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="fal-ai",
    api_key="hf_xxxxxxxxxxxxxxxxxxxxxxxx",
)

video = client.text_to_video(
    "A young man walking on the street",
    model="Lightricks/LTX-Video",
)