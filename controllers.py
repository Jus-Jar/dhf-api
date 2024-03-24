import os
from pydub import AudioSegment

from metaphone import doublemetaphone
import string
import hashlib
import json
import speech_recognition as sr
from pydub.utils import make_chunks
from concurrent.futures import ThreadPoolExecutor



def process_chunk(chunk, index, chunk_length_ms):
    chunk_hash = hashlib.md5(chunk.raw_data).hexdigest()
    cache_file = f"cache_{chunk_hash}.json"

    # Check if this chunk has been processed before
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            print(f"Retrieving cached results for chunk {index}")
            return json.load(file)  # Return cached results without reprocessing

    # If not cached, process the chunk
    chunk_name = f"chunk{index}.wav"
    chunk.export(chunk_name, format="wav")  # Export the audio chunk to a WAV file
    recognizer = sr.Recognizer()

    with sr.AudioFile(chunk_name) as source:
        audio_listened = recognizer.record(source)  # Listen to the audio file
        try:
            # Perform speech recognition using Google's Web Speech API
            text = recognizer.recognize_google(audio_listened)
            words = text.split()  # Split the recognized text into words

            # Store recognized words without calculating durations
            recognized_data = [{'word': word} for word in words]

            # Cache the results to avoid reprocessing in the future
            with open(cache_file, 'w') as file:
                json.dump(recognized_data, file)

            return recognized_data
        except sr.UnknownValueError:
            print(f"Chunk {index}: SpeechRecognition could not understand audio")
        except sr.RequestError as e:
            print(f"Chunk {index}: Could not request results from SpeechRecognition service; {e}")

    return []


def new_open_audio(audio_file_name , text_file_name):
    # Load and preprocess audio
    audio_path = f'C:\\Users\\Avinash Roopnarine\\Desktop\\Input\\{audio_file_name}'
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export("temp.wav", format="wav")

    # Determine chunks
    chunk_length_ms = 30000  # milliseconds
    chunks = make_chunks(audio, chunk_length_ms)

    # Use Vosk to get word timestamps, but not the transcription
    vosk_data = vosk_open_audio('temp.wav')

    # Process audio chunks using Google Web Speech API
    final_words = []  # This will store only the Google API transcriptions
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
        futures = [executor.submit(process_chunk, chunk, i, chunk_length_ms) for i, chunk in enumerate(chunks)]
        for future in futures:
            # Note: Now expecting dictionaries with 'word' keys
            final_words.extend([item['word'] for item in future.result()])

    # Read words from the text file
    words_from_file = read_words_from_file(text_file_name)

    # Initialize updated_final_words_durations for later use with Vosk data
    updated_final_words_durations = [{'word': word} for word in final_words]  # Prepare for Vosk data

    # Assuming 'updated_final_words_durations' and 'vosk_data' lists correspond one-to-one
    for vosk_info, updated_info in zip(vosk_data, updated_final_words_durations):
        updated_info['start'] = vosk_info['start']
        updated_info['end'] = vosk_info['end']
        # If words match, update 'match' field, else set it to False
        updated_info['match'] = updated_info['word'] in words_from_file

    # Return final data structure
    return {
        'audio_data': updated_final_words_durations,
        'text_data': words_from_file
    }


# Function to generate Double Metaphone keys for a given word
def generate_double_metaphone(word):
    try:
        # Generate Double Metaphone keys
        primary, secondary = doublemetaphone(word)
        return primary, secondary
    except Exception as error:
        print('Error generating Double Metaphone:', error)
        raise error  # Reraise the error to be caught by the caller

# Function to compare two words based on their Double Metaphone codes
def compare_words(word1, word2):
    word1_code = generate_double_metaphone(word1)
    word2_code = generate_double_metaphone(word2)
    
    # Comparing the Double Metaphone codes
    if word1_code[0] == word2_code[0] or word1_code[1] == word2_code[1] or word1_code[1] == word2_code[0]:
        return True
    return False

# Example function calls (commented out to comply with instruction)
# print(compare_words('example', 'sample'))  # Should analyze the similarity based on phonetics


def read_words_from_file(text_file_name):
    # Path to your text file
    text_file_path = f'C:\\Users\\Avinash Roopnarine\\Desktop\\Input\\{text_file_name}'  # Replace with your text file path
    
    # List to store words
    words_list = []
    
    # Define a translation table to remove punctuation except apostrophes
    remove_punct = str.maketrans('', '', string.punctuation.replace("'", ""))  # Keep apostrophes
    
    # Open and read the text file
    try:
        with open(text_file_path, 'r') as file:
            for line in file:
                # Remove punctuation except apostrophes and split each line into words
                clean_line = line.translate(remove_punct)
                words_list.extend(clean_line.split())
    except Exception as error:
        print('Error reading text file:', error)
        return []  # Return an empty list in case of error
    
    # Return the list of words
    return words_list

from vosk import Model, KaldiRecognizer
import wave


# Below are the modifications and additions to the user's code based on the instructions provided.

# Updating the vosk_open_audio function to collect and return the words with their timestamps
def vosk_open_audio(audio_file):
    # Path to your Vosk model directory
    model_path = "C:\\Users\\Avinash Roopnarine\\Desktop\\vosk-model-small-en-us-0.15"
    model = Model(model_path)
     
    # Open your audio file
    wf = wave.open(audio_file, "rb")

    # Create a recognizer object
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)  # Tell Vosk to return words with timestamps

    # Process the entire audio file
    results = []
    while True:
        data = wf.readframes(4000)  # Read 4000 frames from the file
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            results.append(json.loads(rec.Result()))

    # Add the final result to the results list
    results.append(json.loads(rec.FinalResult()))

    # Prepare a list for the Vosk processed data
    vosk_processed_data = []
    for result in results:
        if 'result' in result:  # Check if there are words detected
            for word_info in result['result']:
                # Convert seconds to milliseconds for consistency with the rest of the system
                start_ms = int(word_info['start'] * 1000)
                end_ms = int(word_info['end'] * 1000)
                vosk_processed_data.append({
                    'word': word_info['word'],
                    'start': start_ms,
                    'end': end_ms
                })
                
    return vosk_processed_data  # Return the list of word information

