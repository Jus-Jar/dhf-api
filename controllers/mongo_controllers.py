from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId
from pydub import AudioSegment

# Connection URI
mongo_uri = 'mongodb://localhost:27017/'
client = MongoClient(mongo_uri)

# Connect to the specific database
db = client['ozzypie_db']

def get_user_object_id(username):
    client = MongoClient('mongodb://localhost:27017/')
    db = client['ozzypie_db']
    collection = db['users']
    
    user_document = collection.find_one({'username': username})
    
    if user_document:
        return user_document['_id']
    else:
        return None



def retrieve_audio_file(db,object_id):
    try:
        output_file_path = "output/output.wav"
        # Create a GridFS object
        fs = gridfs.GridFS(db)

        # Convert the string ID to an ObjectId
        file_id = ObjectId(object_id)

        # Retrieve the stored file by its ID
        file = fs.get(file_id)  # Now using ObjectId to retrieve the file

        with open(output_file_path, 'wb') as output_file:
            output_file.write(file.read())
        
        #Converts .wav file
        audio = AudioSegment.from_file(output_file_path)

        return audio

    except Exception as e:
        return None

def upload_audio_file(file_path, audio_filename):
    # Create a GridFS object
    try:
        fs = gridfs.GridFS(db)
        audio_filename = file_path.split('/')[-1]

        # Open the audio file you want to store
        with open(file_path, 'rb') as audio_file:
            # Store the file in GridFS
            file_id = fs.put(audio_file, filename=audio_filename)

        return file_id
    except Exception as e:
        return None

def create_new_dhf_lesson(user, assessment_name, reading_level, updated_final_words_durations, audio_filepath, words_from_file, audio_file_name, word_durations, word_durations_s, initial_silence_duration):

    try:
        
        mongo_uri = 'mongodb://localhost:27017/'
        client = MongoClient(mongo_uri)
        db = client['ozzypie_db']

        collection = db['dhf_reading_lessons']

        audio_id = upload_audio_file(audio_filepath,audio_file_name)
        user_id = get_user_object_id(user)

        if audio_id:
            # # Insert a document into the collection
            new_lesson = {
                'user_id' : user_id,
                'assessment_name': assessment_name,
                'reading_level': reading_level,
                'updated_final_words_durations': updated_final_words_durations,
                'audio_file_ID': audio_id,
                'words_from_file': words_from_file,
                'word_durations': word_durations,
                'word_durations_s': word_durations_s,
                'initial_silence_duration' : initial_silence_duration
                
            }

            collection.insert_one(new_lesson)
            return True
        
        return False
    
    except Exception as e:
        return False

def get_reading_assessments(username):   
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['ozzypie_db']
        collection = db['dhf_reading_lessons']

        user_id = get_user_object_id(username)

        # Find Reading lessons for the current user
        assessments = collection.find({"user_id": user_id}, {"assessment_name": 1})

        # Extracting the names and IDs
        assessments_info = [{"id": str(assessment["_id"]), "name": assessment['assessment_name']} for assessment in assessments]
        return assessments_info
    
    except Exception as e:
        return None

def get_reading_assessment_by_id(id):
    try:
        client = MongoClient('mongodb://localhost:27017/')
        db = client['ozzypie_db']
        collection = db['dhf_reading_lessons']

        assessment = collection.find_one({"_id": ObjectId(id)})
        audio_file =retrieve_audio_file(db,assessment['audio_file_ID'])

        if assessment:
            # Remove _id and audio_file_ID from the dictionary
            assessment.pop('_id', None)
            assessment.pop('user_id', None)
            assessment.pop('audio_file_ID', None)

        print(audio_file)

        return {
            'assessment' : assessment,
        }
    
    except Exception as e:
        return print(e)

