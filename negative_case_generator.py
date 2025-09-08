import os
import random
from PIL import Image


# Function to create an image grid of 15 random cards (5 in a row, 3 rows) and resize it to 640x640
def create_card_grid(card_folder_path, output_folder_path, card_size=(600, 838), grid_size=640, iterations=5000):
    # Load all the card images from the folder
    card_images = []
    for filename in os.listdir(card_folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(card_folder_path, filename)
            card_image = Image.open(image_path)
            card_images.append(card_image)

    # Ensure there are enough cards in the folder
    if len(card_images) < 15:
        print("Error: The folder must contain at least 15 cards.")
        return

    # Perform the image creation process 5000 times
    for i in range(iterations):
        # Select 15 random cards
        random_cards = random.sample(card_images, 15)

        # Create a new blank image to hold the grid (5 cards in each row, 3 rows)
        grid_width = card_size[0] * 5  # 5 cards in a row
        grid_height = card_size[1] * 3  # 3 rows
        grid_image = Image.new('RGB', (grid_width, grid_height))

        # Place the random cards in the grid
        card_index = 0
        for row in range(3):
            for col in range(5):
                card_image = random_cards[card_index]
                grid_image.paste(card_image, (col * card_size[0], row * card_size[1]))
                card_index += 1

        # Resize the final image to 640x640 using the LANCZOS filter (formerly ANTIALIAS)
        grid_image = grid_image.resize((grid_size, grid_size), Image.LANCZOS)

        # Save the final image with a unique filename
        output_image_path = os.path.join(output_folder_path, f"grid_image_{i + 1}.png")
        grid_image.save(output_image_path)
        print(f"Image {i + 1} saved to {output_image_path}")


# Path to the folder with card images and the output path for the final image
card_folder = 'downloaded_cards'  # Replace with your folder path
output_path = 'datasets\\images\\all'  # Replace with desired output path

# Perform the process 5000 times
create_card_grid(card_folder, output_path, iterations=5000)
