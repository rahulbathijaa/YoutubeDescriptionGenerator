import os
from openai import OpenAI
from pathlib import Path

# Assuming you've already set your OPENAI_API_KEY in the environment variables
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def transcribe_audio_with_openai_whisper(audio_path, transcription_file_path="transcription.txt"):
    """
    Checks if a transcription already exists in a given file and returns it.
    If not, transcribes an audio file using OpenAI's Whisper model via the API,
    saves the transcription to a file, and then returns it.
    """
    if Path(transcription_file_path).is_file():
        print("Transcription file already exists. Reading from file...")
        with open(transcription_file_path, "r") as file:
            transcription = file.read()
        return transcription
    else:
        print("Transcription file does not exist. Transcribing audio...")
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
              model="whisper-1", 
              file=audio_file
            )
            transcription = response.data.text

        with open(transcription_file_path, "w") as file:
            file.write(transcription)

        return transcription

def generate_youtube_description(transcription_text, channel_name, video_titles, expected_video_title, ctas, social_links):
  """
  Generates a YouTube video description using GPT-4 Turbo via the chat completions endpoint,
  incorporating various inputs.
  """
  prompt = f"""Create a YouTube video description based on the following details:
  - Video Title: {expected_video_title}
  - Channel Name: {channel_name}
  - Style and Tone: Similar to previous videos titled {", ".join(video_titles)}
  - Transcription: {transcription_text}
  Include a compelling summary, calls to action, and social media links.

CTAs: {ctas}
Social Links: {social_links}
"""


  response = client.chat.completions.create(
      model="gpt-4-turbo-preview",  # Use the correct model identifier; adjust as necessary
      messages=[
          {"role": "system", "content": "You are a highly knowledgeable assistant."},
          {"role": "user", "content": prompt}
      ],
      max_tokens=1024,
      temperature=0.7,
      n=1
  )
 # Assuming 'response' is the variable holding the response from the OpenAI API call
  if response.choices:
     # Extracting the content from the first choice's message
      description_content =     response.choices[0].message.content
      print("Video Description Content:\n",   description_content)
  else:
     print("Failed to generate description.")


# print (response)

  # Assuming the response structure aligns with chat completion output
  # description = response.choices[0].message["content"] if response.choices else "Description generation failed."
  # return description


# Example setup (replace placeholders with your actual data)
channel_name = "Your Channel Name"
video_titles = ["Video Title 1", "Video Title 2", "Video Title 3", "Video Title 4", "Video Title 5"]  # Sample existing video titles
expected_video_title = "The Incredible Story of Tootsie Rolls"
ctas = "Don't forget to like and subscribe for more amazing stories!"
social_links = "Follow us on Twitter @YourChannel, Instagram @YourChannelInsta."

# Path to your audio file - ensure this is correctly set
audio_path = "candyvideo.mp3"

# Transcribe the audio file (if not already done)
transcription_text = transcribe_audio_with_openai_whisper(audio_path)

# Generate the YouTube video description
description = generate_youtube_description(transcription_text, channel_name, video_titles, expected_video_title, ctas, social_links)
print("Generated YouTube Video Description:\n", description)
