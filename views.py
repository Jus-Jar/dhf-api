from flask import jsonify, request
from app import app
from controllers import  new_open_audio


@app.route('/api/new', methods=['GET'])
def open_new():
    return new_open_audio(), 201