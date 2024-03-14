import os
from pydub import AudioSegment
from os.path import join

from praatio import textgrid
from os.path import join, splitext, isfile
from praatio import audio


import json
from vosk import Model, KaldiRecognizer
import wave



def pratt_create_textgrid():
    
    # Textgrids take no arguments--it gets all of its necessary attributes from the tiers that it contains.
    tg = textgrid.Textgrid()
    
    # IntervalTiers and PointTiers take four arguments: the tier name, a list of intervals or points,
    # a starting time, and an ending time.
    wordTier = textgrid.IntervalTier('words', [], 0, 1.0)
    maxF0Tier = textgrid.PointTier('maxF0', [], 0, 1.0)

    tg.addTier(wordTier)
    tg.addTier(maxF0Tier)

    tg.save("empty_textgrid.TextGrid", format="short_textgrid", includeBlankSpaces=True)
    

    return "Function is working"


def pratt_save_textgrid():
    inputPath = 'C:\\Users\\Avinash Roopnarine\\Desktop\\Input'
    outputPath = 'C:\\Users\\Avinash Roopnarine\\Desktop\\Output'

    if not os.path.exists(outputPath):
        os.mkdir(outputPath)

    for fn in os.listdir(inputPath):
        name, ext = splitext(fn)
        # Check for supported audio formats
        if ext.lower() not in [".wav", ".m4a", ".mp3"]:
            continue

        # Load the audio file, pydub can handle different formats based on the file extension
        audio_file_path = join(inputPath, fn)
        audio = AudioSegment.from_file(audio_file_path, format=ext.replace('.', ''))

        # Convert to mono if not already
        if audio.channels > 1:
            audio = audio.set_channels(1)  # Convert to mono

        # Note: no need to save and remove a temporary mono file, just use the audio object directly

        # Use the audio object for duration extraction
        duration = len(audio) / 1000.0  # Duration in seconds (pydub uses milliseconds)

        wordTier = textgrid.IntervalTier('words', [], 0, duration)
        
        tg = textgrid.Textgrid()
        tg.addTier(wordTier)
        tg.save(join(outputPath, name + ".TextGrid"), format="short_textgrid", includeBlankSpaces=True)

    # Check the output
    for fn in os.listdir(outputPath):
        ext = splitext(fn)[1]
        if ext != ".TextGrid":
            continue
        print(fn)
        
    return "Success"

def pratt_open_textgrid():
    outputDir = 'C:\\Users\\Avinash Roopnarine\\Desktop\\Output'  # Replace with your output folder

    # Variables to hold your single TextGrid object and its filename
    singleTG = None
    tgFilename = ''

    # Iterate through each file in the output directory
    for filename in os.listdir(outputDir):
        # Check if the file is a TextGrid file
        if isfile(join(outputDir, filename)) and splitext(filename)[1].lower() == '.textgrid':
            # Construct the full file path
            fullPath = join(outputDir, filename)
            
            # Try opening the TextGrid file
            try:
                tg = textgrid.openTextgrid(fullPath, includeEmptyIntervals=False)
                singleTG = tg  # Store the TextGrid object
                tgFilename = filename  # Store the filename
                print(f"Loaded TextGrid: {filename}")
                break  # Exit the loop after the first TextGrid file is found
            except Exception as e:
                print(f"Could not load {filename}: {e}")
                
    # If a TextGrid was successfully loaded
    if singleTG:
        wordTier = singleTG.getTier('words')  # Get the 'words' tier
        if wordTier.entries:  # Check if there are any intervals
            print(f"Intervals in 'words' tier of {tgFilename}:")
            for interval in wordTier.entries:  # Iterate through intervals
                start, end, text = interval
                print(f"Start: {start}, End: {end}, Text: '{text}'")
        else:
            print(f"No intervals found in 'words' tier of {tgFilename}")
        
        # Attempt to get the 'words' tier and print its intervals
        try:
            wordTier = singleTG.getTier('words')  # Replace 'words' with the correct tier name if different
            print(f"Intervals in 'words' tier of {tgFilename}:")
            for interval in wordTier.entries:
                start, end, text = interval
                duration = end - start
                print(f"Start: {start}, End: {end}, Duration: {duration}, Text: '{text}'")
        except ValueError:
            print(f"'words' tier not found in {tgFilename}")

    return "Success" if singleTG else "No TextGrid files found"


def vosk_open_audio():
    model = Model("C:\\Users\\Avinash Roopnarine\\Desktop\\vosk-model-small-en-us-0.15")
    
    input_audio_path = "C:\\Users\\Avinash Roopnarine\\Desktop\\Input\\arth_mb.wav"  # Replace 'your_original_audio_file.ext' with your file's name and extension
    output_audio_path = "C:\\Users\\Avinash Roopnarine\\Desktop\\Output\\arth_mb.wav"  # Name your output file

    convert_audio(input_audio_path, output_audio_path)
    
    # Open your audio file
    wf = wave.open("C:\\Users\\Avinash Roopnarine\\Desktop\\Output\\arth_mb.wav", "rb")
     
   

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

    results.append(json.loads(rec.FinalResult()))

    # Print the words and their start and end times
    for result in results:
        if 'result' in result:  # Check if there are words detected
            for word_info in result['result']:
                print(f"Word: {word_info['word']}, Start: {word_info['start']}, End: {word_info['end']}")
                
    return "Success"

def convert_audio(input_path, output_path):
    # Load the audio file
    audio = AudioSegment.from_file(input_path)

    # Convert the audio to 16kHz mono
    audio = audio.set_frame_rate(16000).set_channels(1)

    # Export the converted audio
    audio.export(output_path, format="wav")