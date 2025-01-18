import glob
import os

def create_data_list(feature: str, class_limit: int, subject: int, camera: str):
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
    
    if camera == '1_2':
        img_folder = os.path.join(
            output_folder,
            f'Subject_{subject}',
            f'CNN_features_sequences_{feature}'
        )
    else:
        img_folder = os.path.join(
            output_folder,
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'CNN_features_sequences_{feature}'
        )
    
    print(f"CNN Features Folder: {img_folder}")
    all_feature_files = glob.glob(os.path.join(img_folder, '*.npy'))
    total_files = len(all_feature_files)
    
    if total_files == 0:
        print(f"Total Files: {total_files}")
        print('Error: No files found!')
        raise FileNotFoundError(f'No files found in {img_folder}')
    out_str = ''
    for feature_path in all_feature_files:
        all_parts = os.path.basename(feature_path).split('-')
        trial = int(all_parts[2].split('Trial')[1])
        train_or_test = 'test' if trial == 3 else 'train'
        
        action = int(all_parts[3].split('Activity')[1])
        if class_limit == 2:
            class_str = 'Falling' if action <= 5 else 'NotFalling'
        elif class_limit == 7 and action <= 5:
            class_str = 'Falling'
        else:
            class_str = class_list[action - 1]

        out_str += f'{train_or_test},{class_str},Subject{subject},Camera{camera},{all_parts[2]},{all_parts[3]},{feature_path}\n'
    
    out_file_name = os.path.join(
        output_folder,
        f'train_data_{class_limit}_classes_cam_{camera}_test_trial3_{feature}.csv'
    )
    with open(out_file_name, 'w') as f:
        f.write(out_str)
        print(f'Writing to {out_file_name} done!')
