import os
import webview
import threading
import logging

from flask import Flask, render_template, request, jsonify, url_for, send_from_directory, Response
from utils.create_common_background import create_common_background_image
from utils.create_background import create_background_image
from utils.extract_fg_fd import extract_fg
from utils.extract_fg_yolo import extract_fg_yolo


app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['OUTPUT_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))

# Configure logging
logging.basicConfig(level=logging.DEBUG)

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
    dataset_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'UP_Fall_Dataset',
            'Common Background Creation'
        )
    )
    
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
    dataset_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'UP_Fall_Dataset'
        )
    )
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
            image_path = create_background_image(dataset_path, cbg_path, subject, camera, trial, str(act))
            image_url = url_for('serve_image', subject=subject, camera=camera, trial=trial, activity=str(act), filename=os.path.basename(image_path))
            image_paths.append(image_url)
        return jsonify({
            'message': 'Background images created successfully for all activities.',
            'images': image_paths
        }), 200
    else:
        image_path = create_background_image(dataset_path, cbg_path, subject, camera, trial, activity)
        print(image_path)
        image_url = url_for('serve_image', subject=subject, camera=camera, trial=trial, activity=activity, filename=os.path.basename(image_path))

        # Return the image path in the response
        return jsonify({
            'message': 'Background image created successfully.',
            'image': image_url
        }), 200

@app.route('/api/extract_fg_fd', methods=['POST'])
def extract_fg_fd():
    data = request.get_json()
    subject = data.get('subject')
    camera = data.get('camera')
    trial = data.get('trial')
    activity = data.get('activity')
    dataset_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'UP_Fall_Dataset'
        )
    )
    
    def generate():
        if activity == 'all':
            for act in range(1, 12):
                extract_fg(dataset_path, subject, camera, trial, act)
                yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {act}\n\n'
        else:
            extract_fg(dataset_path, subject, camera, trial, int(activity))
            yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, activity {activity}\n\n'
    return Response(generate(), mimetype='text/event-stream')

@app.route('/api/extract_fg_yolo', methods=['POST'])
def extract_fg_yolo_api():
    data = request.get_json()
    subject = data.get('subject')
    dataset_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            '..',
            'UP_Fall_Dataset'
        )
    )
    
    def generate():
        for camera in range(1, 3):
            for trial in range(1, 4):
                for action in range(1, 12):
                    extract_fg_yolo(dataset_path, subject, camera, trial, action)
                    yield f'data: Processing subject {subject}, camera {camera}, trial {trial}, action {action}\n\n'
    return Response(generate(), mimetype='text/event-stream')

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

# def run_flask():
#     app.run(debug=True, use_reloader=False)

# if __name__ == '__main__':
#     flask_thread = threading.Thread(target=run_flask)
#     flask_thread.start()

#     webview.create_window(
#         'Fall Detection and Classification with Multiple Cameras Based on Features Fusion and CNN-LST',
#         'http://127.0.0.1:5000'
#     )
#     webview.start()
#     os._exit(0)
