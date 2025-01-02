import os
import webview
import threading
import logging

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, Response
from utils.create_common_background import create_common_background_image
from utils.create_background import create_background_image
from utils.extract_fg_fd import extract_fg
from utils.extract_fg_yolo import extract_fg_yolo
from utils.create_SHI import create_shi
from utils.extract_DOF import extract_color_dof
from utils.create_DOF_SHI import fuse_DOF_SHI
from utils.images_to_video import images_to_video

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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
### End page routes

### API routes
@app.route('/api/create_common_background', methods=['POST'])
def create_common_background():
    data = request.get_json()
    camera = data.get('camera')
    condition = data.get('condition')
    dataset_path = os.path.join(DATASET_PATH, 'Common Background Creation')
    
    image_path = create_common_background_image(dataset_path, condition=f'Camera{camera}_Con{condition}')
    logging.debug(f'Created common background image path: {image_path}')
    
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
                            extract_fg(DATASET_PATH, subject, camera, tr, act, abort_signal)
                            video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{act}.avi'
                            image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{act}', 'extracted_fg_fd')
                            video_path = os.path.join(image_folder, video_name)
                            images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                            print(f"Completed extraction and video creation for subject: {subject}, camera: {camera}, trial: {tr}, activity: {act}")
                            yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'
                    else:
                        extract_fg(DATASET_PATH, subject, camera, tr, int(activity), abort_signal)
                        video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{activity}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{activity}', 'extracted_fg_fd')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        print(f"Completed extraction and video creation for subject: {subject}, camera: {camera}, trial: {tr}, activity: {activity}")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        extract_fg(DATASET_PATH, subject, camera, int(trial), act, abort_signal)
                        video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{act}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{act}', 'extracted_fg_fd')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        print(f"Completed extraction and video creation for subject: {subject}, camera: {camera}, trial: {trial}, activity: {act}")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'
                else:
                    extract_fg(DATASET_PATH, subject, camera, int(trial), int(activity), abort_signal)
                    video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{activity}.avi'
                    image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{activity}', 'extracted_fg_fd')
                    video_path = os.path.join(image_folder, video_name)
                    images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                    print(f"Completed extraction and video creation for subject: {subject}, camera: {camera}, trial: {trial}, activity: {activity}")
                    yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'
        except FileNotFoundError as e:
            yield f'data: {str(e)}\n\n'
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/extract_fg_yolo', methods=['POST'])
def extract_fg_yolo_api():
    global abort_signal
    abort_signal.clear()
    data = request.get_json()
    subject = data.get('subject')
    trial = data.get('trial')
    
    def generate():
        try:
            if trial == 'all':
                for tr in range(1, 4):
                    for camera in range(1, 3):
                        for action in range(1, 12):
                            if abort_signal.is_set():
                                break
                            extract_fg_yolo(DATASET_PATH, subject, camera, tr, action, abort_signal)
                            video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{action}.avi'
                            image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{action}', 'extracted_fg_yolo')
                            video_path = os.path.join(image_folder, video_name)
                            images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                            yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, action {action}\n\n'
            else:
                for camera in range(1, 3):
                    for action in range(1, 12):
                        if abort_signal.is_set():
                            break
                        extract_fg_yolo(DATASET_PATH, subject, camera, int(trial), action, abort_signal)
                        video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{action}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{action}', 'extracted_fg_yolo')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, action {action}\n\n'
        except FileNotFoundError as e:
            yield f'data: {str(e)}\n\n'
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_extract_fg_fd', methods=['POST'])
def stop_extract_fg_fd():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'Foreground extraction using FD has been stopped.'}), 200

@app.route('/api/stop_extract_fg_yolo', methods=['POST'])
def stop_extract_fg_yolo():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'Foreground extraction using YOLO has been stopped.'}), 200

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
                            create_shi(method, DATASET_PATH, subject, camera, tr, act, abort_signal)
                            video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{act}.avi'
                            image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{act}', 'shi')
                            video_path = os.path.join(image_folder, video_name)
                            images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                            yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'
                    else:
                        create_shi(method, DATASET_PATH, subject, camera, tr, int(activity), abort_signal)
                        video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{activity}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{activity}', 'shi')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        create_shi(method, DATASET_PATH, subject, camera, int(trial), act, abort_signal)
                        video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{act}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{act}', 'shi')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'
                else:
                    create_shi(method, DATASET_PATH, subject, camera, int(trial), int(activity), abort_signal)
                    video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{activity}.avi'
                    image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{activity}', 'shi')
                    video_path = os.path.join(image_folder, video_name)
                    images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                    yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'
        except FileNotFoundError as e:
            yield f'data: {str(e)}\n\n'
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_create_shi', methods=['POST'])
def stop_create_shi():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'SHI creation has been stopped.'}), 200

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
                            extract_color_dof(DATASET_PATH, subject, camera, tr, act)
                            video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{act}.avi'
                            image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{act}', 'extracted_dof')
                            video_path = os.path.join(image_folder, video_name)
                            images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                            yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'
                    else:
                        extract_color_dof(DATASET_PATH, subject, camera, tr, int(activity))
                        video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{activity}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{activity}', 'extracted_dof')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        extract_color_dof(DATASET_PATH, subject, camera, int(trial), act)
                        video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{act}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{act}', 'extracted_dof')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'
                else:
                    extract_color_dof(DATASET_PATH, subject, camera, int(trial), int(activity))
                    video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{activity}.avi'
                    image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{activity}', 'extracted_dof')
                    video_path = os.path.join(image_folder, video_name)
                    images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                    yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'
        except FileNotFoundError as e:
            yield f'data: {str(e)}\n\n'
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_extract_dof', methods=['POST'])
def stop_extract_dof():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'DOF extraction has been stopped.'}), 200

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
                            fuse_DOF_SHI(DATASET_PATH, subject, camera, tr, act, method)
                            video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{act}.avi'
                            image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{act}', 'dof_shi')
                            video_path = os.path.join(image_folder, video_name)
                            images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                            yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {act}\n\n'
                    else:
                        fuse_DOF_SHI(DATASET_PATH, subject, camera, tr, int(activity), method)
                        video_name = f'subject{subject}_camera{camera}_trial{tr}_activity{activity}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{tr}', f'Activity_{activity}', 'dof_shi')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {tr}, activity {activity}\n\n'
            else:
                if activity == 'all':
                    for act in range(1, 12):
                        if abort_signal.is_set():
                            break
                        fuse_DOF_SHI(DATASET_PATH, subject, camera, int(trial), act, method)
                        video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{act}.avi'
                        image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{act}', 'dof_shi')
                        video_path = os.path.join(image_folder, video_name)
                        images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                        yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'
                else:
                    fuse_DOF_SHI(DATASET_PATH, subject, camera, int(trial), int(activity), method)
                    video_name = f'subject{subject}_camera{camera}_trial{trial}_activity{activity}.avi'
                    image_folder = os.path.join(app.config['OUTPUT_FOLDER'], f'Subject_{subject}', f'Camera_{camera}', f'Trial_{trial}', f'Activity_{activity}', 'dof_shi')
                    video_path = os.path.join(image_folder, video_name)
                    images_to_video(image_folder, video_path, fps=30, image_format=".png", codec="DIVX")
                    yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'
        except FileNotFoundError as e:
            yield f'data: {str(e)}\n\n'
            return

    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/stop_create_dof_shi', methods=['POST'])
def stop_create_dof_shi():
    global abort_signal
    abort_signal.set()
    return jsonify({'message': 'DOF SHI creation has been stopped.'}), 200

# Serve files dynamically from the output folder
@app.route('/output/<path:filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Serve files dynamically from the output folder
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

# Serve files dynamically from the output folder
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
        'Fall Detection and Classification with Multiple Cameras Based on Features Fusion and CNN-LST',
        'http://127.0.0.1:5000'
    )
    webview.start()
    os._exit(0)
