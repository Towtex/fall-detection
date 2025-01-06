import numpy as np
import cv2 
import os
import shutil
import time
from utils.images_to_video import images_to_video

def bwaeraopen(image, size):
    output = image
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
    for i in range(1, nlabels):
        region_size = stats[i, 4]
        if region_size < size:
            output[labels == i] = 0
    return output

def take_max_obj(image):
    output = image
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
    all_size = stats[:, 4]
    len_s = len(all_size)
    if len(all_size[1:len_s]) != 0:
        max_size = max(all_size[1:len_s])
        for i in range(1, nlabels):
            region_size = stats[i, 4]
            if region_size != max_size:
                output[labels == i] = 0
    return output

def extract_fg(dataset_path: str, subject: str, camera: int, trial: int, action: int, abort_signal):
    sub_str = f'Subject{subject}'
    cam_str = f'Camera{camera}'
    trial_str = f'Trial{trial}'
    act_str = f'Activity{action}'
    main_folder = os.path.join(
        dataset_path, 
        sub_str,
        cam_str,
        trial_str,
        f'{sub_str}{act_str}{trial_str}{cam_str}'
    )
    print(f"Extracting FG from {main_folder}")
    
    input_folder = os.path.join(main_folder, 'RGB')
    if not os.path.exists(input_folder):
        print(f"{input_folder} does not exist")
        return
    
    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'output',
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{action}'
        )
    )
    
    file_list = os.listdir(input_folder)
    total_files = len(file_list)
    start = 3
    inc = 3
    thresh = 25
    
    bg_file = os.path.join(
        output_folder,
        'background_image',
        f'background_{sub_str}_{cam_str}_{trial_str}_{act_str}.png'
    )
    
    if not os.path.exists(bg_file):
        msg = f'Error: Background image "{bg_file}" does not exist'
        return msg
    
    bg_frame = cv2.imread(bg_file)
    if bg_frame is None:
        msg = f'Error: Failed to load background image "{bg_file}"'
        return msg
    bg_frame = cv2.resize(bg_frame, (320, 240))
    
    for index in range(start, total_files + 1, inc):
        if abort_signal.is_set():
            print("Extraction aborted")
            break
        start_time = time.time()
        frame2 = cv2.imread(os.path.join(input_folder, file_list[index-1]))
        if frame2 is None:
            msg = f'Error: Failed to load image "{os.path.join(input_folder, file_list[index-1])}"'
            print(msg)
            return msg
        frame2 = cv2.resize(frame2, (320, 240))
        img1 = cv2.absdiff(bg_frame, frame2)
        img2 = np.zeros_like(img1)
        img2 = img1
        img2[img1 < thresh] = 0
        img2[img1 >= thresh] = 255
        img3 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
        ret, bw_img = cv2.threshold(img3, 127, 255, cv2.THRESH_BINARY)
        se1 = np.ones((4, 4), np.uint8)
        dilate_img1 = cv2.morphologyEx(bw_img, cv2.MORPH_DILATE, se1)
        se2 = np.ones((1, 20), np.uint8)
        dilate_img2 = cv2.morphologyEx(bw_img, cv2.MORPH_DILATE, se2)
        result_img = take_max_obj(dilate_img1)
        path = os.path.join(
            output_folder,
            'FG_FD',
        )
        os.makedirs(path, exist_ok=True)
        cv2.imwrite(os.path.join(path, file_list[index-1]), result_img)
        print(f"Extracted FG {file_list[index-1]} in {time.time() - start_time} seconds")
    
    print(f"Images saved at {path}")
    # Create video from FG FD images
    video_name = f'FG_FD_subject{subject}_camera{camera}_trial{trial}_activity{action}.mp4'
    video_path = os.path.join(path, video_name)
    try:
        # Adjust the frame rate if necessary
        images_to_video(path, video_path, fps=10, image_format=".png")
        print(f"Video created at {video_path}")
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        return None
    return video_path
