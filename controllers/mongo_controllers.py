from pymongo import MongoClient
import gridfs
from bson.objectid import ObjectId

# Connection URI
mongo_uri = 'mongodb://localhost:27017/'
client = MongoClient(mongo_uri)

# Connect to the specific database
db = client['ozzypie_db']

def retrieve_audio_file(db,object_id,output_file_path):  
    try:
        # Create a GridFS object
        fs = gridfs.GridFS(db)

        # Convert the string ID to an ObjectId
        file_id = ObjectId("6608bfe5ec888042a714458a")

        # Retrieve the stored file by its ID
        file = fs.get(file_id)  # Now using ObjectId to retrieve the file

        # # Retrieve the stored file by its ID
        # file = fs.get("6608bfe5ec888042a714458a")  # or use fs.find_one({'filename': 'myaudiofile.mp3'}) to retrieve by filename

        # Save or process the retrieved file
        # output_file_path = 'input/test.mp3'
        with open(output_file_path, 'wb') as output_file:
            output_file.write(file.read())

        return output_file_path

    except Exception as e:
        return None

def upload_audio_file(file_path):
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

def create_new_dhf_lesson(db,user_id, assessment_name,reading_level,audio_data,audio_file_path,text_data):

    try:
        collection = db['dhf_reading_lessons']
        audio_id = upload_audio_file(audio_file_path)

        if audio_id:
            # # Insert a document into the collection
            new_lesson = {
                'assessment_name': assessment_name,
                'reading_level': reading_level,
                'audio_file_ID': audio_id,
                'audio_data': audio_data,
                'text_data' : text_data,
                'user_id' : user_id
            }

            collection.insert_one(new_lesson)
            return True
        
        return False
    
    except Exception as e:
        return False
