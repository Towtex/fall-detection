import numpy as np
import cv2 
import os
import math
import time

def extract_color_dof(dataset_path: str, subject: int, camera: int, trial: int, action: int):
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
        print(f"Folder {input_folder} does not exist")
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
            f'Activity_{action}',
            'ColorDOF'
        )
    )  
        
    file_list = os.listdir(input_folder)
    total_files = len(file_list)    
    start = 3
    inc = 3
    unk_flow_max_th = math.exp(10)
    unk_flow_min_th = 0.25
                
    frame1 = cv2.imread(os.path.join(input_folder, file_list[start - 1]))
    frame1 = cv2.resize(frame1, (320, 240))
    prv_img = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
    hsv = np.zeros_like(frame1)
    hsv[..., 1] = 255

    print(f"Extracting ColorDOF for subject: {subject}, camera: {camera}, trial: {trial}, activity: {action}")
    
    for index in range(start + inc, total_files + 1, inc):
        start_time = time.time()
        frame2 = cv2.imread(os.path.join(input_folder, file_list[index - 1]))
        frame2 = cv2.resize(frame2, (320, 240))
        next_img = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
        flow = cv2.calcOpticalFlowFarneback(prv_img, next_img, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        u = flow[..., 0]
        v = flow[..., 1]
        unk_index_u1 = np.abs(u) > unk_flow_max_th
        u[unk_index_u1] = 0
        unk_index_v1 = np.abs(v) > unk_flow_max_th
        v[unk_index_v1] = 0       
        unk_index_u2 = np.abs(u) <= unk_flow_min_th
        u[unk_index_u2] = 0
        unk_index_v2 = np.abs(v) <= unk_flow_min_th
        v[unk_index_v2] = 0
        mag, ang = cv2.cartToPolar(u, v)
        hsv[..., 0] = ang * 180 / np.pi
        hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
        hsv = np.float32(hsv)
        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        prv_img = next_img
        os.makedirs(output_folder, exist_ok=True)
        cv2.imwrite(os.path.join(output_folder, file_list[index - 1]), bgr)
        print(f"Frame {index}, {file_list[index - 1]} processed in {time.time() - start_time} seconds")
