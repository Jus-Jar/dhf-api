import os
from os.path import join

from praatio import textgrid
from praatio import audio

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


# def pratt_open_textgrid():

#     inputPath =  'examples'+ '\files'
#     outputPath = inputPath + "\generated_textgrids"

#     if not os.path.exists(outputPath):
#         os.mkdir(outputPath)

#     for fn in os.listdir(inputPath):
#         name, ext = os.path.splitext(fn)
#         if ext != ".wav":
#             continue
        
#         duration = audio.getDuration(join(inputPath, fn))
#         wordTier = textgrid.IntervalTier('words', [], 0, duration)
        
#         tg = textgrid.Textgrid()
#         tg.addTier(wordTier)
#         tg.save(join(outputPath, name + ".TextGrid"), format="short_textgrid", includeBlankSpaces=True)

#     # Did it work?
#     for fn in os.listdir(outputPath):
#         ext = os.path.splitext(fn)[1]
#         if ext != ".TextGrid":
#             continue
#         print(fn)
