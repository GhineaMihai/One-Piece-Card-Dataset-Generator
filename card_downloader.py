import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO

# URL of the webpage containing the card images
base_url = "https://onepiece.limitlesstcg.com"
page_url = urljoin(base_url, "/cards/op11-a-fist-of-divine-speed")

# Directory to save the downloaded images
output_dir = "cards"
os.makedirs(output_dir, exist_ok=True)


# Function to download and convert image to PNG
def download_and_convert_image(image_url, save_path):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        # Open the image from the response content
        img = Image.open(BytesIO(response.content))

        # Save the image as PNG
        img.save(save_path, 'PNG')
        print(f"Downloaded and converted: {save_path}")
    except Exception as e:
        print(f"Failed to download or convert {image_url}: {e}")


# Fetch the webpage content
response = requests.get(page_url)
response.raise_for_status()

# Parse the webpage content
soup = BeautifulSoup(response.text, 'html.parser')

# Find all image tags with the class 'card-image'
image_tags = soup.find_all('img', class_='card shadow')

# Extract and download each image
for img_tag in image_tags:
    img_src = img_tag.get('src')

    if img_src:
        # Construct the full image URL
        img_url = urljoin(base_url, img_src)

        # Extract the image filename (change extension to .png)
        img_name = os.path.splitext(os.path.basename(img_src))[0] + '.png'

        # Set the save path
        save_path = os.path.join(output_dir, img_name)

        # Download and convert the image to PNG
        download_and_convert_image(img_url, save_path)

print("All images downloaded and converted to PNG.")
