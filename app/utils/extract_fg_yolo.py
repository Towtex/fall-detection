from ultralytics import YOLO
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

def extract_fg_yolo(dataset_path: str, subject: str, camera: int, trial: int, action: int, abort_signal):
    model = YOLO('yolov8m-seg.pt')
    yolo_classes = list(model.names.values())
    class_ids = [yolo_classes.index(clas) for clas in yolo_classes]
    se2 = np.ones((1, 20), np.uint8)
    conf = 0.5
    width = 320
    height = 240
    
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
    input_folder = os.path.join(main_folder, 'RGB')
    
    if not os.path.exists(input_folder):
        msg = f'Error: {input_folder} does not exist'
        return msg
    
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
    
    for index in range(start, total_files + 1, inc):
        if abort_signal.is_set():
            print("Extraction aborted")
            break
        start_time = time.time()
        img = cv2.imread(os.path.join(input_folder, file_list[index - 1]))
        img = cv2.resize(img, (width, height))
        mask = np.zeros([height, width], dtype=np.uint8)
        results = model.predict(img, conf=conf)

        for result in results:
            if result.masks is not None:
                for mask_points, box in zip(result.masks.xy, result.boxes):
                    points = np.int32([mask_points])
                    class_id = int(box.cls[0])
                    if class_id == 0:
                        color_number = class_ids.index(int(box.cls[0]))
                        cv2.fillPoly(mask, points, 255)

        mask = cv2.convertScaleAbs(mask)
        result_img = take_max_obj(mask)
        path = os.path.join(
            output_folder,
            'FG_Yolov8',
        )
        os.makedirs(path, exist_ok=True)
        cv2.imwrite(os.path.join(path, file_list[index - 1]), result_img)
        print(f"Extracted FG {file_list[index - 1]} in {time.time() - start_time} seconds")
        
    print(f"Images saved at {path}")
    video_name = f'FG_Yolov8_subject{subject}_camera{camera}_trial{trial}_activity{action}.mp4'
    video_path = os.path.join(path, video_name)
    try:
        images_to_video(path, video_path, fps=10, image_format=".png")
        print(f"Video created at {video_path}")
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        return None
    return video_path