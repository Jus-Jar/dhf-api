from controllers.mongo_controllers import get_reading_assessment_by_id

def analyze(id):
    result = get_reading_assessment_by_id(id)
    assessment = result['assessment']  # Get the assessment dictionary

    audio_data = assessment['updated_final_words_durations']
    duration_data = assessment['word_durations_s']
    filtered_audio_data = [item for item in audio_data if item['word'] != '[Silence]']
    
    count = 0
    for item in filtered_audio_data:
        if item['match']:
            count += 1

    accuracy = (count / len(filtered_audio_data)) * 100 

    # To get the last element's end time in duration_data
    if duration_data:
        last_element_end_time = duration_data[-1]['end']  # Access the end time of the last element
        total_duration_minutes = last_element_end_time / (60 * 1000)  # Convert milliseconds to minutes

        if total_duration_minutes > 0:
            words_per_minute = count / total_duration_minutes
        else:
            words_per_minute = 0
    else:
        words_per_minute = 0

    #Standard 1 
    slow = 44.5 
    medium = 75
    
    # Assuming the middle range is medium, above is fast, and below is slow
    if words_per_minute <= slow:
        audio_category = 'Slow'
    elif words_per_minute > slow and words_per_minute < medium:
         audio_category = 'Medium'
    else:
         audio_category = 'Fast'

    print(f"Accuracy: {accuracy}%")
    print(f"Words per Minute: {words_per_minute}")
    print(f"Audio_category: { audio_category}")

    return "Success"


# analyze('6619c8b48862a6217e382bfa') #Fast-Passage-Male   -Jared                          DEMO 1 (MaleFastPassage1)
# analyze('661c45c143eeb2d6f25c611b')  #Fast-Passage-Male  - Malakai(Hyrbid)               MaleFastPassage2

# print("\n")

# analyze('6619c9208862a6217e382c10') #Medium-Passage-Male - Malakai                       DEMO 2 (MaleMediumPassage1)
# analyze('661c5853501e01e2690aef4e') #Medium-Passage-Male  - Jared/Avin                   MaleMediumPassage2

# print("\n")

# analyze('6619e30f8862a6217e382ca9') #Fast-Passage-Female   -Anamika                      DEMO 3 (FemaleFastPassage1)
# analyze('661c6594f765018ad9abe1ad') #Fast-Passage-Female  - Jared's Cousin/Friend        FemaleFastPassage2

# print("\n")
                        
# analyze('6619cf6f8862a6217e382c60') #Medium-Passage-Female - Anamika                       DEMO 4(FemaleMediumPassage1)
# analyze('661c5d86038831c7224d81d7') #Medium-Passage-Female - Jared's Cousin/Friend         FemaleMediumPassage2

# print("\n")
                                    
# analyze('661c55955d6bf182ccd9c775') #Slow-Passage-Male - Jared                           MalePassageSlow1
# analyze('661c4c7530e46d0fc8692944') #Slow-Passage-Male  - Avin                           MalePassageSlow2

# print("\n")
                                    
# analyze('661c741df6090515a95cc4de') #Slow-Passage-Female - Jared Cousin/Friend           FemaleSlowPassage1
# analyze('661c5ec5038831c7224d81f9') #Slow-Passage-Female  -Jared Cousin/Friend           FemaleSlowPassage2

# print("\n")
                                    
# analyze('6619dc828862a6217e382c85') #Fast-Sentence-Male - Jared                              DFH Demo    
# analyze('661c4ed361e1b165af892652') #Fast-Sentence-Male - Avin                               MaleFastSentence2

# print("\n")
                                    
# analyze('661c68ca87b0cd447aee58b3') #Medium-Sentence-Male - Jared                            MaleMediumSentence1
# analyze('661c5022577821f82e4a85d4') #Medium-Sentence-Male - Avin                             MaleMediumSentence2

# print("\n")
                                    
# analyze('661c5bd89703e32bb392e472') #Slow-Sentence-Male - Jared                              MaleSlowSentence1
# analyze('661c547f373a0c442f233976') #Slow-Sentence-Male - Avin                               MaleSlowSentence2

# print("\n")
                                    
# analyze('661c6b4942b5fc9d50a4e176') #Fast-Sentence-Female - Jared Cosuin/Friend              FemaleFastSentence1
# analyze('661c7262d9e70da22173f3fc') #Fast-Sentence-Female - Anamika                          FemaleFastSentence2

# print("\n")
                                    
                                    
# analyze('661c6c1a9b2c5011df688284') #Medium-Sentence-Female - Jared Cosuin/Friend            FemaleMediumSentence1
# analyze('661c69dc765836e86209b7a1') #Medium-Sentence-Female - Jared Cosuin/Friend            FemaleMediumSentence2

# print("\n")
                                    
# analyze('661c6d8aa33524b82152313a') #Slow-Sentence-Female - Jared Cosuin/Friend              FemaleSlowSentence1
# analyze('661c63ee8c1e7816fdc9a33b') #Slow-Sentence-Female - Jared Cosuin/Friend              FemaleSlowSentence2

# print("\n")
                                    
                                    