import os
import csv
import requests
import re

# Function to format the image name
def format_image_name(image_url):
    image_name = image_url.split("/")[-1]  # Extract image name from URL
    image_name = image_name.replace("-", "_")  # Replace hyphens with underscores
    
    # Remove numeric ID (e.g., _12345 before .jpg)
    image_name = re.sub(r'_\d+(?=\.jpg)', '', image_name)
    #remove the 5g or 4g from the name
    image_name = re.sub(r'_(5g|4g)(?=\.jpg)', '', image_name)
    
    image_name = image_name.split(".")[0]  # Remove file extension
    formatted_name = "_".join([word.capitalize() for word in image_name.split("_")])  # Capitalize each word
    formatted_name = formatted_name.replace("_", " ")
    return formatted_name + ".jpg"  # Add back the file extension

# Define a function to download images
def download_image(image_url, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    image_name = format_image_name(image_url)  # Format the image name as requested
    image_path = os.path.join(folder_name, image_name)

    # Check if the file already exists
    if os.path.exists(image_path):
        print(f"Skipping {image_name}: File already exists")
        return

    # Download the image
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(image_path, 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {image_name}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download {image_name}: {e}")

# Read the CSV file and download images from URLs
def download_images_from_csv(csv_file, folder_name):
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            image_url = row.get('Image')  # Assuming 'image_url' is the column header
            if image_url:
                download_image(image_url, folder_name)


                

# Function to add "Samsung" prefix if not present and remove "sm_" followed by numbers and letters
# def check_and_add_samsung(folder_path):
#     for filename in os.listdir(folder_path):
#         if filename.endswith(".jpg"):
#             new_filename = filename
#             # Remove "sm_" followed by numbers and letters
#             new_filename = re.sub(r'_Sm_[a-zA-Z0-9]+', '', new_filename)
#             if not new_filename.lower().startswith("samsung"):
#                 new_filename = f"Samsung_{new_filename}"
            
#             if new_filename != filename:
#                 old_file_path = os.path.join(folder_path, filename)
#                 new_file_path = os.path.join(folder_path, new_filename)
                
#                 # Check if the new filename already exists
#                 if os.path.exists(new_file_path):
#                     print(f"Skipping rename: {new_filename} already exists")
#                 else:
#                     os.rename(old_file_path, new_file_path)
#                     print(f"Renamed: {filename} -> {new_filename}")
#             else:
#                 print(f"No changes needed for {filename}")



# Provide the path to your uploaded CSV file
file = input("masukkan nama handphone yang ingin di download: ")

csv_file_path = f'exports/brands_exports/{file}_exports.csv'
folder_name = f"images/{file}"
download_images_from_csv(csv_file_path, folder_name)

# Call the function to add Samsung prefix and remove "sm_" patterns
# check_and_add_samsung(folder_name)
