# 02-1.
# for Amazon image data
# This Python file is intended to extract colors(3) and percentages from Amazon data!!!!
# used: cuML for KMeans
# with 'nugi'

# Frequency of each cluster(n=3)
import pandas as pd
import os
import numpy as np
from PIL import Image
import requests
from io import BytesIO
from cuml.cluster import KMeans
# from sklearn.cluster import KMeans

def remove_background(img):
    # Convert the image to RGBA (if it's not already in that mode)
    img = img.convert("RGBA")
    datas = img.getdata()

    newData = []
    for item in datas:
        # Change all white (also shades of whites)
        # pixels to transparent
        if item[0] > 220 and item[1] > 220 and item[2] > 220:  # Finding white-ish pixels
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)

    img.putdata(newData)
    return img

def extract_ordered_dominant_colors_gpu(image_url, num_colors):
    # Load image from the web URL
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))

    # Remove the background of the image
    image = remove_background(image)

    image = np.array(image) / 255.0  # Normalize the image

    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 4)  # Changed to 4 because the image is now RGBA

    # Remove all transparent/white pixels (alpha=0)
    pixels = pixels[pixels[:, 3] > 0][:, :3]  # Removing the alpha channel and transparent pixels

    # Use KMeans to find main colors
    model = KMeans(n_clusters=num_colors)
    model.fit(pixels)
    
    # Get the colors and labels
    colors = model.cluster_centers_
    labels = model.labels_
    
    # Count labels to find the frequency of each cluster
    count_labels = np.bincount(labels, minlength=num_colors)
    total_pixels = len(pixels)
    
    # Calculate the percentage of each cluster
    percentages = 100 * count_labels / total_pixels
    percentages_rounded = np.round(percentages, 2)  # Round to 2 decimal places
    
    # Order the clusters by their frequency (most common first)
    ordered_indices = np.argsort(count_labels)[::-1]  # Descending order
    ordered_colors = colors[ordered_indices]
    ordered_percentages = percentages_rounded[ordered_indices]
    
    return ordered_colors, ordered_percentages


names = [
    'Sectional_Sofas', 'Sleeper_Sofas', 
        'Reclining_Sofas', 
        'LoveSeats', 'Futons', 'Settles', 'Convertibles', 
         'Accent_Chairs', 'Coffee_Tables', 'TV_Stands', 'End_Tables', 'Console_Tables', 'Ottomans', 'Living_Room_Sets', 
         'Decorative_Pillows', 'Throw_Blankets', 'Area_Rugs', 'Wall_Arts', 'Table_Lamps', 'Floor_Lamps', 
         'Pendants_and_Chandeliers', 'Sconces', 'Baskets_and_Storage', 'Candles', 'Live_Plants', 'Artificial_Plants', 
         'Planters', 'Decorative_Accessories', 'Window_Coverings', 'Decorative_Mirrors', 'Dining_Sets', 
         'Dining_Tables', 'Dining_Chairs', 'Bar_Stools', 'Kitchen_Islands', 'Buffets_and_Sideboards', 'China_Cabinets', 
         'Bakers_Recks', 'Bedroom_Sets', 'Mattresses', 'Nightstands', 'Dressers', 'Beds', 'Bedframes', 'Bases', 'Vanities', 
         'Entryway_Furnitures', 'Desks', 'Desk_Chairs', 'Bookcases', 
         'File_Cabinets', 'Computer_Armoires', 'Drafting_Tables', 'Cabinets', 'Furniture_Sets'
         ]



from multiprocessing import Pool
import pandas as pd
import os
import csv

# Set file paths
infos_path = '/home/all/product_infos/'
colors_path = '/home/all/product_infos_colors_nugi/'

def process_row(row):
    index = row.name
    image_path = row.get('Img_URL')  # Get the image path

    if not image_path:
        print(f"No image path for row {index}. Skipping.")
        return None, None
    else:
        try:
            # Extract dominant colors
            rgb_colors, rgb_percentages = extract_ordered_dominant_colors_gpu(image_path, num_colors=3)
            return rgb_colors, rgb_percentages
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None, None

def add_dominant_color_info(infos_path, colors_path, name):
    infos_file = os.path.join(infos_path, f'{name}_product_infos.csv')
    output_file = os.path.join(colors_path, f'{name}_product_infos_with_colors.csv')

    if os.path.exists(infos_file):
        # Read the input CSV file
        infos_csv = pd.read_csv(infos_file)

        total_items = len(infos_csv)
        
        # Check if 'RGB_3colors' and 'RGB_percentages' columns already exist
        if 'RGB_3colors' in infos_csv.columns and 'RGB_percentages' in infos_csv.columns:
            print(f"'RGB_3colors' and 'RGB_percentages' columns already exist in {infos_file}. Skipping.")
            return

        # Calculate the number of workers (total cores - 2)
        num_workers = max(1, os.cpu_count() - 2)  # Ensure at least one worker is used

        # Set up a pool of workers to process rows in parallel
        with Pool(num_workers) as pool:
            results = pool.map(process_row, [row for _, row in infos_csv.iterrows()])
            
        # Write results to the output CSV file
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(list(infos_csv.columns) + ['RGB_3colors', 'RGB_percentages'])
            
            # Output the progress for each product
            for index, (row, (colors, percentages)) in enumerate(zip(infos_csv.iterrows(), results)):
                # Calculate the progress
                progress = (index + 1) / total_items * 100
                # Print the current progress
                print(f"Processing item {index + 1}/{total_items} ({progress:.2f}%)")
                writer.writerow(list(row[1]) + [str(colors), str(percentages)])
            
            
            for row, (colors, percentages) in zip(infos_csv.iterrows(), results):
                writer.writerow(list(row[1]) + [str(colors), str(percentages)])
    else:
        print(f"{infos_file} does not exist. Skipping.")

if __name__ == "__main__":
    for name in names:
        add_dominant_color_info(infos_path, colors_path, name)
