import numpy as np
import cv2 
import os
import shutil
import time

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
    # print(all_size[1:len_s])
    if len(all_size[1:len_s]) != 0:
        # print(all_size[1:len_s])
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
    
    # if os.path.exists(output_folder):
    #     shutil.rmtree(output_folder)
    # os.mkdir(output_folder)
    
    file_list = os.listdir(input_folder)
    total_files = len(file_list)
    start = 3
    inc = 3
    thresh = 25
    #sizeTh=200
    
    bg_file = os.path.join(
        output_folder,
        'background_image',
        f'background_{sub_str}_{cam_str}_{trial_str}_{act_str}.png'
    )
    # frame1 = np.float32(cv2.imread(file_list[start-1]))
    bg_frame = cv2.imread(bg_file)
    bg_frame = cv2.resize(bg_frame, (320, 240))
    #bgImg = cv2.cvtColor(bgFrame,cv2.COLOR_BGR2GRAY)
    
    for index in range(start, total_files + 1, inc):
        if abort_signal.is_set():
            print("Extraction aborted")
            break
        start_time = time.time()
        # print(file_list[index-1])
        frame2 = cv2.imread(os.path.join(input_folder, file_list[index-1]))
        frame2 = cv2.resize(frame2, (320, 240))
        # nextImg = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)        
        img1 = cv2.absdiff(bg_frame, frame2)  # image difference
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
        #print("--- %s seconds ---" % (time.time() - start_time))
        path = os.path.join(
            output_folder,
            'extracted_fg_fd',
        )
        os.makedirs(path, exist_ok=True)
        cv2.imwrite(os.path.join(path, file_list[index-1]), result_img)
        print(f"Extracted FG {file_list[index-1]}")
