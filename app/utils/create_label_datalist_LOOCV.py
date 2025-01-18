import glob
import os

def create_data_list_loocv(feature: str, class_limit: int, test_subject: int, camera: str):
    class_list = [
        'Falling',
        'Falling forward using hands',
        'Falling forward using knees',
        'Falling backward',
        'Falling sideward',
        'Falling while attempting to sit in an empty chair',
        'Walking',
        'Standing',
        'Sitting',
        'Picking up an object',
        'Jumping',
        'Laying'
    ]
    
    output_folder = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            '..',
            'output',
        )
    )
    
    out_str = ''
    for sub in range(1, 18):
        sub_str = f'Subject_{sub}'
        if camera == '1_2':
            img_folder = os.path.join(
                output_folder,
                sub_str,
                f'CNN_features_sequences_{feature}'
            )
        else:
            img_folder = os.path.join(
                output_folder,
                sub_str,
                f'Camera_{camera}',
                f'CNN_features_sequences_{feature}'
            )
        
        if not os.path.exists(img_folder):
            print(f"Error: {sub_str} folder does not exist.")
            return f'Error: {sub_str} folder does not exist.'
        else:
            print(f"{sub_str} Folder exists: {img_folder}.")
        
        # print(f"CNN Features Folder: {img_folder}")
        all_feature_files = glob.glob(os.path.join(img_folder, '*.npy'))
        total_files = len(all_feature_files)
        
        if total_files == 0:
            print(f"Error: No files found in CNN Features Folder, {img_folder}.")
            return f'Error: No files found in CNN Features Folder, {img_folder}.'
        
        for feature_path in all_feature_files:
            all_parts = os.path.basename(feature_path).split('-')
            trial = int(all_parts[2].split('Trial')[1])
            train_or_test = 'test' if sub == test_subject else 'train'
            
            action = int(all_parts[3].split('Activity')[1])
            if class_limit == 2:
                class_str = 'Falling' if action <= 5 else 'NotFalling'
            elif class_limit == 7 and action <= 5:
                class_str = 'Falling'
            else:
                class_str = class_list[action - 1]

            out_str += f'{train_or_test},{class_str},{sub_str},Camera{camera},{all_parts[2]},{all_parts[3]},{feature_path}\n'
    
    if out_str:
        out_file_dir = os.path.join(output_folder, f'Subject_{test_subject}')
        os.makedirs(out_file_dir, exist_ok=True)
        
        out_file_name = os.path.join(
            out_file_dir,
            f'train_data_{class_limit}_classes_cam_{camera}_test_subject{test_subject}_{feature}.csv'
        )
        with open(out_file_name, 'w') as f:
            f.write(out_str)
            print(f"Success: Label created for Subject {test_subject}, {out_file_name}")
            return f'Success: Label created for Subject {test_subject}, {out_file_name}'
    
    return 'Error: No data found to create label.'
