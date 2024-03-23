from flask import jsonify, request
from app import app
from controllers import  new_open_audio


@app.route('/api/new', methods=['POST'])
def open_new():
    audio_file_name = request.form.get('audioFileName')
    text_file_name = request.form.get('textFileName')

    # Print the file names
    print(f"Received audio file name: {audio_file_name}")
    print(f"Received text file name: {text_file_name}")
    result = new_open_audio(audio_file_name, text_file_name)
    return jsonify(result), 201