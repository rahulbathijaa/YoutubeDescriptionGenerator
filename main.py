from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os
from pathlib import Path
import shutil

app = FastAPI()

# Set up CORS middleware for local development with frontend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"], 
)
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/transcribe/")
async def transcribe_audio(audio: UploadFile = File(...)):
    transcription_file_path = "transcription.txt"
    if Path(transcription_file_path).is_file():
        print("Transcription file already exists. Reading from file...")
        with open(transcription_file_path, "r") as file:
            return file.read()
    else:
        print("Transcription file does not exist. Transcribing audio...")
        with open(audio.filename, "wb") as buffer:
            shutil.copyfileobj(audio.file, buffer)

        with open(audio.filename, "rb") as audio_file:
            response = client.audio.transcriptions.create(
              model="whisper-1", 
              file=audio_file
            )
            transcription = response.data.text

        with open(transcription_file_path, "w") as file:
            file.write(transcription)
        return transcription

@app.post("/generate-description/")
async def generate_description(
    transcription_text: str = Form(...), 
    channel_name: str = Form(...),
    video_titles: list = Form(...), 
    expected_video_title: str = Form(...), 
    ctas: str = Form(...), 
    social_links: str = Form(...), 
    regenerate: bool = Form(False)
):
    description_file_path = "output.txt"
    if not regenerate and Path(description_file_path).is_file():
        print("Description file already exists. Reading from file...")
        with open(description_file_path, "r") as file:
            return file.read()
    else:
        print("Generating new description...")
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
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": "You are a highly knowledgeable assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024,
            temperature=0.7,
            n=1
        )
        description = response.choices[0].message.content if response.choices else "Description generation failed."
        with open(description_file_path, "w") as file:
            file.write(description)
        return description

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
