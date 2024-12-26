import cv2
import os
import numpy as np


def create_common_background_image(fld_path: str, condition: str):
    image_path = os.path.join(fld_path, condition, 'RGB')
    maskPath = os.path.join(fld_path, condition, 'Mask')
    file_list = os.listdir(image_path)
    filename1 = file_list[0]
    filename2 = file_list[1]

    image1 = cv2.imread(os.path.join(image_path, filename1))
    image1 = cv2.resize(image1, (320, 240))
    image2 = cv2.imread(os.path.join(image_path, filename2))
    image2 = cv2.resize(image2, (320, 240))
    mask0 = cv2.imread(os.path.join(maskPath, filename1))
    mask0 = cv2.resize(mask0, (320, 240))

    kernel = np.ones((3, 3), np.uint8)
    # img_erosion = cv2.erode(mask0, kernel, iterations=1)
    mask1 = cv2.dilate(mask0, kernel, iterations=1)

    thresh = 128
    im_bool1 = mask1 >= thresh
    im_bool2 = mask1 < thresh

    image3 = image1 * im_bool2
    image4 = image2 * im_bool1

    data2 = im_bool2 * 255
    mask2 = data2.astype(np.uint8)

    bg_result = image3 + image4
    path = os.path.join(
        os.path.dirname(__file__),
        '..',
        '..',
        'output',
        'common background creation',
        f'background_{condition}.png'
    )
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    cv2.imwrite(path, bg_result)
    # cv2.imshow('bg_result', bg_result)
    cv2.waitKey(0)
