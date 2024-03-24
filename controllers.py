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
    chunk_start = index * chunk_length_ms
    chunk_hash = hashlib.md5(chunk.raw_data).hexdigest()  # Generate a unique hash for this chunk
    cache_file = f"cache_{chunk_hash}.json"  # Cache file based on the chunk's hash

    # Check if we already processed this chunk before and saved its results
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as file:
            print(f"Retrieving cached results for chunk {index}")
            return json.load(file)  # Return the cached results

    chunk_name = f"chunk{index}.wav"
    chunk.export(chunk_name, format="wav")  # Export the audio chunk to a WAV file

    recognizer = sr.Recognizer()  # Initialize the recognizer
    words_durations = []  # List to store the (word, start_time, end_time) tuples

    # Use the SpeechRecognition library to convert the audio to text
    with sr.AudioFile(chunk_name) as source:
        audio_listened = recognizer.record(source)  # Listen to the audio file
        try:
            text = recognizer.recognize_google(audio_listened)  # Use Google Web Speech API to decode the audio
            words = text.split()  # Split the recognized text into words
            chunk_duration = len(chunk)  # Get the duration of the chunk in milliseconds
            word_duration = chunk_duration / len(words) if words else 0  # Calculate the duration of each word

            # Calculate the start and end times for each word
            for j, word in enumerate(words):
                word_start = chunk_start + j * word_duration
                word_end = word_start + word_duration
                words_durations.append((word, word_start, word_end))  # Add the word's details to the list

            # Cache the results to avoid reprocessing in the future
            with open(cache_file, 'w') as file:
                json.dump(words_durations, file)

        except sr.UnknownValueError:
            print(f"Chunk {index}: SpeechRecognition could not understand audio")
        except sr.RequestError as e:
            print(f"Chunk {index}: Could not request results from SpeechRecognition service; {e}")

    return words_durations

def new_open_audio(audio_file_name , text_file_name):
    # Load and preprocess audio
    audio = AudioSegment.from_file(f'input\{audio_file_name}')
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export("temp.wav", format="wav")

    # Determine chunks
    chunk_length_ms = 30000  # milliseconds
    chunks = make_chunks(audio, chunk_length_ms)

    # Prepare for parallel processing
    final_words_durations = []
    default_workers = os.cpu_count() * 5  # Determine the number of parallel workers

    # Process audio chunks in parallel
    with ThreadPoolExecutor(max_workers=default_workers) as executor:
        futures = [executor.submit(process_chunk, chunk, i, chunk_length_ms) for i, chunk in enumerate(chunks)]
        for future in futures:
            final_words_durations.extend(future.result())

    # Read words from the text file
    words_from_file = read_words_from_file(text_file_name)

    # Update final_words_durations with match information
    updated_final_words_durations = []  # Use a new list to store the dictionaries
    for i, (word, start, end) in enumerate(final_words_durations):
        if i < len(words_from_file):
            # Convert each tuple into a dictionary, and add 'match' information
            match = compare_words(word, words_from_file[i])
            updated_final_words_durations.append({
                'word': word,
                'start': start,
                'end': end,
                'match': match
            })
        else:
            # If no corresponding word in the text file, assume no match
            updated_final_words_durations.append({
                'word': word,
                'start': start,
                'end': end,
                'match': False
            })

    # Print updated final_words_durations with match information
    for word_info in updated_final_words_durations:
        print(f"Word: {word_info['word']}, Start: {word_info['start']}, End: {word_info['end']}, Match: {word_info['match']}")

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
    text_file_path = f'input\{text_file_name}'  # Replace with your text file path


    
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
