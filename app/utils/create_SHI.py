import cv2 
import os
import time
from utils.images_to_video import images_to_video


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

def create_shi(method, subject: int, camera: int, trial: int, activity: int, abort_signal):
    
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
        fg_folder = os.path.join(main_folder, 'FG_Yolov8')
        output_folder = os.path.join(
            main_folder,
            'SHI_Yolov8'
        )
    elif method == 'FD':
        fg_folder = os.path.join(main_folder, 'FG_FD')
        output_folder = os.path.join(main_folder, 'SHI_FD')
    else:
        raise ValueError("Unsupported method: {}".format(method))
    
    if not os.path.exists(fg_folder):
        msg = f'Error: {fg_folder} does not exist'
        print(msg)
        return msg
    
    file_list = [f for f in os.listdir(fg_folder) if f.endswith('.png') or f.endswith('.jpg')]
    total_files = len(file_list) - 1
    
    if total_files <= 0:
        msg = f'Error: No images found in {fg_folder}'
        print(msg)
        return msg
    
    print(f"Creating SHI for subject: {subject}, camera: {camera}, trial: {trial}, activity: {activity}")
    
    for index in range(1, total_files + 1):
        if abort_signal.is_set():
            print("SHI creation aborted.")
            break
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
    
    print(f"Images saved at {output_folder}")
    # Create video from SHI images
    video_name = f'SHI_{method}_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
    video_path = os.path.join(output_folder, video_name)
    try:
        images_to_video(output_folder, video_path, fps=10, image_format=".png")
        print(f"Video created at {video_path}")
    except Exception as e:
        print(f"Error creating video: {str(e)}")
        return None
    return video_path
