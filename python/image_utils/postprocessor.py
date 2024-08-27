'''
Author: Zeeshan Randhawa
Date: 5-June-2024
Desc: Utility to porcess the floorplan images generated
'''


from PIL import Image, ImageChops
import numpy as np
import torchvision.transforms as transforms
import torchvision.transforms.functional as TF

class PostProcessor:
    
    def __init__(self):
        self.future = None

    def _white_to_transparency(self, img):
        x = np.asarray(img.convert('RGBA')).copy()
        x[:, :, 3] = (255 * (x[:, :, :3] != 255).any(axis=2)).astype(np.uint8)
        return Image.fromarray(x)
    
    def _tensor_to_pil_image(self, tensor):
        '''Convert PyTorch tensor to PIL Image'''
        transform = transforms.ToPILImage()
        return transform(tensor)
    
    def _pil_image_to_tensor(self, image):
        '''Convert PIL Image to PyTorch tensor'''
        return TF.to_tensor(image)
    
    def _crop_to_content(self, img):
        bg = Image.new(img.mode, img.size, (255, 255, 255, 0))
        diff = ImageChops.difference(img, bg)
        bbox = diff.getbbox()
        if bbox:
            img = img.crop(bbox)
        return img

    def remove_white_background(self, image, transparency=0.7):
        '''
        Removes white background and makes it transparent, also makes the subject translucent
        '''
        if isinstance(image, str):
            img = Image.open(image)
        else:
            img = image.convert("RGBA")  # Ensure image is in RGBA mode
        
        img = self._white_to_transparency(img)
        img.putalpha(img.split()[-1].point(lambda p: p * transparency))  # Make translucent
        img = self._pil_image_to_tensor(img)
        return img
    
    def remove_white_background_after(self, image, transparency=0.7):
        '''
        Removes white background and makes it transparent, also makes the subject translucent
        '''
        if isinstance(image, str):
            img = Image.open(image)
        else:
            img = self._tensor_to_pil_image(image)
        
        img = img.convert("RGBA")
        img = self._white_to_transparency(img)
        img.putalpha(img.split()[-1].point(lambda p: p * transparency))  # Make translucent
        img = self._crop_to_content(img)
        img = self._pil_image_to_tensor(img)
        return img
#Testing - commented    
# postprocessor = PostProcessor()
# input_image_path = r"D:\Floor generator\houseganpp\dump\fp_final_2.png"
# output_image = postprocessor.remove_white_background(input_image_path)
# output_image.show() 
# postprocessor.check_transparency(input_image_path)