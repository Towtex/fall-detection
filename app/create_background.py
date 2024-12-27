import cv2
import sys
import os
import numpy as np


def create_background_image(fld_path, cfg_path, subject):
    sub_str = f'Subject{subject}'
    camera=1
    while camera<=2:
        cam_str = f'Camera{camera}'
        trial=1
        while trial<=3:
            trial_str = f'Trial{trial}'
            action=1
            while action<=11: 
                act_str = f'Activity{action}'
                print(f"{sub_str}{act_str}{trial_str}{cam_str}")
                main_folder = os.path.abspath(os.path.join(fld_path, sub_str, cam_str, trial_str, f'{sub_str}{act_str}{trial_str}{cam_str}'))
                 
                if (action<=6 | action==11):
                    cfgFilename = cfg_path + 'background_'+cam_str + '_Con1.png'
                else:
                    cfgFilename = cfg_path + 'background_'+cam_str + '_Con2.png'
                
                if (action ==11):
                    cfgImage = cv2.imread(cfgFilename)
                    cv2.imwrite(main_folder + '/background.png',cfgImage)
                                                   
                imagePath = main_folder +"/RGB/"
                maskPath = main_folder +"/Mask/"
                
                file_list = os.listdir(imagePath)                
                total_files =len(file_list) -1  
                filename1 = file_list[0]
                copyFlag = 0

                if os.path.exists(maskPath):
                    file_list2 = os.listdir(maskPath)                    
                    filename2 = file_list2 [0]
                    mask0 = cv2.imread(maskPath+filename2)
                    if not filename2.endswith('.png'):
                        copyFlag = 1
                else:
                    copyFlag = 1                
                
                image1 = cv2.imread(imagePath+filename1)
                image1 = cv2.resize(image1,(320,240))
                cfgImage = cv2.imread(cfgFilename)
                cfgImage = cv2.resize(cfgImage,(320,240))
                
                if copyFlag==1:
                    print('Mask File does not exist');
                    print(filename1)
                    file_list3 = os.listdir(main_folder +"/FgResult/")
                    fgPath = main_folder +"/FgResult/" + file_list3[0];
                    print(fgPath)
                    mask0 = cv2.imread(fgPath)                    
                
                copyFlag = 0;   
                
                mask0 = cv2.resize(mask0,(320,240))
                   
                kernel = np.ones((3,3), np.uint8)
                mask1 = cv2.dilate(mask0, kernel, iterations=1)
                thresh = 128;
                im_bool1 = mask1 >= thresh;
                im_bool2 = mask1 < thresh;
                
                image3 = image1 * im_bool2;
                image4 = cfgImage * im_bool1;
                   
                bg_result = image3 + image4;
                  
                cv2.imwrite(main_folder + '/background.png',bg_result)
                action = action +1
            trial=trial+1
        camera =camera+1
      
    		
if __name__ == "__main__": 
    fld_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'UP_Fall_Dataset',
        ))
    cfg_path = 'Background Creation'
    
    print(fld_path)
    print(cfg_path)
    
    subject=1
    while subject<=17:
        subject += 1
