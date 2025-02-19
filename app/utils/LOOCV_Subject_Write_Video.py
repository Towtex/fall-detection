import warnings
warnings.filterwarnings('ignore')
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf
# gpus = tf.config.list_physical_devices('GPU')
# if gpus is not None:
#   # Restrict TensorFlow to only use the first GPU
#   try:
#     tf.config.set_visible_devices(gpus[0], 'GPU')
#   except RuntimeError as e:
#     # Visible devices must be set before GPUs have been initialized
#     print(e)
from keras.preprocessing import image
from keras.applications.inception_v3 import InceptionV3, preprocess_input
import keras.models 
from keras.layers import Input
import glob
import cv2 
import numpy as np
import os.path
#import global_variables as gv
import warnings
warnings.filterwarnings("ignore")

class_list=[
                "Falling",
                "Falling forward using hands",
                "Falling forward using knees",
                "Falling backward",
                "Falling sideward",
                "Falling while attempting to sit in an empty chair",
                "Walking",
                "Standing",
                "Sitting",
                "Picking up an object",
                "Jumping",
                "Laying"
                ]

def test_by_features(output_path:str, dataset_path:str,subject:int,camera:str, trial:int,feature_str:str,class_limit:int, action: int):
    model_str = os.path.join(output_path, f"Subject{subject}", f"train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_{feature_str}")
    
    model_fld = os.path.join(model_str, 'weight_models')
    all_model_files = glob.glob(os.path.join(model_fld, '*.hdf5'))
    all_model_files.sort(key=os.path.getctime, reverse=True)

    for file_name in all_model_files:
        if file_name != all_model_files[0]:
            os.remove(file_name)
    if len(all_model_files) != 0:
        saved_model = all_model_files[0]
    else:
        saved_model = None
    print(f"Load model: {saved_model}")
    
    # font
    font = cv2.FONT_HERSHEY_SIMPLEX
    # org
    org = (50, 50)
    # fontScale
    fontScale = 1    
    # Blue color in BGR
    color = (255, 0, 0)
    # Line thickness of 2 px
    thickness = 2
    width = 320 
    height = 240 
        
    subStr = f"Subject_{subject}"
    camStr = f"Camera_{camera}"     
    seq_length = 18
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    fps = 5    
    model = keras.models.load_model(saved_model)
    #print(model.input_shape)
    #print(model.summary())
    
    # if feature_str=="DOF":
    #     img_str="ColorDOF"    
        #img_str="DOF" 
    while trial<=3:
        action=1
        while action<=11:            
            trialStr = f"Trial_{trial}"
            actStr = f"Activity_{action}"
            img_fld_1 = ""
            img_fld_2 = ""
            fg_fld_1 = ""
            fg_fld_2 = ""
            output_fld_1 = ""
            output_fld_2 = ""    

            if camera=="1_2":
                img_fld_1 = os.path.join(dataset_path, subStr, "Camera1", trialStr, f"{subStr}{actStr}{trialStr}Camera1", "RGB")
                img_fld_2 = os.path.join(dataset_path, subStr, "Camera2", trialStr, f"{subStr}{actStr}{trialStr}Camera2", "RGB")
                fg_fld_1 = os.path.join(dataset_path, subStr, "Camera1", trialStr, f"{subStr}{actStr}{trialStr}Camera1", "SHI")
                fg_fld_2 = os.path.join(dataset_path, subStr, "Camera2", trialStr, f"{subStr}{actStr}{trialStr}Camera2", "SHI")
                features_fld = os.path.join(output_path, subStr, f"CNN_features_sequences_{feature_str}")
                output_fld_1 = os.path.join(output_path, subStr, "Camera_1", trialStr, f"{subStr}-{actStr}-{trialStr}-Camera_1", f"{camStr}_{feature_str}_Test_LOOCV_Subject_{subStr}_{class_limit}_Classes_Results.avi")
                output_fld_2 = os.path.join(output_path, subStr, "Camera_2", trialStr, f"{subStr}-{actStr}-{trialStr}-Camera_2", f"{camStr}_{feature_str}_Test_LOOCV_Subject_{subStr}_{class_limit}_Classes_Results.avi")
                video_writer_1 = cv2.VideoWriter(output_fld_1, fourcc, fps, (int(width), int(height)))
                video_writer_2 = cv2.VideoWriter(output_fld_2, fourcc, fps, (int(width), int(height)))
                frames_path_1 = glob.glob(os.path.join(fg_fld_1,'*.png'))
                frames_path_1.sort(key=os.path.getctime)
                frames_path_2 = glob.glob(os.path.join(fg_fld_2,'*.png'))
                frames_path_2.sort(key=os.path.getctime)
                frames_len_1 = len(frames_path_1)
                print(f"frames_len_1 ={frames_len_1}")
                frames_len_2 = len(frames_path_2)
                print(f"frames_len_2 ={frames_len_2}")
            
            else: 
                img_fld_1 = os.path.join(dataset_path, subStr, camStr, trialStr, f"{subStr}{actStr}{trialStr}{camStr}", "RGB")
                fg_fld_1 = os.path.join(output_path, subStr, camStr, trialStr, f"{subStr}{actStr}{trialStr}{camStr}", "SHI")
                
                features_fld = os.path.join(output_path, subStr, camStr, f"CNN_features_sequences_{feature_str}")
                if(trial==1):
                    output_fld_1 = os.path.join(dataset_path, subStr, camStr, trialStr, f"{subStr}{actStr}{trialStr}{camStr}", f"{camStr}_{feature_str}_Test_LOOCV_Subject_{subStr}_{class_limit}_Classes_Results.avi")
                elif(trial==2):
                    output_fld_1 = os.path.join(output_path, subStr, camStr, trialStr, f"{subStr}-{actStr}-{trialStr}-{camStr}", f"{camStr}_{feature_str}_Test_LOOCV_Subject_{subStr}_{class_limit}_Classes_Results.avi")
                else:
                    output_fld_1 = os.path.join(output_path, subStr, camStr, trialStr, f"{subStr}-{actStr}-{trialStr}-{camStr}", f"{camStr}_{feature_str}_Test_LOOCV_Subject_{subStr}_{class_limit}_Classes_Results.avi")
                
                #output_fld_1 = f'{dataset_path}train_data_{class_limit}_classes_cam_{camera}_test_trial3_{test_feature}/{feature_str}_Results.avi/' #Camera 1_2
                video_writer_1 = cv2.VideoWriter(output_fld_1, fourcc, fps, (int(width), int(height)))
                frames_path_1 = glob.glob(os.path.join(fg_fld_1,'*.png'))
                frames_path_1.sort(key=os.path.getctime)
                frames_len_1 = len(frames_path_1)
                print(f"frames_len_1 ={frames_len_1}")
                        
            startF=0        
            incStartF=0
            incEndF=seq_length    

            while True:
                endF=startF+incEndF
                subFrame_path_1 = frames_path_1[startF+incStartF:endF]
                if camera =="1_2":
                    subFrame_path_2 = frames_path_2[startF+incStartF:endF]

                features_path = os.path.join(features_fld, f"{subStr}-{camStr}-{trialStr}-{actStr}-{endF}-{seq_length}-features.npy")
                if not os.path.exists(features_path):
                    print(f"Features file not found: {features_path}")
                    break
                x_data =  np.load(features_path)
                features1 = np.asarray(x_data).astype('float32')
                test_data = np.array([features1])
                predicted_classes = np.argmax(model.predict(test_data), axis=-1)
                
                #class_list=""
                if  class_limit==2:
                    if (predicted_classes==0):
                        class_str='Falling'
                        color = (0, 0, 255)# Red color in BGR
                    else:
                        class_str='Not Falling'
                        color = (0, 0, 255)# Red color in BGR
                elif class_limit==7:
                    if (predicted_classes<5):
                        class_str='Falling'
                        color = (0, 0, 255)# Red color in BGR
                    else:
                        if (predicted_classes==0):
                            class_str='Falling'
                            color = (0, 0, 255)# Red color in BGR
                        elif (predicted_classes==5):
                            class_str='Walking'
                            color = (0, 0, 255)# Red color in BGR
                        elif (predicted_classes==6):
                            class_str='Standing'
                            color = (0, 0, 255)# Red color in BGR
                        elif (predicted_classes==7):
                            class_str='Sitting'
                            color = (0, 0, 255)# Red color in BGR
                        elif (predicted_classes==8):
                            class_str='Picking Object'
                            color = (0, 0, 255)# Red color in BGR
                        elif (predicted_classes==9):
                            class_str='Jumping'
                            color = (0, 0, 255)# Red color in BGR
                        else:
                            class_str='Laying'
                            color = (0, 0, 255)# Red color in BGR
                elif class_limit==11:
                    if (predicted_classes==0):
                        class_str='Falling forward using hands'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==1):
                        class_str='Falling forward using knees'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==2):
                        class_str='Falling backward'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==3):
                        class_str='Falling sideway'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==4):
                        class_str='Falling while attempting to sit in an empty chair'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==5):
                        class_str='Walking'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==6):
                        class_str='Standing'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==7):
                        class_str='Sitting'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==8):
                        class_str='Picking Object'
                        color = (0, 0, 255)# Red color in BGR
                    elif (predicted_classes==9):
                        class_str='Jumping'
                        color = (0, 0, 255)# Red color in BGR
                    else:
                        class_str='Laying'
                        color = (0, 0, 255)# Red color in BGR

            
                ind =1
                i=0
                while (i<len(subFrame_path_1)):
                    image_path1 = subFrame_path_1[i]
                    image_path_list = image_path1.split('\\')
                    img_fileName = image_path_list[-1]
                    img_path1 = os.path.join(img_fld_1, img_fileName)
                    image_1 = cv2.imread(img_path1)
                    image_1= cv2.resize(image_1,(320,240))
                    fg_path_1= os.path.join(fg_fld_1, img_fileName)
                    fg_img_1 = cv2.imread(fg_path_1, cv2.IMREAD_GRAYSCALE)
                    (thresh, im_bw) = cv2.threshold(fg_img_1, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                    contours, hierarchy = cv2.findContours(fg_img_1,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2:]
                    bounding_boxes=[]
                    for c in contours:
                        rect = cv2.boundingRect(c)
                        if cv2.contourArea(c) >= 1000: 
                            bounding_boxes.append(rect) 
                    
                    if len(bounding_boxes)>0:
                        x,y,w,h = bounding_boxes[0]
                        image_1 = cv2.rectangle(image_1,(x,y),(x+w,y+h),(0,255,0),2)
                        #cv2.putText(image_1,'Moth Detected',(x+w+10,y+h),0,0.3,(0,255,0))
                        video_writer_1.write(image_1)                   

                    if camera =="1_2":
                        image_path2 = subFrame_path_2[i]
                        image_path_list = image_path2.split('\\')
                        img_fileName = image_path_list[-1]
                        img_path2 = os.path.join(img_fld_2, img_fileName)
                        image_2 = cv2.imread(img_path2)
                        image_2= cv2.resize(image_2,(320,240))
                        fg_path_2= os.path.join(fg_fld_2, img_fileName)
                        fg_img_2 = cv2.imread(fg_path_2)
                        fg_path_2= os.path.join(fg_fld_2, img_fileName)
                        fg_img_2 = cv2.imread(fg_path_2, cv2.IMREAD_GRAYSCALE)
                        (thresh, im_bw) = cv2.threshold(fg_img_2, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
                        contours, hierarchy = cv2.findContours(fg_img_2,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)[-2:]
                        bounding_boxes=[]

                        for c in contours:
                            rect = cv2.boundingRect(c)
                            if cv2.contourArea(c) >= 1000: 
                                bounding_boxes.append(rect) 
                        
                        if len(bounding_boxes)>0:
                            x,y,w,h = bounding_boxes[0] 
                            image_2 = cv2.rectangle(image_2,(x,y),(x+w,y+h),(0,255,0),2)
                            video_writer_2.write(image_2)

                    image_1 = cv2.putText(image_1, class_str, org, font, 
                                    fontScale, color, thickness, cv2.LINE_AA)                    
                    video_writer_1.write(image_1)
                    if camera =="1_2":
                        image_2 = cv2.putText(image_2, class_str, org, font, 
                                    fontScale, color, thickness, cv2.LINE_AA)                        
                        video_writer_2.write(image_2) 
                    i+=1  
                    
                incStartF=9
                startF=startF+incStartF
                if(startF+incEndF > frames_len_1) : 
                    break

            video_writer_1.release()
            if camera=="1_2":
                video_writer_2.release()
            action = action +1
        trial=trial+1       
            
# if __name__ == '__main__':
#     #dataset_path= gv.mainFld
#     #test_feature= gv.test_feature   
#     #camera=gv.camera
#     #class_limit = gv.class_limit
    
#     dataset_path="D:/Ph.D_Research/Research/Datasets_for_Fall_Detection/UP_Fall_Dataset/" # update the dataset path
#     #main_fld="D:/Ph.D_Research/Research/UI for Research/fall-detection/UP_Fall_Dataset/"
#     class_limit = 11 # for training 7 or 11 classes, update class_limit to 7 or 11.
#     test_feature="DOF" # can change value to "SHI_FD", "DOF_SHI_FD", "DOF_SHI_Yolov8", "DOF" ""SHI_Yolov8"
#     camera="1_2" # for training both camera 1 and 2 data, change value to "1_2" "4096" . otherwise change to "1" or "2" "2048" for training each camera data separately
    
#     subject=1
#     model_str = os.path.join(dataset_path, f"Subject{subject}", f"train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_{test_feature}")
    
#     #log_file= f"{model_str}_performance_eval.txt"
#     #file_writer = open(log_file, "w")
#     #print(type(file_writer))
   
#     model_fld = os.path.join(model_str, 'weight_models')
#     all_model_files = glob.glob(os.path.join(model_fld, '*.hdf5'))
#     all_model_files.sort(key=os.path.getctime, reverse=True)

#     for file_name in all_model_files:
#         if file_name != all_model_files[0]:
#             os.remove(file_name)
#     if len(all_model_files)!=0:
#         saved_model = all_model_files[0]
#     else:
#         saved_model = None
#     print(f"Load model: {saved_model}")

    
#     while subject<=1: 
#         test_by_features(fld=dataset_path,subject=subject,camera=camera,feature_str=test_feature,saved_model=saved_model,class_limit=class_limit)
#         subject= subject+1




