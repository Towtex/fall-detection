import cv2 
import os
import shutil
import time

def take_max_obj(image):
    output = image
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
    all_size = stats[:, 4]
    len_s = len(all_size)
    if len(all_size[1:len_s]) != 0:
        max_size = max(all_size[1:len_s])
        for i in range(1, nlabels):
            regions_size = stats[i, 4]
            if regions_size != max_size:
                output[labels == i] = 0
    return output

def create_shi(method, dataset_path: str, subject: int, camera: int, trial: int, activity: int):
    sub_str = f'Subject{subject}'
    cam_str = f'Camera{camera}'
    trial_str = f'Trial{trial}'
    act_str = f'Activity{activity}'
    
    main_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'output',
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}'
        )
    )
    
    if method == 'Yolov8':
        fg_folder = os.path.join(main_folder, 'extracted_fg_yolo')
        output_folder = os.path.join(
            main_folder,
            'SHI_Yolov8'
        )
    elif method == 'CBF&BS':
        fg_folder = os.path.join(main_folder, 'extracted_fg_fd')
        output_folder = os.path.join(main_folder, 'SHI_CBF_BS')
    else:
        raise ValueError("Unsupported method: {}".format(method))
    
    if not os.path.exists(fg_folder):
        print(f"{fg_folder} does not exist")
        return
    
    file_list = os.listdir(fg_folder)
    total_files = len(file_list) - 1
    
    for index in range(1, total_files + 1):
        start_time = time.time()
        filename = file_list[index]
        fg_frame1 = cv2.imread(os.path.join(fg_folder, file_list[index-1]))
        fg_frame1 = cv2.resize(fg_frame1, (320, 240))
        fg_frame2 = cv2.imread(os.path.join(fg_folder, filename))
        fg_frame2 = cv2.resize(fg_frame2, (320, 240))
        result_img = fg_frame1 + fg_frame2
        result_img = take_max_obj(cv2.cvtColor(result_img, cv2.COLOR_BGR2GRAY))
        os.makedirs(output_folder, exist_ok=True)
        cv2.imwrite(os.path.join(output_folder, file_list[index]), result_img)
        print(f"SHI created for {file_list[index]} in {time.time() - start_time} seconds")