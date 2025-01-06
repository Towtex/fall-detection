import cv2
import os
import numpy as np

def create_background_image(dataset_path: str, cbg_path: str, subject: str, camera: str, trial: str, activity: str):
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname('app.py'),
            '..',
            'output',
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}'
        )
    )
    sub_str = f'Subject{subject}'
    cam_str = f'Camera{camera}'
    trial_str = f'Trial{trial}'
    act_str = f'Activity{activity}'
    main_folder = os.path.join(
        dataset_path,
        sub_str,
        cam_str,
        trial_str,
        f'{sub_str}{act_str}{trial_str}{cam_str}'
    )
    
    # path to save the background images
    path = os.path.join(
        output_path,
        'background_image',
        f'background_{sub_str}_{cam_str}_{trial_str}_{act_str}.png',
    )
                  
    if (int(activity) <= 6 or int(activity) == 11):
        cbg_filename = os.path.join(
            cbg_path,
            f'cm_background_{cam_str}_Con1.png'
        )
    else:
        cbg_filename = os.path.join(
            cbg_path,
            f'cm_background_{cam_str}_Con2.png'
        )
    
    if (int(activity) == 11):
        cbg_image = cv2.imread(cbg_filename)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cv2.imwrite(path, cbg_image)
        
    # print(f"reading {cbg_filename}")
    image_path = os.path.join(main_folder, 'RGB')
    mask_path = os.path.join(main_folder, 'Mask')
    file_list = os.listdir(image_path)
    filename1 = file_list[0]

    if os.path.exists(mask_path):
        file_list2 = os.listdir(mask_path)
        filename2 = file_list2 [0]
        mask = cv2.imread(os.path.join(mask_path, filename2))
    else:
        print("Mask File does not exist")
        return
    
    image1 = cv2.imread(os.path.join(image_path, filename1))
    image1 = cv2.resize(image1,(320,240))
    cbg_image = cv2.imread(cbg_filename)
    cbg_image = cv2.resize(cbg_image,(320,240))
    
    mask = cv2.resize(mask,(320,240))
       
    kernel = np.ones((3,3), np.uint8)
    mask1 = cv2.dilate(mask, kernel, iterations=1)
    thresh = 128
    im_bool1 = mask1 >= thresh
    im_bool2 = mask1 < thresh
    
    image3 = image1 * im_bool2
    image4 = cbg_image * im_bool1
       
    bg_result = image3 + image4
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cv2.imwrite(path, bg_result)
    print(f'Background image created for {path}')
    return path
