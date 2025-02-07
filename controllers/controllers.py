import os
from pydub import AudioSegment

from metaphone import doublemetaphone
import string
import hashlib
import json
import speech_recognition as sr
from pydub.utils import make_chunks
from concurrent.futures import ThreadPoolExecutor

from os.path import join

from praatio import textgrid
from praatio import audio

import requests
import xml.etree.ElementTree as ET

from controllers.mongo_controllers import create_new_dhf_lesson


url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runMAUSBasic"


def process_chunk(chunk, index, chunk_length_ms):
    chunk_hash = hashlib.md5(chunk.raw_data).hexdigest()
    cache_file = f"cache_{chunk_hash}.json"

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

def new_open_audio(audio_file_name, passage_name, audio_file, text_file, assessment_name, reading_level, user):
    # Load and preprocess audio
    text_file_name = 'passage.txt'
    audio_path = 'audio.wav'
    audio_path2 = 'input/audio.wav'

    audio = AudioSegment.from_file(audio_path2)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export("temp.wav", format="wav")

    # Determine chunks
    chunk_length_ms = 30000  # milliseconds
    chunks = make_chunks(audio, chunk_length_ms)

    # Process audio chunks using Google Web Speech API
    final_words = []  # This will store only the Google API transcriptions
    with ThreadPoolExecutor(max_workers=os.cpu_count() * 5) as executor:
        futures = [executor.submit(process_chunk, chunk, i, chunk_length_ms) for i, chunk in enumerate(chunks)]
        for future in futures:
            final_words.extend([item['word'] for item in future.result()])

    # Read words from the text file
    words_from_file = read_words_from_file(text_file_name)

    # Get the durations from the TextGrid
    durations =  get_durations(url, audio_path, text_file_name)
    
    word_durations = durations['durations']
    word_durations_s = durations['durations_s']
    
   # Initialize updated_final_words_durations for later use with duration data
    updated_final_words_durations = []

    # Dictionary to track how many times each word has been processed
    word_occurrences_processed = {}

    for word_index, word in enumerate(final_words):
        normalized_word = word.lower()

        # Determine the occurrence of this word instance
        if normalized_word in word_occurrences_processed:
            word_occurrences_processed[normalized_word] += 1
        else:
            word_occurrences_processed[normalized_word] = 1

        current_occurrence = word_occurrences_processed[normalized_word]

        # Find the matching duration for this specific occurrence
        matched_duration = None
        occurrence_counter = 0
        for item in word_durations:
            if item['word'].lower() == normalized_word:
                occurrence_counter += 1
                if occurrence_counter == current_occurrence:
                    matched_duration = item
                    break
        

        # If there's a corresponding word in words_from_file, check for phonetic match
        matched = False
        fallback_timing = None
        if word_index < len(words_from_file):
            matched = compare_words(word, words_from_file[word_index].translate(str.maketrans('', '', string.punctuation)))
            # Use the index to find the corresponding timing from word_durations as fallback
            # if not matched and word_index < len(word_durations):
            fallback_timing = word_durations[word_index]
            print(fallback_timing)  # Fallback timing from the compared word

        # Append the word information with timing information if matched, or fallback timing
        if matched_duration:
            updated_final_words_durations.append({
                'word': word,
                'start': matched_duration['start'],
                'end': matched_duration['end'],
                'match': matched
            })
        elif fallback_timing:
            updated_final_words_durations.append({
                'word': word,
                'start': fallback_timing['start'],
                'end': fallback_timing['end'],
                'match': matched
            })
       


    silences_with_match = [{'word': item['word'], 'start': item['start'], 'end': item['end'], 'match': True} for item in word_durations_s if item['word'] == '[Silence]']

    updated_final_words_durations.extend(silences_with_match)

    updated_final_words_durations_sorted = sorted(updated_final_words_durations, key=lambda x: x['start']) 

    updated_final_words_durations = updated_final_words_durations_sorted
    
    created = create_new_dhf_lesson(user, assessment_name, reading_level, updated_final_words_durations, audio_path2, words_from_file, audio_file_name, word_durations, word_durations_s)

    #this function save the stuff to mongo db <============
    return {
        'audio_data': updated_final_words_durations,
        'text_data': words_from_file,
        'duration_data': word_durations,
        "durarion_data_s": word_durations_s
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


def read_words_from_file(text_file_name):
    # Path to your text file
    text_file_path = f'input\{text_file_name}'  # Replace with your text file path

    # List to store words
    words_list = []
    
    # Open and read the text file
    try: 
        with open(text_file_path, 'r') as file:
            for line in file:
                # Remove punctuation except apostrophes and split each line into words
                clean_line = line
                words_list.extend(clean_line.split())
    except Exception as error:
        print('Error reading text file:', error)
        return []  # Return an empty list in case of error
    
    print(words_list)
    
    # Return the list of words
    return words_list


def generate_text_grid(url,audio_file_name , text_file_name):
    # Prepare the payload
    payload = {
        'LANGUAGE': 'eng-US',  # Adjust the language code according to your needs
        'OUTFORMAT': 'TextGrid',
    }
    files = {
        'SIGNAL': ('audio.wav', open(f'input\{audio_file_name }', 'rb'), 'audio/wav'),
        'TEXT': ('transcript.txt', open(f'input\{text_file_name}', 'rb'), 'text/plain'),
    }

    # Make the request
    response = requests.post(url, data=payload, files=files)

    # Parse the string
    root = ET.fromstring(response.content)

    # Extract the download link
    download_link = root.find('.//downloadLink').text

    response = requests.get(download_link)

    # Check if the request was successful
    if response.status_code == 200:
        # Save the TextGrid to a file
        with open('input/output.TextGrid', 'wb') as file:
            file.write(response.content)
            return "input/output.TextGrid"
    else:
        return False
    
def get_durations(url, audio_file_name, text_file_name):
    inputFN = generate_text_grid(url, audio_file_name, text_file_name)
    tg = textgrid.openTextgrid(inputFN, includeEmptyIntervals=False)
    
    tg1 = textgrid.openTextgrid(inputFN, includeEmptyIntervals=True)
    
    wordTier = tg.getTier('ORT-MAU')
    
    wordTier_S = tg1.getTier('ORT-MAU')
    
    
    word_durations = [
        {
            'word': entry.label, 
            'start': int(entry.start * 1000),
            'end': int(entry.end * 1000)
        }
        for entry in wordTier.entries
    ]
    
    
    word_durations_S = [
        {
            'word': entry.label if entry.label else "[Silence]",  # Use "[Silence]" for empty labels
            'start': int(entry.start * 1000),
            'end': int(entry.end * 1000)
        }
        for entry in wordTier_S.entries
    ]

    return {
        'durations' : word_durations,
        'durations_s' : word_durations_S
    }


            
        
        
         