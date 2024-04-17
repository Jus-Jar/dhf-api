from flask import jsonify, request, send_file
from app import app
from controllers.controllers import  new_open_audio
from controllers.analysis_contollers import analyze
from controllers.file_controllers import store_files
from controllers.mongo_controllers import get_reading_assessments, get_reading_assessment_by_id

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
    result = new_open_audio(audio_file_name, text_file_name, audio_file, text_file, assessment_name, reading_level, user)


    return jsonify(result), 201

@app.route('/api/readingAssessments/<username>', methods=['GET'])
def retrieve_assessments_names(username):
    reading_assessments = get_reading_assessments(username)
    return jsonify(reading_assessments), 200

@app.route('/api/readingAssessment', methods=['POST'])
def retrieve_reading_assessment():
    assessment_id = request.form.get('assessment_id')
    reading_lesson = get_reading_assessment_by_id(assessment_id)
    # return jsonify(reading_lesson), 200
    return jsonify(reading_lesson),200

@app.route('/api/audio', methods=['GET'])
def serve_audio_file():
    # Assuming retrieve_audio_file saves the audio to 'output/output.wav'
    output_file_path = "output\\output.wav"
    return send_file(output_file_path, mimetype='audio/wav'), 200