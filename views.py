from flask import jsonify, request
from app import app
from controllers.controllers import  new_open_audio, analyzeVoice
from controllers.file_controllers import store_files

@app.route('/api/new', methods=['POST'])
def open_new():
    audio_file_name = request.form.get('audioFileName')
    text_file_name = request.form.get('textFileName')
    audio_file = request.files.get('audioFile')
    text_file = request.files.get('textFile')
    assessment_name = request.form.get('assessmentName')
    reading_level = request.form.get('readingLevel')
    user = request.form.get('user')
    

    # Print the file names
    print(f"Received audio file name: {audio_file_name}")
    print(f"Received text file name: {text_file_name}")
    print(f"Received audio file : {audio_file}")
    print(f"Received text file : {text_file}")
    print(f"Assessment Name : {assessment_name}")
    print(f"Reading Level : {reading_level}")
    print(f"User : {user}")
    

    store_files(audio_file,text_file)
    result = new_open_audio(audio_file_name, text_file_name)


    return jsonify(result), 201

@app.route('/api/analysis', methods=['POST'])
def analyze_voice():
    audio_file_name = request.form.get('audioFileName')
    text_file_name = request.form.get('textFileName')

    # Print the file names
    print(f"Received audio file name: {audio_file_name}")
    print(f"Received text file name: {text_file_name}")
    result = analyzeVoice(audio_file_name , text_file_name )
    return "Success", 201
