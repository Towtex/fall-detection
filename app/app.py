import json
import os
import webview
import threading
import csv
# import logging

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, Response
from utils.extract_CNN_features import extract_cnn_features
from utils.create_common_background import create_common_background_image
from utils.create_background import create_background_image
from utils.extract_fg_fd import extract_fg
from utils.extract_fg_yolo import extract_fg_yolo
from utils.create_SHI import create_shi
from utils.extract_DOF import extract_color_dof
from utils.create_DOF_SHI import fuse_DOF_SHI
from utils.images_to_video import images_to_video
from utils.create_label_datalist_test_trial3 import create_data_list  # Updated import statement
from utils.train_classes_test_trial3 import train
from utils.train_classes_test_LOOCV import train as train_loocv
from utils.test_trial3 import test
from utils.create_label_datalist_LOOCV import create_data_list_loocv
from utils.test_LOOCV import test_loocv
from utils.Test_Trial3_Write_Video import test_by_features as test_trial3_write_video
from utils.LOOCV_Subject_Write_Video import test_by_features as loocv_subject_write_video

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))

# Configure logging
# logging.basicConfig(level=logging.DEBUG)

# Global variable to store the abort signal
abort_signal = threading.Event()

# Define dataset_path globally to avoid repetition
DATASET_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',
        'UP_Fall_Dataset'
    )
)

### Page routes
# 404 error page
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def index():
    return render_template('index.html', active_page='index')

app.add_url_rule('/index', 'index', index)

@app.route('/information')
def information():
    return render_template('information.html', active_page='information')

@app.route('/preprocessing')
def preprocessing():
    return render_template('preprocessing.html', active_page='preprocessing')

@app.route('/feature-extraction')
def feature_extraction():
    return render_template('feature-extraction.html', active_page='feature-extraction')

@app.route('/training')
def training():
    return render_template('training.html', active_page='training')

@app.route('/testing')
def testing():
    return render_template('testing.html', active_page='testing')

@app.route('/deep-feature-extraction')
def deep_feature_extraction():
    return render_template('deep-feature-extraction.html', active_page='deep-feature-extraction')

@app.route('/multicam')
def multicam():
    return render_template('multicam.html', active_page='multicam')

@app.route('/write-video')
def write_video():
    return render_template('write-video.html', active_page='write-video')

### End page routes

### API routes
# create_common_background API route
@app.route('/api/create_common_background', methods=['POST'])
def create_common_background():
    data = request.get_json()
    camera = data.get('camera')
    condition = data.get('condition')
    dataset_path = os.path.join(DATASET_PATH, 'Common Background Creation')
    
    image_path = create_common_background_image(dataset_path, condition=f'Camera{camera}_Con{condition}')
    # logging.debug(f'Created common background image path: {image_path}')
    
    if image_path is None:
        return jsonify({
            'message': 'Failed to create common background image.',
            'image': None
        }), 500

    image_url = url_for('serve_common_image', filename=os.path.basename(image_path))

    # Return the image path in the response
    return jsonify({
        'message': 'Common background created successfully.',
        'image': image_url
    }), 200
###############

# create_background API route
@app.route('/api/create_background', methods=['POST'])
def create_background():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    cbg_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'output',
            'common_background_images'
        )
    )
    if activity == "all":
        image_paths = []
        for act in range(1, 12):
            image_path = create_background_image(DATASET_PATH, cbg_path, subject, camera, trial, str(act))
            image_url = url_for('serve_image', subject=subject, camera=camera, trial=trial, activity=str(act), filename=os.path.basename(image_path))
            image_paths.append(image_url)
        return jsonify({
            'message': 'Background images created successfully for all activities.',
            'images': image_paths
        }), 200
    else:
        image_path = create_background_image(DATASET_PATH, cbg_path, subject, camera, trial, activity)
        print(image_path)
        image_url = url_for('serve_image', subject=subject, camera=camera, trial=trial, activity=activity, filename=os.path.basename(image_path))

        # Return the image path in the response
        return jsonify({
            'message': 'Background image created successfully.',
            'image': image_url
        }), 200
#############

# extract_fg_fd API route
@app.route('/api/extract_fg_fd', methods=['POST'])
def extract_fg_fd():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    if activity == 'all':
                        for act in range(1, 12):
                            if abort_signal.is_set():
                                break
                            msg = extract_fg(DATASET_PATH, subject, camera, tr, act, abort_signal)
                            if msg:
                                yield f'{msg}\n\n'.encode()
                            else:
                                yield f'Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'.encode()
                    else:
                        msg = extract_fg(DATASET_PATH, subject, camera, tr, int(activity), abort_signal)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'.encode()
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        msg = extract_fg(DATASET_PATH, subject, camera, int(trial), act, abort_signal)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'.encode()
                else:
                    msg = extract_fg(DATASET_PATH, subject, camera, int(trial), int(activity), abort_signal)
                    if msg:
                        yield f'{msg}\n\n'.encode()
                    else:
                        yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'.encode()
        except FileNotFoundError as e:
            yield f'Error: {str(e)}\n\n'.encode()
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_extract_fg_fd', methods=['POST'])
def stop_extract_fg_fd():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'Foreground extraction using FD has been stopped.'}), 200

@app.route('/api/get_fg_fd_video', methods=['POST'])
def get_fg_fd_video():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    video_name = f'FG_FD_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
    video_path = os.path.join(
        app.config['OUTPUT_FOLDER'],
        f'Subject_{subject}',
        f'Camera_{camera}',
        f'Trial_{trial}',
        f'Activity_{activity}',
        'FG_FD',
        video_name
    )
    
    if os.path.exists(video_path):
        video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify({'video_url': video_url}), 200
    else:
        return jsonify({'video_url': None}), 404

@app.route('/api/get_fg_fd_videos', methods=['POST'])
def get_fg_fd_videos():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    
    video_urls = []
    for activity in range(1, 12):
        video_name = f'FG_FD_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
        video_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}',
            'FG_FD',
            video_name
        )
        
        if os.path.exists(video_path):
            video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
            video_urls.append(video_url)
    
    if video_urls:
        return jsonify({'videos': video_urls}), 200
    else:
        return jsonify({'videos': []}), 404

###############

# extract_fg_yolo API route
@app.route('/api/extract_fg_yolo', methods=['POST'])
def extract_fg_yolo_api():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    if activity == 'all':
                        for act in range(1, 12):
                            if abort_signal.is_set():
                                break
                            msg = extract_fg_yolo(DATASET_PATH, subject, camera, tr, act, abort_signal)
                            if msg:
                                yield f'{msg}\n\n'.encode()
                            else:
                                yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'.encode()
                    else:
                        msg = extract_fg_yolo(DATASET_PATH, subject, camera, tr, int(activity), abort_signal)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'.encode()
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        msg = extract_fg_yolo(DATASET_PATH, subject, camera, int(trial), act, abort_signal)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'.encode()
                else:
                    msg = extract_fg_yolo(DATASET_PATH, subject, camera, int(trial), int(activity), abort_signal)
                    if msg:
                        yield f'{msg}\n\n'.encode()
                    else:
                        yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'.encode()
        except FileNotFoundError as e:
            yield f'Error: {str(e)}\n\n'.encode()
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_extract_fg_yolo', methods=['POST'])
def stop_extract_fg_yolo():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'Foreground extraction using YOLO has been stopped.'}), 200

@app.route('/api/get_fg_yolo_video', methods=['POST'])
def get_fg_yolo_video():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    video_name = f'FG_Yolov8_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
    video_path = os.path.join(
        app.config['OUTPUT_FOLDER'],
        f'Subject_{subject}',
        f'Camera_{camera}',
        f'Trial_{trial}',
        f'Activity_{activity}',
        'FG_Yolov8',
        video_name
    )
    
    if os.path.exists(video_path):
        video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify({'video_url': video_url}), 200
    else:
        return jsonify({'video_url': None}), 404

@app.route('/api/get_fg_yolo_videos', methods=['POST'])
def get_fg_yolo_videos():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    
    video_urls = []
    for activity in range(1, 12):
        video_name = f'FG_Yolov8_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
        video_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}',
            'FG_Yolov8',
            video_name
        )
        
        if os.path.exists(video_path):
            video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
            video_urls.append(video_url)
    
    if video_urls:
        return jsonify({'videos': video_urls}), 200
    else:
        return jsonify({'videos': []}), 404

###############

# create_shi API route
@app.route('/api/create_shi', methods=['POST'])
def create_shi_api():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    method = data.get('method')
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    if activity == 'all':
                        for act in range(1, 12):
                            if abort_signal.is_set():
                                break
                            msg = create_shi(method, subject, camera, tr, act, abort_signal)
                            if msg:
                                yield f'{msg}\n\n'.encode()
                            else:
                                yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'.encode()
                    else:
                        msg = create_shi(method, subject, camera, tr, int(activity), abort_signal)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'.encode()
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        msg = create_shi(method, subject, camera, int(trial), act, abort_signal)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'.encode()
                else:
                    msg = create_shi(method, subject, camera, int(trial), int(activity), abort_signal)
                    if msg:
                        yield f'{msg}\n\n'.encode()
                    else:
                        yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'.encode()
        except Exception as e:
            yield f'Error: {str(e)}\n\n'.encode()
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_create_shi', methods=['POST'])
def stop_create_shi():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'SHI creation has been stopped.'}), 200

@app.route('/api/get_shi_video', methods=['POST'])
def get_shi_video():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    method = data.get('method')
    
    video_name = f'SHI_{method}_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
    video_path = os.path.join(
        app.config['OUTPUT_FOLDER'],
        f'Subject_{subject}',
        f'Camera_{camera}',
        f'Trial_{trial}',
        f'Activity_{activity}',
        f'SHI_{method}',
        video_name
    )
    
    if os.path.exists(video_path):
        video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify({'video_url': video_url}), 200
    else:
        return jsonify({'video_url': None}), 404

@app.route('/api/get_shi_videos', methods=['POST'])
def get_shi_videos():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    method = data.get('method')
    
    video_urls = []
    for activity in range(1, 12):
        video_name = f'SHI_{method}_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
        video_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}',
            f'SHI_{method}',
            video_name
        )
        
        if os.path.exists(video_path):
            video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
            video_urls.append(video_url)
    
    if video_urls:
        return jsonify({'videos': video_urls}), 200
    else:
        return jsonify({'videos': []}), 404

###############

# extract_dof API route
@app.route('/api/extract_dof', methods=['POST'])
def extract_dof_api():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    if activity == 'all':
                        for act in range(1, 12):
                            if abort_signal.is_set():
                                break
                            msg = extract_color_dof(DATASET_PATH, subject, camera, tr, act)
                            if msg:
                                yield f'{msg}\n\n'.encode()
                            else:
                                yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'.encode()
                    else:
                        msg = extract_color_dof(DATASET_PATH, subject, camera, tr, int(activity))
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'.encode()
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        msg = extract_color_dof(DATASET_PATH, subject, camera, int(trial), act)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'.encode()
                else:
                    msg = extract_color_dof(DATASET_PATH, subject, camera, int(trial), int(activity))
                    if msg:
                        yield f'{msg}\n\n'.encode()
                    else:
                        yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'.encode()
        except FileNotFoundError as e:
            yield f'Error: {str(e)}\n\n'.encode()
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_extract_dof', methods=['POST'])
def stop_extract_dof():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'DOF extraction has been stopped.'}), 200

@app.route('/api/get_dof_video', methods=['POST'])
def get_dof_video():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    video_name = f'DOF_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
    video_path = os.path.join(
        app.config['OUTPUT_FOLDER'],
        f'Subject_{subject}',
        f'Camera_{camera}',
        f'Trial_{trial}',
        f'Activity_{activity}',
        'DOF',
        video_name
    )
    
    if os.path.exists(video_path):
        video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify({'video_url': video_url}), 200
    else:
        return jsonify({'video_url': None}), 404

@app.route('/api/get_dof_videos', methods=['POST'])
def get_dof_videos():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    
    video_urls = []
    for activity in range(1, 12):
        video_name = f'DOF_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
        video_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}',
            'DOF',
            video_name
        )
        
        if os.path.exists(video_path):
            video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
            video_urls.append(video_url)
    
    if video_urls:
        return jsonify({'videos': video_urls}), 200
    else:
        return jsonify({'videos': []}), 404

###############

# create_dof_shi API route
@app.route('/api/create_dof_shi', methods=['POST'])
def create_dof_shi_api():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    method = data.get('method')
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    
    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    if activity == 'all':
                        for act in range(1, 12):
                            if abort_signal.is_set():
                                break
                            msg = fuse_DOF_SHI(DATASET_PATH, subject, camera, tr, act, method)
                            if msg:
                                yield f'{msg}\n\n'.encode()
                            else:
                                yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'.encode()
                    else:
                        msg = fuse_DOF_SHI(DATASET_PATH, subject, camera, tr, int(activity), method)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'.encode()
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        msg = fuse_DOF_SHI(DATASET_PATH, subject, camera, int(trial), act, method)
                        if msg:
                            yield f'{msg}\n\n'.encode()
                        else:
                            yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'.encode()
                else:
                    msg = fuse_DOF_SHI(DATASET_PATH, subject, camera, int(trial), int(activity), method)
                    if msg:
                        yield f'{msg}\n\n'.encode()
                    else:
                        yield f'Success: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'.encode()
        except FileNotFoundError as e:
            yield f'Error: {str(e)}\n\n'.encode()
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_create_dof_shi', methods=['POST'])
def stop_create_dof_shi():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'DOF SHI creation has been stopped.'}), 200

@app.route('/api/get_dof_shi_video', methods=['POST'])
def get_dof_shi_video():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    method = data.get('method')
    
    video_name = f'DOF_SHI_{method}_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
    video_path = os.path.join(
        app.config['OUTPUT_FOLDER'],
        f'Subject_{subject}',
        f'Camera_{camera}',
        f'Trial_{trial}',
        f'Activity_{activity}',
        f'DOF_SHI_{method}',
        video_name
    )
    
    if os.path.exists(video_path):
        video_url = url_for('output_file', filename=os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify({'video_url': video_url}), 200
    else:
        return jsonify({'video_url': None}), 404

@app.route('/api/get_dof_shi_videos', methods=['POST'])
def get_dof_shi_videos():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    method = data.get('method')
    
    video_urls = []
    for activity in range(1, 12):
        video_name = f'DOF_SHI_{method}_subject{subject}_camera{camera}_trial{trial}_activity{activity}.mp4'
        video_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'Subject_{subject}',
            f'Camera_{camera}',
            f'Trial_{trial}',
            f'Activity_{activity}',
            f'DOF_SHI_{method}',
            video_name
        )
        
        if os.path.exists(video_path):
            filename = os.path.relpath(video_path, app.config['OUTPUT_FOLDER']).replace('\\', '/')
            video_url = url_for('output_file', filename)
            video_urls.append(video_url)
    
    if video_urls:
        return jsonify({'videos': video_urls}), 200
    else:
        return jsonify({'videos': []}), 404

##############

# extract_deep_features API route
@app.route('/api/extract_deep_features', methods=['POST'])
def extract_deep_features():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    feature = data.get('feature')
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')

    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    if activity == 'all':
                        for act in range(1, 12):
                            if abort_signal.is_set():
                                break
                            result = extract_cnn_features(feature, int(subject), int(camera), tr, act, abort_signal)
                            if result and "Error" in result:
                                yield f'{result}\n\n'.encode()
                                return
                            yield f'Success: Extracted deep features for subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'.encode()
                    else:
                        result = extract_cnn_features(feature, int(subject), int(camera), tr, int(activity), abort_signal)
                        if result and "Error" in result:
                            yield f'{result}\n\n'.encode()
                            return
                        yield f'Success: Extracted deep features for subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'.encode()
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        result = extract_cnn_features(feature, int(subject), int(camera), int(trial), act, abort_signal)
                        if result and "Error" in result:
                            yield f'{result}\n\n'.encode()
                            return
                        yield f'Success: Extracted deep features for subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'.encode()
                else:
                    result = extract_cnn_features(feature, int(subject), int(camera), int(trial), int(activity), abort_signal)
                    if result and "Error" in result:
                        yield f'{result}\n\n'.encode()
                        return
                    yield f'Success: Extracted deep features for subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'.encode()
        except FileNotFoundError as e:
            yield f'Error: File not found - {str(e)}\n\n'.encode()
        except Exception as e:
            yield f'Error: {str(e)}\n\n'.encode()

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_extract_deep_features', methods=['POST'])
def stop_extract_deep_features():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'Deep feature extraction has been stopped.'}), 200

# create_label API route
@app.route('/api/create_label', methods=['POST'])
def create_label():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    camera = data.get('camera')
    
    try:
        create_data_list(feature, int(class_limit), camera)
        return jsonify({'message': 'Label created successfully.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/create_label_loocv', methods=['POST'])
def create_label_loocv():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    subject = data.get('subject')
    camera = data.get('camera')
    
    try:
        message = create_data_list_loocv(feature, int(class_limit), int(subject), camera)
        return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify({'message': [f'Error: {str(e)}']}), 500

@app.route('/api/get_label_result', methods=['POST'])
def get_label_result():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    camera = data.get('camera')
    
    if 'loocv' in data:
        subject = data.get('subject')
        print(subject)
        # Construct the file path for LOOCV based on the parameters
        file_path = os.path.join(
            app.config['OUTPUT_FOLDER'],
            f'Subject_{subject}',
            f'train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_LOOCV_{feature}.csv'
        )
    else:
        # Construct the file path for regular training based on the parameters
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], f'train_data_{class_limit}_classes_cam_{camera}_test_trial3_{feature}.csv')
    
    print(f"Looking for file at: {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            csv_reader = csv.reader(file)
            csv_data = [row for row in csv_reader]
        return jsonify({'data': csv_data}), 200
    except FileNotFoundError:
        print("File not found.")
        return jsonify({'error': 'Result file not found'}), 404
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': str(e)}), 500
##########

# training API route
@app.route('/api/start_training', methods=['POST'])
def start_training():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    camera = data.get('camera')
    print("***** Training started *****")
    print(f"feature: {feature}, class_limit: {class_limit}, camera: {camera}")
    
    def generate():
        try:
            result = train(feature, int(class_limit), camera, abort_signal)
            yield f'{result}\n\n'
        except Exception as e:
            print(f"Error: {str(e)}")
            yield f'Error: {str(e)}\n\n'

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_training', methods=['POST'])
def stop_training():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'Training has been stopped.'}), 200

# LOOCV training API route
@app.route('/api/start_training_loocv', methods=['POST'])
def start_training_loocv():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    subject = data.get('subject')
    camera = data.get('camera')
    print("***** LOOCV Training started *****")
    print(f"feature: {feature}, class_limit: {class_limit}, camera: {camera}")
    
    def generate():
        try:
            result = train_loocv(feature, class_limit, subject, camera, abort_signal)
            yield f'{result}\n\n'
        except Exception as e:
            print(f"Error: {str(e)}")
            yield f'Error: {str(e)}\n\n'

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_training_loocv', methods=['POST'])
def stop_training_loocv():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'LOOCV Training has been stopped.'}), 200

##########

# testing API route
@app.route('/api/start-testing', methods=['POST'])
def start_testing():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    camera = data.get('camera')
    print("***** Testing started *****")
    try:
        test(feature, int(class_limit), camera)
        return jsonify({'message': 'Model has been tested successfully.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/get-test-result', methods=['POST'])
def get_test_result():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    camera = data.get('camera')
    
    # Construct the file path based on the parameters
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], f'train_data_{class_limit}_classes_cam_{camera}_test_trial3_{feature}_performance_eval.json')
    plot_image_path = os.path.join(app.config['OUTPUT_FOLDER'], f'train_data_{class_limit}_classes_cam_{camera}_test_trial3_{feature}_performance_eval.png')
    print(f"Looking for file at: {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            result_data = json.load(file)
        result_data['plot_image_path'] = url_for('output_file', filename=os.path.relpath(plot_image_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify(result_data), 200
    except FileNotFoundError:
        print("File not found.")
        return jsonify({'error': 'Result file not found'}), 404
    except json.JSONDecodeError:
        print("Invalid JSON in result file.")
        return jsonify({'error': 'Invalid JSON in result file'}), 500

# testing LOOCV API route
@app.route('/api/start-testing-loocv', methods=['POST'])
def start_testing_loocv():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    subject = data.get('subject')
    camera = data.get('camera')
    print("***** LOOCV Testing started *****")
    try:
        test_loocv(feature, int(class_limit), subject, camera)
        return jsonify({'message': 'LOOCV model has been tested successfully.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/api/get-test-loocv-result', methods=['POST'])
def get_test_loocv_result():
    data = request.get_json()
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    subject = data.get('subject')
    camera = data.get('camera')
    
    # Construct the file path based on the parameters
    file_path = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_LOOCV_{feature}_performance_eval.json')
    plot_image_path = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'train_data_{class_limit}_classes_cam_{camera}_test_subject{subject}_LOOCV_{feature}_performance_eval.png')
    print(f"Looking for file at: {file_path}")
    
    try:
        with open(file_path, 'r') as file:
            result_data = json.load(file)
        result_data['plot_image_path'] = url_for('output_file', filename=os.path.relpath(plot_image_path, app.config['OUTPUT_FOLDER']).replace('\\', '/'))
        return jsonify(result_data), 200
    except FileNotFoundError:
        print("File not found.")
        return jsonify({'error': 'Result file not found'}), 404
    except json.JSONDecodeError:
        print("Invalid JSON in result file.")
        return jsonify({'error': 'Invalid JSON in result file'}), 500

@app.route('/api/write_video', methods=['POST'])
def api_write_video():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    feature = data.get('feature')
    class_limit = data.get('class_limit')
    
    try:
        if 'loocv' in data:
            trial = data.get('trial')
            loocv_subject_write_video(app.config['OUTPUT_FOLDER'], DATASET_PATH, subject, camera, trial, feature, int(class_limit))
        else:
            test_trial3_write_video(app.config['OUTPUT_FOLDER'], DATASET_PATH, subject, camera, feature, int(class_limit))
        return jsonify({'message': 'Video written successfully.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

##########

# Serve files dynamically from the output folder
@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Serve background_image dynamically from the output folder
@app.route('/output/<subject>/Camera_<camera>/Trial_<trial>/Activity_<activity>/background_image/<filename>')
def serve_image(subject, camera, trial, activity, filename):
    folder_path = os.path.join(
        app.config['OUTPUT_FOLDER'], 
        f'Subject_{subject}', 
        f'Camera_{camera}', 
        f'Trial_{trial}', 
        f'Activity_{activity}', 
        'background_image'
    )
    return send_from_directory(folder_path, filename)

# Serve common_background_images dynamically from the output folder
@app.route('/output/common_background_images/<filename>')
def serve_common_image(filename):
    folder_path = os.path.join(app.config['OUTPUT_FOLDER'], 'common_background_images')
    return send_from_directory(folder_path, filename)

### End API routes

def run_flask():
    app.run(debug=True, use_reloader=False)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    webview.create_window(
        'Fall Detection and Classification Using Multiple Cameras Based on Features Fusion and CNN-LST',
        'http://127.0.0.1:5000'
    )
    webview.start()
    os._exit(0)
