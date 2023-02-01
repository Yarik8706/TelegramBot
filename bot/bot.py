import logging
from aiogram import Bot, Dispatcher, types, executor
import config
import openai
import whisper
import requests
from pathlib import Path
from pydub import AudioSegment


model = whisper.load_model("base")

logging.basicConfig(level=logging.INFO)

bot = Bot(config.TELEGRAMBOTTOKEN)
bot_controller = Dispatcher(bot)

openai.api_key = config.OPENAITOKEN

start_sequence = "\nAI:"
restart_sequence = "\nHuman: "
bad_message = "Простите я не знаю как на это ответить"
bot_history = []


def ai_answer(answer):
    try:
        return openai.Completion.create(
            model="text-davinci-003",
            prompt="The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n" + "".join(
                bot_history) + answer + "\nAI:",
            temperature=0.9,
            max_tokens=2000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=[" Human:", " AI:"]
        )["choices"][0]["text"]
    except:
        return bad_message


@bot_controller.message_handler(commands=['reset'], commands_prefix="!/")
async def command_1(message: types.Message):
    chat_dest = message['chat']['id']
    bot_history.clear()
    await bot.send_message(chat_dest, "Я успешно очистилась!")


@bot_controller.message_handler(commands=['unpack'], commands_prefix="!/")
async def command_2(message: types.Message):
    chat_dest = message['chat']['id']
    await bot.send_message(chat_dest, "Пересылаю текущую историю сообщений:")
    await bot.send_message(chat_dest, "".join(bot_history))


@bot_controller.message_handler(commands=['image'], commands_prefix="!/")
async def command_3(message: types.Message):
    chat_dest = message['chat']['id']
    user_msg = message['text']
    response = openai.Image.create(
        prompt=user_msg,
        n=1,
        size="512x512"
    )
    image_url = response['data'][0]['url']
    await bot.send_photo(chat_dest, image_url, reply_to_message_id=message.message_id)


@bot_controller.message_handler(content_types=["text"])
async def any_message(message: types.Message):
    chat_dest = message.chat.id
    user_msg = message.text
    if user_msg.lower().find('нейросеть') == -1 and message['chat']['type'] != "private" \
            or message.reply_to_message and not message.reply_to_message.from_user.username == config.MYUSERNAME:
        return
    print(message["from"]["username"] + ": " + user_msg)
    text = ai_answer(message["from"]["username"] + ": " + user_msg)
    if text != bad_message:
        bot_history.append(message["from"]["username"] + ": " + user_msg)
        bot_history.append(start_sequence + text)
    await bot.send_message(chat_dest, text, reply_to_message_id=message.message_id)


@bot_controller.message_handler(content_types=["voice"])
async def audio_message(message: types.Message):
    voice = message.voice
    file_info = await bot.get_file(voice.file_id)
    response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.TELEGRAMBOTTOKEN,
                                                                              file_info.file_path))
    voice = Path('./input/voice.ogg')
    voice.write_bytes(response.content)
    AudioSegment.from_file("/input/voice").export("/output/audio", format="mp3")
    audio = whisper.load_audio("/output/audio.mp3")
    audio = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio).to(model.device)

    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    options = whisper.DecodingOptions()
    result = whisper.decode(model, mel, options)

    await bot.send_message(message.chat.id, result.text)


if __name__ == '__main__':
    executor.start_polling(bot_controller, skip_updates=True)
