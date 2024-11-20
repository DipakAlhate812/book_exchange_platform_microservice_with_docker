from flask import Blueprint, request, jsonify, make_response
from models import User, Token
from db import db  # Import the db from the new fileimport jwt
import datetime
import os
import jwt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from functools import wraps
from flask import request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()
auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv("SECRET_KEY")

def generate_otp():
    return random.randint(100000, 999999)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({'message': 'Authorization token is missing or invalid'}), 401
        try:
            token = auth_header.split(" ")[1]
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user_id = decoded_token.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated


@auth_bp.route('/test')
def get_user_profile():
    print("Hello World")
    response = requests.get("http://127.0.0.1:8001/test")
    return {"success": "Success"}

# Sign-up route
@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({'message': 'Missing fields'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if user:
        return jsonify({'message': 'User already exists'}), 400

    new_user = User(
        name=data['name'],
        email=data['email'],
    )

    new_user.set_password(data['password'])
    
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User created successfully'}), 201


# Login route
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print("2",data)

    if not data.get('email') or not data.get('password'):
        return jsonify({'message': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    print("2", user.query.count())
    if user and user.check_password(data['password']):
        print("3", user.query.count())
        print(SECRET_KEY)
        # Generate JWT tokens
        token = jwt.encode({
            'user_email': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)
        }, os.getenv("SECRET_KEY"))
        print("2")

        refresh_token = jwt.encode({
            'user_email': user.email,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        }, os.getenv("SECRET_KEY"))
        print("2")

        # Save tokens to the database
        new_token = Token(email=user.email, token=token, refresh_token=refresh_token)
        db.session.add(new_token)
        db.session.commit()
        print("2")

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'refresh_token': refresh_token
        }), 200
    
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# Forgot password route
@auth_bp.route('/send-otp', methods=['POST'])
def forgot_password():
    data = request.get_json()
    if not data.get('email'):
        return jsonify({'message': 'Email field is missing'}), 400

    # Look for the user by email
    user = User.query.filter_by(email=data['email']).first()

    if not user:
        return jsonify({'message': 'User with this email does not exist'}), 404
     # Generate OTP and expiration time
    otp = generate_otp()
    otp_expiration = datetime.datetime.utcnow() + datetime.timedelta(minutes=2)  # OTP valid for 5 minutes

    # Store the OTP and expiration in the Token table (or a separate OTP table if needed)
    new_token = Token(email=user.email, 
                      token=None,  
                      refresh_token=None,
                      otp=str(otp), 
                      otp_expires_at=otp_expiration) 
    
    db.session.add(new_token)
    db.session.commit()

    try:
        response = requests.post("http://service_2:8002/api/notify", json={
            "actionType": "Password Reset- OTP Sent",
            'email': user.email,
            'details': otp
        })
        response.raise_for_status()  # Raise an exception for HTTP errors

    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Failed to send OTP email', 'error': str(e)}), 500

    return jsonify({
        'message': 'OTP sent successfully. Please check your email.',
        'otp': otp  # For testing purposes, you can remove this in production
    }), 200

# Reset password route
@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    if not data.get('otp') or not data.get('password'):
        return jsonify({'message': 'OTP and new password fields are required'}), 400

    print(data)
    # Get the user ID from the token
    email = data.get("email")

    # Look for the user by user email
    user = User.query.filter_by(email=email).first()    
    print(user)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Look for the OTP and validate it
    otp_entry = Token.query.filter_by(email=user.email, otp=data['otp']).first()
    if not otp_entry or otp_entry.otp_expires_at < datetime.datetime.utcnow():
        return jsonify({'message': 'Invalid or expired OTP'}), 400

    # Update the user's password
    user.set_password(data['password'])  # Replace with your password hashing logic

    # Delete the used OTP to prevent reuse
    db.session.delete(otp_entry)
    db.session.commit()


    try:
        response = requests.post("http://service_2:8002/api/notify", json={
            "actionType": "Password has been reset",
            'email': user.email,
            'details': "Password has been reset"
        })
        response.raise_for_status()  # Raise an exception for HTTP errors

    except requests.exceptions.RequestException as e:
        return jsonify({'message': 'Failed to reset password.', 'error': str(e)}), 500

    return jsonify({'message': 'Password has been reset successfully'}), 200


# API to delete a user by ID
# Delete user route with JWT validation
@auth_bp.route('/user/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    # Validate that the user making the request matches the user being deleted
    data = request.get_json()
    print("asdas")
    # Find the user by ID
    user = User.query.get(user_id)
    print("asdas")
    if not user:
        return make_response(jsonify({"error": "User not found"}), 404)

    try:
        # First, delete all associated tokens
        Token.query.filter_by(email=data["email"]).delete()

        # Then, delete the user
        db.session.delete(user)
        db.session.commit()

        return make_response(jsonify({"message": "User and associated tokens deleted successfully"}), 200)

    except Exception as e:
        db.session.rollback()  # Rollback if something goes wrong
        return make_response(jsonify({"error": str(e)}), 500)
    
    
@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Extract the token from the Authorization header (assuming it's a Bearer token)
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 400
        
        # Split to get token from "Bearer token"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({"error": "Invalid authorization header format"}), 400
        
        token = parts[1]

        # Find the token in the database
        token_entry = Token.query.filter_by(token=token).first()

        if token_entry:
            # Delete the token from the database
            db.session.delete(token_entry)
            db.session.commit()
            return jsonify({"message": "Logout successful, token removed from server"}), 200
        else:
            return jsonify({"error": "Token not found"}), 400
    
    except Exception as e:
        # Return error message in case of unexpected issues
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500
