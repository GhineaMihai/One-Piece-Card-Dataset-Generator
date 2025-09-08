import os
import random
import cv2
import numpy as np

# Set paths
CARD_PATH = "cards/"  # Folder containing card images
BACKGROUND_PATH = "backgrounds/"  # Folder containing background images
OUTPUT_PATH = "datasets/images/all/"  # Folder to save augmented images
ANNOTATION_PATH = "datasets/labels/all/"  # Folder to save bounding box annotations

# Create directories if they don’t exist
os.makedirs(OUTPUT_PATH, exist_ok=True)
os.makedirs(ANNOTATION_PATH, exist_ok=True)

# Parameters
NUM_IMAGES_PER_CARD = 500  # Number of augmented images per card
BG_WIDTH, BG_HEIGHT = 640, 640  # Background size
CARD_ASPECT_RATIO = 600 / 838  # Maintain aspect ratio of original cards
MAX_CARD_HEIGHT = 350  # Maximum height for resized cards


# Load images from folder
def load_images_from_folder(folder):
    return [os.path.join(folder, filename) for filename in os.listdir(folder) if
            filename.endswith((".png", ".jpg", ".jpeg"))]


cards = load_images_from_folder(CARD_PATH)
backgrounds = load_images_from_folder(BACKGROUND_PATH)

if not cards:
    raise FileNotFoundError("No card images found in the specified card folder!")


# Function to resize card while keeping aspect ratio
def resize_card(card_img):
    scale_factor = random.uniform(0.4, 1.0)  # Randomly scale between 70% and 100%
    height = int(MAX_CARD_HEIGHT * scale_factor)
    width = int(height * CARD_ASPECT_RATIO)
    return cv2.resize(card_img, (width, height), interpolation=cv2.INTER_AREA), width, height

# Function to rotate an image while keeping bounding box updated
def rotate_image_and_bbox(image, angle):
    """Rotates the image and updates the bounding box correctly"""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1)

    # Compute new bounding box coordinates after rotation
    cos = np.abs(rotation_matrix[0, 0])
    sin = np.abs(rotation_matrix[0, 1])

    new_w = int((h * sin) + (w * cos))
    new_h = int((h * cos) + (w * sin))

    # Adjust rotation matrix
    rotation_matrix[0, 2] += (new_w / 2) - center[0]
    rotation_matrix[1, 2] += (new_h / 2) - center[1]

    rotated_image = cv2.warpAffine(image, rotation_matrix, (new_w, new_h), borderMode=cv2.BORDER_CONSTANT,
                                   borderValue=(0, 0, 0, 0))

    return rotated_image


# Function to overlay card on background
def overlay_card_on_background(card_img, background_img):
    """Overlays a card on a random position of the background"""
    background_img = cv2.resize(background_img, (BG_WIDTH, BG_HEIGHT), interpolation=cv2.INTER_AREA)

    card_height, card_width = card_img.shape[:2]
    x_offset = random.randint(0, BG_WIDTH - card_width)
    y_offset = random.randint(0, BG_HEIGHT - card_height)

    overlay = background_img.copy()
    card_alpha = card_img[:, :, 3] / 255.0 if card_img.shape[-1] == 4 else np.ones_like(card_img[:, :, 0])

    for c in range(3):
        overlay[y_offset:y_offset + card_height, x_offset:x_offset + card_width, c] = (
                card_alpha * card_img[:, :, c] +
                (1 - card_alpha) * background_img[y_offset:y_offset + card_height, x_offset:x_offset + card_width, c]
        )

    return overlay, (x_offset, y_offset, x_offset + card_width, y_offset + card_height)


# Function to apply realistic effects
def apply_realistic_effects(image):
    """Applies post-processing augmentations to make the image look real"""
    if random.random() < 0.5:
        image = cv2.GaussianBlur(image, (5, 5), 0)  # Slight blur

    if random.random() < 0.3:
        motion_blur_kernel = np.zeros((5, 5))
        motion_blur_kernel[random.randint(0, 4), :] = 1
        motion_blur_kernel /= 5
        image = cv2.filter2D(image, -1, motion_blur_kernel)

    if random.random() < 0.4:
        factor = random.uniform(0.7, 1.3)
        image = np.clip(image * factor, 0, 255).astype(np.uint8)

    if random.random() < 0.3:
        noise = np.random.normal(0, 2, image.shape)
        image = image + noise

    return image


# Function to save YOLO annotations
def save_annotations(card_id_count, filename, bbox):
    """Saves bounding box in YOLO format"""
    x_min, y_min, x_max, y_max = bbox

    x_center = (x_min + x_max) / 2 / BG_WIDTH
    y_center = (y_min + y_max) / 2 / BG_HEIGHT
    width = (x_max - x_min) / BG_WIDTH
    height = (y_max - y_min) / BG_HEIGHT

    with open(filename, "w") as f:
        f.write(f"{card_id_count} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")  # Class 0 = card

card_id_count = 0

# Generate augmented images
for card_path in cards:
    card_name = os.path.splitext(os.path.basename(card_path))[0]
    card = cv2.imread(card_path, cv2.IMREAD_UNCHANGED)

    card_output_path = OUTPUT_PATH

    annotation_output_path = ANNOTATION_PATH

    for i in range(NUM_IMAGES_PER_CARD):
        background = cv2.imread(random.choice(backgrounds), cv2.IMREAD_UNCHANGED) if backgrounds else np.zeros(
            (BG_WIDTH, BG_HEIGHT, 3), dtype=np.uint8)

        resized_card, card_width, card_height = resize_card(card)

        # Apply random rotation
        rotation_angle = random.uniform(-30, 30)  # Rotate randomly between -30 and +30 degrees
        rotated_card = rotate_image_and_bbox(resized_card, rotation_angle)

        # Overlay rotated card on background
        final_image, bbox = overlay_card_on_background(rotated_card, background)

        # Apply realistic augmentations
        final_image = apply_realistic_effects(final_image)

        output_file = os.path.join(card_output_path, f"{card_name}_{i + 1}.png")
        annotation_file = os.path.join(annotation_output_path, f"{card_name}_{i + 1}.txt")

        cv2.imwrite(output_file, final_image)
        save_annotations(card_id_count, annotation_file, bbox)

        print(f"Generated {output_file} with annotation {annotation_file}")

    card_id_count += 1

print(f"Generated {NUM_IMAGES_PER_CARD} augmented images per card in '{OUTPUT_PATH}'")
