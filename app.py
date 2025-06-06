from flask import Flask, render_template
from models import db
from auth import auth
from requests import requests
from admin import admin  

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  
@app.route('/')
def index():
    return render_template('index.html')

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(requests, url_prefix='/requests')
app.register_blueprint(admin, url_prefix='/admin')  

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
