import os
import numpy as np
from PIL import Image
from patchify import patchify
import argparse
from tqdm import tqdm

# Avoid DecompressionBombWarning
Image.MAX_IMAGE_PIXELS = 145500000

class Split:

    def __init__(self, input_folder, output_folder, split_size, step, type):
        self.input_folder_ = input_folder
        self.output_folder_ = output_folder
        self.split_size_ = split_size
        self.step_ = step
        self.type_ = type
        
    def process(self):
        if self.type_ == 'image':
            self.split_images()
        elif self.type_ == 'mask':
            self.split_masks()

    def split_masks(self):
        for filename in tqdm(os.listdir(self.input_folder_), desc='Splitting masks'):
            file_path = os.path.join(self.input_folder_, filename)

            mask_array = np.load(file_path)

            # Ensure the output folder exists
            if not os.path.exists(self.output_folder_):
                os.makedirs(self.output_folder_)

            # Split the input array into patches
            patches = patchify(mask_array, (self.split_size_,self.split_size_), step=self.step_)

            identifier = 0
            # Save each patch to the output folder
            for i in range(patches.shape[0]):
                for j in range(patches.shape[1]):
                    patch = patches[i, j] 
                    if np.any(patch == 1):
                        patch_image = Image.fromarray((patch * 255).astype(np.uint8))
                        output_path = os.path.join(self.output_folder_, f"{filename.split('.')[0]}_split_{identifier}.png")
                        identifier += 1
                        patch_image.save(output_path)

    def split_images(self):
       for filename in tqdm(os.listdir(self.input_folder_), desc='Splitting masks'):
            file_path = os.path.join(self.input_folder_, filename)

            image_array = np.array(Image.open(file_path))

            # Ensure the output folder exists
            if not os.path.exists(self.output_folder_):
                os.makedirs(self.output_folder_)
        
            # Split the input array into patches
            patches = patchify(image_array, (self.split_size_,self.split_size_, 3), step=self.step_)

            identifier = 0
            # Save each patch to the output folder
            for i in range(patches.shape[0]):
                for j in range(patches.shape[1]):
                    patch = patches[i, j, 0, :, :, :] 
                    patch_image = Image.fromarray(patch)
                    output_path = os.path.join(self.output_folder_, f"{filename.split('.')[0]}_split_{identifier}.png")
                    identifier += 1
                    patch_image.save(output_path)

def main():
    parser = argparse.ArgumentParser(description='Split images and masks into patches.')
    parser.add_argument('--input-folder', type=str, help='Path to the folder containing input images (TIFF format) or binary masks (NumPy format).')
    parser.add_argument('--output-folder', type=str, help='Path to the folder where patches will be saved.')
    parser.add_argument('--patch-size', type=int, help='Size of the patches.')
    parser.add_argument('--step', type=int, help='Overlap between patches. (If step=patch_size, there is no overlap.)')
    parser.add_argument('--type', type=str, help='Type of data to split (images or masks).' )
    args = parser.parse_args()

    input_folder = args.input_folder
    output_folder = args.output_folder
    patch_size = args.patch_size
    step = args.step
    type = args.type

    split = Split(input_folder, output_folder, patch_size, step, type)

    split.process()

if __name__ == "__main__":
    main()