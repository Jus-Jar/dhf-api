from mongo_controllers import get_reading_assessment_by_id

def analyzeVoice(id):
    result = get_reading_assessment_by_id(id)
    assessment = result['assessment']  # Get the assessment dictionary

    audio_data = assessment['updated_final_words_durations']
    duration_data = assessment['word_durations_s']
    text_data = assessment['words_from_file']

    count = 0
    for item in audio_data:
        if item['match']:
            count += 1

    accuracy = (count / len(audio_data)) * 100 if audio_data else 0

    # To get the last element's end time in duration_data
    if duration_data:
        last_element_end_time = duration_data[-1]['end']  # Access the end time of the last element
        total_duration_minutes = last_element_end_time / (60 * 1000)  # Convert milliseconds to minutes

        if total_duration_minutes > 0:
            words_per_minute = len(audio_data) / total_duration_minutes
        else:
            words_per_minute = 0
    else:
        words_per_minute = 0
        
    total_word_length = sum(len(word) for word in text_data)
    average_word_length = total_word_length / len(text_data) if text_data else 0
    
    expected_reading_rate = 238*(4.6/average_word_length)
    
    # print("Average Word Length:" ,average_word_length)
    # print("Expected Word per Minute:" ,expected_reading_rate)
    

    print(f"Accuracy: {accuracy}%")
    print(f"Words per Minute: {words_per_minute}")
    print("Predicted Grade Level:", classify_reader_by_wpm(words_per_minute))
    print("Reading Rate For Passage:", classify_reading_rate(words_per_minute, expected_reading_rate))

    return "Success"

def classify_reader_by_wpm(wpm):
    if wpm < 53:
        return 'Below 1st Grade level'
    elif 53 <= wpm <= 111:
        return '1st Grade level'
    elif 112 <= wpm <= 149:
        return '2nd Grade level'
    elif 150 <= wpm <= 162:
        return '3rd Grade level'
    else:
        return 'Above 3rd Grade level'
    
def classify_reading_rate(reader_wpm, expected_wpm):
    if reader_wpm > expected_wpm * 1.1:
        return "Above Average"
    elif reader_wpm < expected_wpm * 0.9:
        return "Below Average"
    else:
        return "Average"

   
analyzeVoice(id = '660cc221fe912c6589c51094')      
         