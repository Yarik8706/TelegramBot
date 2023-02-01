import logging
from aiogram import Bot, Dispatcher, types, executor
import config
import openai
import whisper
import requests
from pathlib import Path
from pydub import AudioSegment
import ffmpeg

model = whisper.load_model("base")
AudioSegment.from_ogg("./voice.ogg").export("audio", format="mp3")

audio = whisper.load_audio("audio.mp3")

audio = whisper.pad_or_trim(audio)
mel = whisper.log_mel_spectrogram(audio).to(model.device)

_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)
