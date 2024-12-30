from ultralytics import YOLO
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
    if len(all_size[1:len_s]) != 0:
        max_size = max(all_size[1:len_s])
        for i in range(1, nlabels):
            region_size = stats[i, 4]
            if region_size != max_size:
                output[labels == i] = 0
    return output

def extract_fg_yolo(dataset_path: str, subject: str, camera: int, trial: int, action: int):
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
        print(f"{input_folder} does not exist")
        return
    
    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'output',
            f'Subject_{subject}',
        )
    ) 
    
    # if not os.path.exists(output_folder):
    #     os.mkdir(output_folder)
    # else:
    #     shutil.rmtree(output_folder)
    #     os.mkdir(output_folder)

    file_list = os.listdir(input_folder)
    total_files = len(file_list)

    start = 3
    inc = 3
    
    for index in range(start, total_files + 1, inc):
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

        # Convert mask to 8-bit single-channel image
        mask = cv2.convertScaleAbs(mask)
        result_img = take_max_obj(mask)
        path = os.path.join(
            output_folder,
            'extracted_fg_yolo',
            cam_str,
            trial_str,
            act_str
        )
        os.makedirs(path, exist_ok=True)  # Ensure the directory exists
        cv2.imwrite(os.path.join(path, file_list[index - 1]), result_img)
        print(f"Extracted FG {file_list[index - 1]}")