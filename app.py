from flask import Flask, render_template


app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)