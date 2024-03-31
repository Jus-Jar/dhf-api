import os

def store_files(audio_file, text_file):
    try:

        # You must read the file content from the FileStorage objects
        audio_data = audio_file.read()
        text_data = text_file.read().decode('utf-8')  # Assuming text file is utf-8 encoded

        directory = "input"
        if not os.path.exists(directory):
            os.makedirs(directory)

        wav_file_path = os.path.join(directory, "audio.wav")
        txt_file_path = os.path.join(directory, "passage.txt")

        # Write the audio data
        with open(wav_file_path, 'wb') as wav_file:
            wav_file.write(audio_data)

        # Write the text data
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text_data)

        print("Files saved successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
