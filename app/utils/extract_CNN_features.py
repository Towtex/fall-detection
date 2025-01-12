import warnings
warnings.filterwarnings('ignore')
import os
import tensorflow as tf
from keras.preprocessing import image
from keras.applications.inception_v3 import InceptionV3, preprocess_input
from keras.models import Model
from keras.layers import Input
import glob
import cv2
import numpy as np

# gpus = tf.config.list_physical_devices('GPU')
# if gpus:
#     try:
#         tf.config.set_visible_devices(gpus[0], 'GPU')
#     except RuntimeError as e:
#         print(e)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

def process_image(image_path, model):
    """
    Process a single image and extract features using the given model.
    
    Args:
        image_path (str): Path to the image file.
        model (Model): Pre-trained CNN model for feature extraction.
    
    Returns:
        np.ndarray: Extracted features or None if the image cannot be read.
    """
    img = cv2.imread(image_path)
    if img is None:
        print(f"Warning: Image not found or cannot be read: {image_path}")
        return None
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = model.predict(x)[0]
    return features

def extract_features_from_frames(frames_path, feat_path1, feat_path2, model, seq_length):
    """
    Extract features from a sequence of frames.
    
    Args:
        frames_path (list): List of frame file paths.
        feat_path1 (str): Path to the first set of features.
        feat_path2 (str): Path to the second set of features (optional).
        model (Model): Pre-trained CNN model for feature extraction.
        seq_length (int): Expected sequence length.
    
    Returns:
        list: List of extracted features or None if the sequence length is not met.
    """
    sequence = []
    for image_path in frames_path:
        img_file_name = image_path.split('\\')[-1]
        img_path1 = os.path.join(feat_path1, img_file_name)
        print(f"Processing image: {img_path1}")
        features1 = process_image(img_path1, model)
        if features1 is None:
            continue

        if feat_path2:
            img_path2 = os.path.join(feat_path2, img_file_name)
            print(f"Processing image: {img_path2}")
            features2 = process_image(img_path2, model)
            if features2 is None:
                continue
            all_features = np.concatenate((features1, features2), axis=None)
        else:
            all_features = features1

        sequence.append(all_features)
    return sequence if len(sequence) == seq_length else None

def extract_cnn_features(feature: str, subject: int, camera: int, trial: int, action: int, abort_signal):
    """
    Extract CNN features for a given subject, camera, trial, and action.
    
    Args:
        feature (str): Feature type to extract.
        subject (int): Subject identifier.
        camera (int): Camera identifier.
        trial (int): Trial identifier.
        action (int): Action identifier.
        abort_signal (threading.Event): Signal to abort the extraction process.
    """
    try:
        sub_str = f'Subject{subject}'
        trial_str = f'Trial{trial}'
        cam_str = f'Camera{camera}' if camera != 3 else 'Camera1_2'
        act_str = f'Activity{action}'
        seq_length = 18
        image_height = 240
        image_width = 320
        image_shape = (image_height, image_width, 3)
        input_tensor = Input(image_shape)
        base_model = InceptionV3(
            input_tensor=input_tensor,
            weights='imagenet',
            include_top=True
        )
        model = Model(
            inputs=base_model.input,
            outputs=base_model.get_layer('avg_pool').output
        )
        main_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                '..',
                '..',
                'output',
                f'Subject_{subject}',
                f'Camera_{camera}',
                f'Trial_{trial}',
                f'Activity_{action}',
            )
        )
        
        if camera == 3:
            print(f"Starting feature extraction for Subject: {subject}, Camera: 1+2, Trial: {trial}, Action: {action}")
            feat_path1 = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    'output',
                    f'Subject_{subject}',
                    f'Camera_1',
                    f'Trial_{trial}',
                    f'Activity_{action}',
                    feature
                )
            )
            
            feat_path2 = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    'output',
                    f'Subject_{subject}',
                    f'Camera_2',
                    f'Trial_{trial}',
                    f'Activity_{action}',
                    feature
                )
            )
            
            output_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    '..',
                    '..',
                    'output',
                    f'Subject_{subject}',
                    f'Camera_1_2',
                    f'Trial_{trial}',
                    f'Activity_{action}',
                    f'CNN_features_sequences_{feature}'
                )
            )
            
            frames_path1 = glob.glob(os.path.join(feat_path1, '*.png'))
            frames_path2 = glob.glob(os.path.join(feat_path2, '*.png'))
            
            if len(frames_path1) == 0 or len(frames_path2) == 0:
                print(f"Error: No frames found at {feat_path1} or {feat_path2}")
                return f"Error: No frames found at {feat_path1} or {feat_path2}"
            
            frames_path = frames_path1
        else:
            print(f"Starting feature extraction for Subject: {subject}, Camera: {camera}, Trial: {trial}, Action: {action}")
            feat_path1 = os.path.join(main_path, feature)
            feat_path2 = None
            output_path = os.path.join(main_path, f'CNN_features_sequences_{feature}')
            frames_path = glob.glob(os.path.join(feat_path1, '*.png'))
        
            if len(frames_path) == 0:
                print("Error: No frames found.")
                return f"Error: No frames found at {feat_path1}"
        
        print(f"Feature paths: {feat_path1}, {feat_path2}")
        print(f"Output path: {output_path}")
        print(f"Frames found: {len(frames_path)}")
        
        
        frames_path.sort(key=os.path.getctime)
        frames_len = len(frames_path)
        inc_start_f = 9
        inc_end_f = seq_length
        os.makedirs(output_path, exist_ok=True)
        
        for start_f in range(0, frames_len, inc_start_f):
            if abort_signal.is_set():
                print("Extraction aborted.")
                return "Extraction aborted."
            end_f = start_f + inc_end_f
            if end_f > frames_len:
                break
            sub_frame_path = frames_path[start_f:end_f]
            save_path = os.path.join(
                output_path,
                f'{sub_str}-{cam_str}-{trial_str}-{act_str}-{end_f}-{seq_length}-features'
            )
            
            if not os.path.exists(save_path + '.npy'):
                print(f"Extracting features for frames {start_f} to {end_f}")
                sequence = extract_features_from_frames(sub_frame_path, feat_path1, feat_path2, model, seq_length)
                if sequence:
                    np.save(save_path, sequence)
                    print(f"Saved features to {save_path}.npy")
                else:
                    print("Sequence length mismatch. Skipping save.")
            else:
                print(f"Feature file already exists at {save_path}. Skipping extraction.")
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}"
