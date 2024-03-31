import os
from os.path import join

from praatio import textgrid
from praatio import audio

import requests
import xml.etree.ElementTree as ET


# Define the API endpoint
url = "https://clarin.phonetik.uni-muenchen.de/BASWebServices/services/runMAUSBasic"

def generate_text_grid(url):
    # Prepare the payload
    payload = {
        'LANGUAGE': 'eng-US',  # Adjust the language code according to your needs
        'OUTFORMAT': 'TextGrid',
    }
    files = {
        'SIGNAL': ('audio.wav', open('input\sentence1.wav', 'rb'), 'audio/wav'),
        'TEXT': ('transcript.txt', open('input\sentences1.txt', 'rb'), 'text/plain'),
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



inputFN = generate_text_grid(url)
tg = textgrid.openTextgrid(inputFN, includeEmptyIntervals=False)
print(tg.getTier(tg.tierNames[0]))

wordTier = tg.getTier('ORT-MAU')
# I just want the labels from the entries
labelList = [entry.label for entry in wordTier.entries]
print(labelList)

# Get the duration of each interval
# (in this example, an interval is a word, so this outputs word duration)
durationList = []
for start, stop, _ in wordTier.entries:
    durationList.append(stop - start)

print(durationList)