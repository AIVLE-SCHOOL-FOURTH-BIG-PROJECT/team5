# imports
# import torch
# import torch.nn as nn
# from torch.utils.data import Dataset, DataLoader
# from contextlib import redirect_stdout
# import os
# import h5py
# import json
# import gc
# import io
# import joblib
# from sklearn.calibration import LabelEncoder
# import matplotlib.pyplot as plt
# from PIL import Image

# from torchvision import transforms
import numpy as np

# def process_image_path(image_path):
#     try:
#         # Open the image file
#         with Image.open(image_path) as img:
#             # Resize and convert to RGB
#             img = img.resize((64, 64)).convert('RGB')
#             # Convert to numpy array and normalize
#             img_array = np.asarray(img) / 255.0
#             # # Transpose the array to have channels first
#             # img_array = img_array.transpose((2, 0, 1))
#             return img_array.reshape(1,-1)
#     except IOError:
#         print(f"Error in processing image: {image_path}")
#         return None

def process_image_file(image_file):
    try:
        # Resize and convert to RGB
        image_file = image_file.resize((64, 64)).convert('RGB')
        # Convert to numpy array and normalize
        img_array = np.asarray(image_file) / 255.0
        # # Transpose the array to have channels first
        # img_array = img_array.transpose((2, 0, 1))
        return img_array.reshape(1,-1)
    except IOError:
        print(f"Error in processing image: {image_file}")
        return None