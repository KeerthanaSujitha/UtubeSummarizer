import re
from fastapi import FastAPI, Request, File, UploadFile,Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
from dotenv import load_dotenv
load_dotenv()
from pytube import YouTube
import uvicorn
import fastapi
import assemblyai as aai
from googletrans import Translator
from pydantic import BaseModel
import openai

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

class URLItem(BaseModel):
    url: str
    language: str






@app.get('/')
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})





@app.post("/submit_url")
async def submit_url(item: URLItem):
    url = item.url
    language = item.language
    # Process the URL and language data as needed
    print(f"Received URL: {url}, Language: {language}")
    
    youtube_url = url
    output_path = "./output"
    download_audio(youtube_url, output_path, filename="audio")

    
    # aai.settings.api_key = "d31b46660902421d8b7de5c2fd378c9a"

    # # URL of the file to transcribe
    # FILE_URL = "./output/audio.mp3"

    # transcriber = aai.Transcriber()
    # transcript = transcriber.transcribe(FILE_URL)



    # mixed_text = transcript.text
    # # Translate the mixed text to English
    # print("Original Text:", mixed_text)

    # translated_text = translate_text(mixed_text)
   

    # API_KEY = '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'
    API_KEY = os.getenv("API_KEY")
    model_id = 'whisper-1'
    language = "en"

    audio_file_path = './output/audio.mp3'
    audio_file = open(audio_file_path, 'rb')

    response = openai.Audio.translate(
        api_key=API_KEY,
        model=model_id,
        file=audio_file
    )
    translation_text = response.text
    # Print the results
    print("Translated Text:", translation_text)

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    # Split the content into chunks of 1000 tokens
    chunk_size = 1000
    chunks = [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

    # Summarize each chunk and store the results
    summaries = []
    for chunk in chunks:
        summary = summarizer(chunk, max_length=40, min_length=8, length_penalty=2.0, num_beams=4, early_stopping=True)
        summaries.append(summary[0]['summary_text'])

    text = '\n'.join(summaries)
    print(text)

    # Load BertSum model
    bertsum_model = Summarizer()

    # Summarize the content to 40 lines
    summary = bertsum_model(text, num_sentences=40)

    # Print the summarized content
    print(summary)

    

    return {"message": "URL submitted successfully"}





def download_audio(youtube_url, output_path, filename="audio"):
    yt = YouTube(youtube_url)
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(output_path)

    # Get the default filename
    default_filename = audio_stream.default_filename

    # Rename the downloaded file
    downloaded_file_path = os.path.join(output_path, default_filename)
    new_file_path = os.path.join(output_path, f"{filename}.mp3")
    os.rename(downloaded_file_path, new_file_path)



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
    
    