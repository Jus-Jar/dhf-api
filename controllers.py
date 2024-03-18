import os
from pydub import AudioSegment

from metaphone import doublemetaphone

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

def new_open_audio():
    audio = AudioSegment.from_file("C:\\Users\\Avinash Roopnarine\\Desktop\\Input\\arth_mb.wav")
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export("temp.wav", format="wav")

    chunk_length_ms = 30000  # milliseconds
    chunks = make_chunks(audio, chunk_length_ms)

    final_words_durations = []
    
    default_workers = os.cpu_count() * 5 

    # Using ThreadPoolExecutor to process audio chunks in parallel
    with ThreadPoolExecutor(max_workers=default_workers) as executor:
        futures = [executor.submit(process_chunk, chunk, i, chunk_length_ms) for i, chunk in enumerate(chunks)]
        for future in futures:
            final_words_durations.extend(future.result())

    print(final_words_durations)
    
    return "Success"

    