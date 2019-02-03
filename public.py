from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('public/index.html')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0', port='5001')
