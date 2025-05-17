import requests
from bs4 import BeautifulSoup

def scrape_meme_image():
    url = "https://imgflip.com/memegenerator/184152522/Oh-yeah-Oh-no"
    
    # Add headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Debug: Print all image tags and their classes
        print("Searching for images...")
        all_images = soup.find_all('img')
        print(f"Total images found: {len(all_images)}")
        
        for img in all_images:
            print(f"Image classes: {img.get('class', 'No class')}")
            print(f"Image src: {img.get('src', 'No src')}")
            print("---")
        
        # Find the image with classes 'im' and 'um'
        meme_image = soup.find('img', class_=['im', 'um'])
        
        if meme_image and meme_image.get('src'):
            # Get the image URL and ensure it has https
            image_url = meme_image['src']
            if image_url.startswith('//'):
                image_url = f"https:{image_url}"
            
            print(f"Found meme image URL: {image_url}")
            return image_url
        else:
            print("No meme image found with classes 'im' and 'um'")
            return None
            
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    meme_url = scrape_meme_image()
    if meme_url:
        # You can download the image if needed
        try:
            response = requests.get(meme_url)
            response.raise_for_status()
            with open('meme.jpg', 'wb') as f:
                f.write(response.content)
            print("Meme image downloaded successfully as 'meme.jpg'")
        except Exception as e:
            print(f"Error downloading the image: {e}")
