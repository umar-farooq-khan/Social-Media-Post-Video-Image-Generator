import os
import json
import base64
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import openai
from PIL import Image
import requests
from io import BytesIO
import time
import pdb
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores.faiss import FAISS
from dotenv import load_dotenv
from pypdf import PdfReader
import tempfile

# Load environment variables
load_dotenv()

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def index(request):
    return render(request, 'generator/index.html')



def generate_post(request):
    competitors_posts = '''1. "Satellite technology has come a long way and is now a big part of our everyday lives. Many fundamental concepts apply to all satellite constellations. Understanding these basics is a great first step in choosing the right antenna, radio module, and other components for devices that rely on satellite connectivity - like autonomous vehicles, fitness wearables, asset trackers, and more. Check out our latest engineering blog: "How Satellite Communication Works: Key Concepts, Technologies, and Business Opportunities" to learn more 👉 ​https://bit.ly/3YWcI7d hashtag#SatelliteTech hashtag#CellularTechnology hashtag#5G hashtag#IoT hashtag#MobileNetworks. Check out our latest engineering blog: "How Satellite Communication Works: Key Concepts, Technologies, and Business Opportunities" to learn more"
               2. "Dive into the features of our new flex PCB FXUB06 & FXUB16 Antennas with David Connolly, Global Product Management Director. These antennas are designed to meet the demands of next-gen Cellular & IoT devices where space is tight, but performance can't be compromised! Want to see more? Check out their datasheets at the following links: https://bit.ly/3EycjRB  #4G hashtag#LTE # CellularTech hashtag#5G"
               3. "Every generation aspires to outdo its ancestors. That's true for both people and cellular technologies. In our latest engineering blog, we break down the key differences between 4G, LTE, and 5G and examine how mobile technology continues to evolve. Dive in here 👉 ​https://bit.ly/4iJv4j1 hashtag#4G hashtag#LTE hashtag#CellularTech hashtag#5G
               '''
    
    # Get form data from request
    business_details = json.loads(request.POST.get('business_details', '{}'))
    business_name = business_details.get('name', 'Peak Antenna')
    business_description = business_details.get('description', '')
    industry = business_details.get('industry', '')
    
    # Get other form fields
    tone = request.POST.get('tone', 'Professional, Linkedin styled')
    style = request.POST.get('style', 'Showing confidence and professionalism leave a magnet post')
    post_topic = request.POST.get('post_topic', '')
    
    prompt = f"""
    Create a social media post for a business with the following details with a similar tone and style of competitors posts:
    Business Name: {business_name}
    Business Description: {business_description}
    Industry: {industry}
    Post Topic: {post_topic}
    Tone: {tone}
    Style: {style}
    Competitors Posts: {competitors_posts}
    """

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a social media marketing expert."},
            {"role": "user", "content": prompt}
        ]
    )

    generated_text = response.choices[0].message.content
    return generated_text



def ask_chatgpt(prompt):

    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful bot."},
            {"role": "user", "content": prompt}
        ]
    )

    generated_text = response.choices[0].message.content
    return generated_text
@csrf_exempt
def generate_content(request):
    if request.method == 'POST':
        try:
            uploaded_images = request.FILES.getlist('images')
            # Process images
            processed_images = []
            for image in uploaded_images:
                try:
                    # Convert the uploaded file to a BytesIO object
                    image_data = BytesIO(image.read())
                    img = Image.open(image_data)
                    processed_images.append(img)
                except Exception as e:
                    print(f"Error processing image: {str(e)}")
                    continue

            # Generate post text using ChatGPT
            generated_text = generate_post(request)
            industry = ask_chatgpt('Just output the Industry or wider category from this post: '+ generated_text + 'Dont output anything else')
            print('Industry Detected' , industry)
            
            # Get custom image prompt if provided, otherwise use default
            custom_image_prompt = request.POST.get('image_prompt', '')
            if custom_image_prompt:
                image_prompt = custom_image_prompt
            else:
                image_prompt = f"""Generate a photorealistic photo of two people handshaking related to {industry} for the linkedIn post
                Here are more details about the post: {generated_text[:100]}"""

            try:
                if uploaded_images:
                    # Use the first uploaded image
                    print("Reference image uploaded")
                    try:
                        # Convert the uploaded file to a BytesIO object
                        image_file = uploaded_images[0]
                        image_data = BytesIO(image_file.read())
                        image_data.seek(0)  # Reset the file pointer
                        
                        result = client.images.edit(
                            model="gpt-image-1",
                            image=image_data,
                            prompt=image_prompt,
                            n=1,
                            size="1024x1024"
                        )
                    except Exception as e:
                        print(f"Error processing uploaded image: {str(e)}")
                        print('Falling back to generating new image')
                        result = client.images.generate(
                            model="gpt-image-1",
                            prompt=image_prompt,
                            size="1024x1024",
                        )
                else:
                    # Generate new image without reference
                    print("Generating new image without reference")
                    result = client.images.generate(
                        model="dall-e-3",
                        prompt=image_prompt,
                        size="1024x1024",
                    )

                # Get the image URL from the response
                generated_image_url = result.data[0].url
                print(f"Generated image URL: {generated_image_url}")

                return JsonResponse({
                    'status': 'success',
                    'generated_text': generated_text,
                    'generated_image_url': generated_image_url
                })

            except Exception as e:
                print(f"Error in image generation: {str(e)}")
                # Return response without image URL if image generation fails
                return JsonResponse({
                    'status': 'success',
                    'generated_text': generated_text,
                    'generated_image_url': None
                })

        except Exception as e:
            print(f"Error in generate_content: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

@csrf_exempt
def generate_custom_content(request):
    if request.method == 'POST':
        try:
            # Get form data
            tone = request.POST.get('tone', '')
            style = request.POST.get('style', '')
            business_name= request.POST.get('businessName', '')
            business_details= request.POST.get('businessDescription', '')
            custom_prompt = request.POST.get('customPrompt', '')
            pdf_file = request.FILES.get('pdf_document')
            
            # Process images
            processed_images = []

            # Prepare the raw text from business details and custom prompt
            raw_text = f"""
            Business Name: {business_name}
            Business Description: {business_details}
            Custom Requirements: {custom_prompt}
            """

            # Process PDF if uploaded
            if pdf_file:
                # Save PDF to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_pdf:
                    for chunk in pdf_file.chunks():
                        temp_pdf.write(chunk)
                    temp_pdf_path = temp_pdf.name

                try:
                    # Read PDF content
                    pdf_reader = PdfReader(temp_pdf_path)
                    pdf_text = ""
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text() + "\n"
                    
                    # Add PDF content to raw text
                    raw_text += f"\nAdditional Context from PDF:\n{pdf_text}"
                finally:
                    # Clean up temporary file
                    os.unlink(temp_pdf_path)

            # Split the text using Character Text Splitter
            try:
                text_splitter = CharacterTextSplitter(
                    separator="\n",
                    chunk_size=800,
                    chunk_overlap=200,
                    length_function=len,
                )
                texts = text_splitter.split_text(raw_text)

                # Create embeddings and vector store
                embeddings = OpenAIEmbeddings()
                document_search = FAISS.from_texts(texts, embeddings)

                # Search for relevant context
                relevant_docs = document_search.similarity_search(custom_prompt, k=3)
                context = "\n".join([doc.page_content for doc in relevant_docs])
                print('context', context)
            except Exception as e:
                print(f"Error in RAG processing: {str(e)}")
                context = raw_text  # Fallback to using raw text if RAG fails

            # Generate post text using ChatGPT with RAG context
            prompt = f"""
            Create a linkedIn post for a business with the following details:
            
            Context from business information and uploaded document:
            {context}
            
            Additional Requirements:
            Tone: {tone}
            Style: {style}
            Custom Requirements: {custom_prompt}
            Please create a post that matches the specified tone and style while incorporating the custom requirements and relevant context from both the business information and any uploaded document.
            """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a social media marketing expert."},
                    {"role": "user", "content": prompt}
                ]
            )

            generated_text = response.choices[0].message.content
            print(f"Generated text: {generated_text}")  # Debug print
            #
            # # Generate image based on the generated text
            # image_prompt = f"""Create a professional business image that represents: {generated_text[:200]}"""
            #
            # try:
            #     # Generate a new image using DALL-E
            #     image_response = openai.images.generate(
            #         model="dall-e-3",
            #         prompt=image_prompt,
            #         size="1024x1024",
            #         quality="standard",
            #         n=1,
            #     )
            #     generated_image_url = image_response.data[0].url
            #     print(f"Generated image URL: {generated_image_url}")  # Debug print
            # except Exception as e:
            #     print(f"Error generating image: {str(e)}")
            #     generated_image_url = None

            return JsonResponse({
                'status': 'success',
                'generated_text': generated_text
                # 'generated_image_url': generated_image_url
            })

        except Exception as e:
            print(f"Error in generate_custom_content: {str(e)}")  # Debug print
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def custom_prompt(request):
    return render(request, 'generator/custom_prompt.html')

def reference_image_generator(request):
    return render(request, 'generator/reference_image.html')

@csrf_exempt
def generate_reference_image(request):
    if request.method == 'POST':
        try:
            # Get the reference image and description
            reference_image = request.FILES.get('referenceImage')
            image_description = request.POST.get('imageDescription')

            if not reference_image:
                print('no refernece image')
                return JsonResponse({
                    'status': 'error',
                    'message': 'No reference image provided'
                }, status=400)

            try:
                # Read the uploaded file
                image_data = BytesIO(reference_image.read())
                image_data.seek(0)

                # Open and process the image
                img = Image.open(image_data)
                
                # Convert to RGB if image is in RGBA mode
                if img.mode == 'RGBA':
                    img = img.convert('RGB')
                
                # Create a new BytesIO object for the PNG
                png_data = BytesIO()
                
                # Save as PNG
                img.save(png_data, format='PNG')
                png_data.seek(0)

                # Create a temporary file to ensure proper MIME type
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_file.write(png_data.getvalue())
                    temp_file.flush()
                    
                    # Open the temporary file in binary mode
                    with open(temp_file.name, 'rb') as image_file:
                        # Generate image using DALL-E
                        result = client.images.edit(
                            model="gpt-image-1",
                            image=image_file,
                            prompt=f"""Generate a photorealistic image of similar image which is given as a reference on a white background. 
                            Additional requirements: {image_description}"""
                        )

                # Clean up the temporary file
                os.unlink(temp_file.name)

                # Get the base64 image data
                image_base64 = result.data[0].b64_json
                image_bytes = base64.b64decode(image_base64)

                # Generate a unique filename
                timestamp = int(time.time())
                output_filename = f"generated_image_{timestamp}.png"
                output_path = os.path.join(settings.MEDIA_ROOT, 'generated_images', output_filename)

                # Ensure the directory exists
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                # Save the image to a file
                with open(output_path, "wb") as f:
                    f.write(image_bytes)

                # Get the URL for the saved image
                image_url = f"/media/generated_images/{output_filename}"

                return JsonResponse({
                    'status': 'success',
                    'generated_image_url': image_url
                })

            except Exception as e:

                print(f"Error in image generation: {str(e)}")
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error generating image: {str(e)}'
                }, status=500)

        except Exception as e:
            print(f"Error in generate_reference_image: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)

def healthcheck(request):
    return JsonResponse({'status': 'ok'})


#git pull
#sudo docker compose build
#sudo docker compose up -d