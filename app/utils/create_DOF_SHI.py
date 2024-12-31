import numpy as np
import cv2 
import os
import time

def takeMaxObj(image):
    output=image
    nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(image)
    all_size = stats[:,4]
    len_s = len(all_size)
    # print(all_size[1:len_s])
    if (len(all_size[1:len_s])!=0):
        # print(all_size[1:len_s])
        max_size = max(all_size[1:len_s])
        
        for i in range(1,nlabels):
            regions_size=stats[i,4]
            if regions_size!=max_size:            
                output[labels==i]=0
    return output

def fuse_DOF_SHI(dataset_path: str, subject: int, camera: int, trial: int, action: int, method: str):
    main_folder = os.path.abspath(
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
    
    dof_folder = os.path.join(main_folder, 'ColorDOF')
    
    if method == 'Yolov8':
        fg_folder = os.path.join(main_folder, 'SHI_Yolov8')
        output_folder = os.path.join(main_folder, 'DOF_SHI_Yolov8')
    else:
        fg_folder = os.path.join(main_folder, f'SHI_CBF_BS')
        output_folder = os.path.join(main_folder, f'DOF_SHI')
    
    if not (os.path.exists(fg_folder) and os.path.exists(dof_folder)):
        raise FileNotFoundError(f"{fg_folder} or {dof_folder} does not exist")
    
    file_list = os.listdir(dof_folder)
    total_files = len(file_list)    

    for index in range(total_files):
        start_time = time.time()
        filename = file_list[index]
        #print(filename)
        
        dof_frame_path = os.path.join(dof_folder, filename)
        fg_frame_path = os.path.join(fg_folder, filename)
        
        if not os.path.exists(fg_frame_path):
            raise FileNotFoundError(f"{fg_frame_path} does not exist")
        
        dof_frame = cv2.imread(dof_frame_path)
        dof_frame = cv2.resize(dof_frame, (320, 240))#(320,240)
        
        fg_frame = cv2.imread(fg_frame_path)   
        fg_frame = cv2.resize(fg_frame, (320, 240))   
                
        dof_frame1 = dof_frame[..., 0]
        dof_frame2 = dof_frame[..., 1]
        dof_frame3 = dof_frame[..., 2] 
        
        img1 = fg_frame.copy()
        img1[dof_frame1 != 0] = 0
        img1[dof_frame2 != 0] = 0
        img1[dof_frame3 != 0] = 0 
        
        #print(len(fg_frame[fg_frame != 0]))
        
        if len(fg_frame[fg_frame != 0]) < 38400:
            img2 = img1 + dof_frame
        else:
            img2 = dof_frame
            
        img3 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY) 
        img4 = takeMaxObj(img3)
        result_img = img2        
        result_img[img4 == 0] = 0
        #print("--- %s seconds ---" % (time.time() - start_time))
        os.makedirs(output_folder, exist_ok=True)
        cv2.imwrite(os.path.join(output_folder, filename), result_img)
        print(f"DOF_SHI created for {filename} in {time.time() - start_time} seconds")
