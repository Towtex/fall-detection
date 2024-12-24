import os
import webview
import threading

from flask import Flask, render_template, request, jsonify
from utils.Create_common_background import create_common_background_image

app = Flask(__name__, static_folder='static', template_folder='templates')

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

@app.route('/training')
def training():
    return render_template('training.html', active_page='training')

@app.route('/testing')
def testing():
    return render_template('testing.html', active_page='testing')

### API routes
@app.route('/api/create_common_background', methods=['POST'])
def create_common_background():
    data = request.get_json()
    camera = data.get('camera')
    condition = data.get('condition')
    fld_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__),
        '..',
        'UP_Fall_Dataset',
        'Common Background Creation'
        ))
    
    create_common_background_image(fld_path, condition=f'Camera{camera}_Con{condition}')
    return jsonify({'message': 'Common background created successfully'}), 200

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
