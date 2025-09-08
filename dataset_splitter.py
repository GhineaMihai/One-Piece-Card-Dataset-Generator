import os
import random
import shutil

# Define paths
dataset_path = "datasets"
image_folder = os.path.join(dataset_path, "images/all")
label_folder = os.path.join(dataset_path, "labels/all")

train_image_folder = os.path.join(dataset_path, "images/train")
val_image_folder = os.path.join(dataset_path, "images/val")

train_label_folder = os.path.join(dataset_path, "labels/train")
val_label_folder = os.path.join(dataset_path, "labels/val")

# Create folders if they don't exist
for folder in [
    train_image_folder, val_image_folder,
    train_label_folder, val_label_folder
]:
    os.makedirs(folder, exist_ok=True)

# Get all image files
image_files = [f for f in os.listdir(image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]

# Shuffle images
random.shuffle(image_files)

# Define split percentages
train_split = 0.8  # 80% training
val_split = 0.2    # 10% validation

# Compute split indices
num_images = len(image_files)
train_index = int(num_images * train_split)
val_index = train_index + int(num_images * val_split)

# Split dataset
train_images = image_files[:train_index]
val_images = image_files[train_index:val_index]

# Function to move images and labels
def move_files(image_list, dest_img_folder, dest_label_folder):
    for img_file in image_list:
        img_path = os.path.join(image_folder, img_file)
        label_path = os.path.join(label_folder, img_file.replace(".png", ".txt").replace(".jpg", ".txt").replace(".jpeg", ".txt"))

        # Move image
        shutil.move(img_path, os.path.join(dest_img_folder, img_file))

        # Move corresponding label if exists
        if os.path.exists(label_path):
            shutil.move(label_path, os.path.join(dest_label_folder, os.path.basename(label_path)))

# Move files
move_files(train_images, train_image_folder, train_label_folder)
move_files(val_images, val_image_folder, val_label_folder)

print(f"✅ Dataset split complete! {len(train_images)} train, {len(val_images)} val images.")
