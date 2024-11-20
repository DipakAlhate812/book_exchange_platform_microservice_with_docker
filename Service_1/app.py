from flask import Flask
from routes import auth_bp
import os
from db import db  
from routes import SECRET_KEY
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/auth/*": {"origins": "http://localhost:3000"}}) # Configuration for SQLite

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.secret_key = SECRET_KEY

db.init_app(app)

# Register the auth blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True,host='0.0.0.0', port=8001)
