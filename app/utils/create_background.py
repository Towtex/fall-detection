import cv2
import os
import numpy as np


def create_background_image(dataset_path: str, cbg_path: str, subject: str):
    output_path = os.path.abspath(
        os.path.join(
            os.path.dirname('app.py'),
            '..',
            'output'
        )
    )
    sub_str = f'Subject{subject}'
    for camera in range(1, 3):
        cam_str = f'Camera{camera}'
        for trial in range(1, 4):
            trial_str = f'Trial{trial}'
            for action in range(1, 12):
                act_str = f'Activity{action}'
                main_folder = os.path.join(
                    dataset_path,
                    sub_str,
                    cam_str,
                    trial_str,
                    f'{sub_str}{act_str}{trial_str}{cam_str}'
                )
                
                if (action <= 6 or action == 11):
                    cbg_filename = os.path.join(
                        cbg_path,
                        f'background_{cam_str}_Con1.png'
                    )
                else:
                    cbg_filename = os.path.join(
                        cbg_path,
                        f'background_{cam_str}_Con2.png'
                    )
                
                if (action == 11):
                    cbg_image = cv2.imread(cbg_filename)
                    path = os.path.join(
                        output_path,
                        'background_images',
                        f'{sub_str}_{act_str}_{trial_str}_{cam_str}',
                        'background.png'
                    )
                    os.makedirs(os.path.dirname(path), exist_ok=True)
                    cv2.imwrite(path, cbg_image)
                    
                # print(f"reading {cbg_filename}")
                image_path = os.path.join(main_folder, 'RGB')
                mask_path = os.path.join(main_folder, 'Mask')
                file_list = os.listdir(image_path)
                total_files =len(file_list) -1
                filename1 = file_list[0]
                copyFlag = 0

                if os.path.exists(mask_path):
                    file_list2 = os.listdir(mask_path)
                    filename2 = file_list2 [0]
                    mask0 = cv2.imread(os.path.join(mask_path, filename2))
                    if not filename2.endswith('.png'):
                        copyFlag = 1
                else:
                    copyFlag = 1
                
                image1 = cv2.imread(os.path.join(image_path, filename1))
                image1 = cv2.resize(image1,(320,240))
                cbg_image = cv2.imread(cbg_filename)
                cbg_image = cv2.resize(cbg_image,(320,240))
                
                if copyFlag == 1:
                    print('Mask File does not exist')
                    file_list3 = os.listdir(
                        os.path.join(
                            main_folder,
                            'FgResult'
                        )
                    )
                    
                    fg_path = os.path.join(
                        main_folder,
                        'FgResult',
                        file_list3[0]
                    )
                    
                    mask0 = cv2.imread(fg_path)
                
                copyFlag = 0
                
                mask0 = cv2.resize(mask0,(320,240))
                   
                kernel = np.ones((3,3), np.uint8)
                mask1 = cv2.dilate(mask0, kernel, iterations=1)
                thresh = 128
                im_bool1 = mask1 >= thresh
                im_bool2 = mask1 < thresh
                
                image3 = image1 * im_bool2
                image4 = cbg_image * im_bool1
                   
                bg_result = image3 + image4
                path = os.path.join(
                    output_path,
                    'background_images',
                    f'{sub_str}_{act_str}_{trial_str}_{cam_str}',
                    'background.png'
                )
                os.makedirs(os.path.dirname(path), exist_ok=True)
                cv2.imwrite(path, bg_result)
                # print(f'Background image created for {path}')
      
# if __name__ == '__main__':
#     subject = 1
#     create_background_image(subject)
