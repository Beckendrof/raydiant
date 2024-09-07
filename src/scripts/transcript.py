from youtube_transcript_api import YouTubeTranscriptApi

# Retrieve the available transcripts
transcript_list = YouTubeTranscriptApi.list_transcripts('jGwO_UgTS7I')

# Accumulate text from all segments
all_text = ""
for transcript in transcript_list:
    # Translate the transcript
    translated_transcript = transcript.translate('en').fetch()
    
    # Print the top of the translated transcript
    if translated_transcript:
        first_segment = translated_transcript[0]
        print("Top of the transcript:")
        print(first_segment['text'])
        print()  # Add a blank line for separation

    # Concatenate text from all segments
    all_text += first_segment['text'] + '\n'

# Save the transcript to a text file
text_file = "transcript.txt"
with open(text_file, "w") as file:
    file.write(all_text)

print("Transcript saved to", text_file)




   

