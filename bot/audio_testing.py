import logging
import pathlib

import whisper
from pydub import AudioSegment

model = whisper.load_model("base")
print(str(pathlib.Path().parent.absolute()) + "\\cash\\voice.ogg")
voice = AudioSegment.from_ogg(str(pathlib.Path().parent.absolute()) + "\\cash\\voice.ogg");

voice.export("audio", format="mp3")

audio = whisper.load_audio("audio.mp3")

audio = whisper.pad_or_trim(audio)
mel = whisper.log_mel_spectrogram(audio).to(model.device)

_, probs = model.detect_language(mel)
print(f"Detected language: {max(probs, key=probs.get)}")
options = whisper.DecodingOptions()
result = whisper.decode(model, mel, options)
print(result)