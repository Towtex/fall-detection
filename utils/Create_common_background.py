import cv2
import sys
import os
import numpy as np

def create_common_background_image(fldPath, condition):
    # cond = 'Camera2_Con1'  # Change Camera and Condition
    imagePath = os.path.join(fldPath, condition, 'RGB')
    maskPath = os.path.join(fldPath, condition, 'Mask')
    file_list = os.listdir(imagePath)
    filename1 = file_list[0]
    filename2 = file_list[1]

    image1 = cv2.imread(os.path.join(imagePath, filename1))
    image1 = cv2.resize(image1, (320, 240))
    image2 = cv2.imread(os.path.join(imagePath, filename2))
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
    # cv2.namedWindow('bg_result')
    cv2.imwrite(os.path.join(os.path.dirname(__file__),'..', 'images', 'common background', f'background_{condition}.png'), bg_result)
    # cv2.imshow('bg_result', bg_result)
    cv2.waitKey(0)

# if __name__ == '__main__':
#     fldPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'UP_Fall_Dataset', 'Common Background Creation'))
#     condition = 'Camera1_Con1'
#     create_common_background_image(fldPath, condition)
