# -*- coding: utf-8 -*-
import logging
from aiogram import Bot, Dispatcher, types, executor
import config
import openai

logging.basicConfig(level=logging.INFO)

bot = Bot(config.TELEGRAMBOTTOKEN)
bot_controller = Dispatcher(bot)

openai.api_key = config.OPENAITOKEN
openai.api_base = "https://neuroapi.host/v1"

start_sequence = "\nAI"
restart_sequence = "\nHuman: "
bad_message = "Простите я не знаю как на это ответить"
conversation = [{"role": "system", "content": "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly and you're also a robo cat girl."}]
logs = []


def ai_answer():
    try:
        print("Get response")
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logs.append(e.__str__() + "\n")
        return bad_message


@bot_controller.message_handler(commands=['reset'], commands_prefix="!/")
async def command_1(message: types.Message):
    chat_dest = message['chat']['id']
    clear_bot_history()
    await bot.send_message(chat_dest, "Я успешно очистилась!")


def clear_bot_history():
    global conversation
    conversation = [{"role": "system", "content": "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly and you're also a robo cat girl."}]


@bot_controller.message_handler(commands=['unpack'], commands_prefix="!/")
async def command_2(message: types.Message):
    chat_dest = message['chat']['id']
    await bot.send_message(chat_dest, "Пересылаю текущую историю сообщений:")
    text_history = ""
    for mes in conversation:
        text_history = text_history + "\n" + mes["role"] + " : " + mes['content']

    await bot.send_message(chat_dest, text_history)


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


@bot_controller.message_handler(commands=['logs'], commands_prefix="!/")
async def command_4(message: types.Message):
    chat_dest = message['chat']['id']
    await bot.send_message(chat_dest, "".join(logs), reply_to_message_id=message.message_id)


@bot_controller.message_handler(content_types=["text"])
async def any_message(message: types.Message):
    user_msg = message.text
    if message.content_type != "text":
        return
    if user_msg.lower().find('нейросеть') == -1 and message['chat']['type'] != "private" \
            and not message.reply_to_message:
        return
    if message.reply_to_message and not message.reply_to_message.from_user.username == config.MYUSERNAME \
            and user_msg.lower().find('нейросеть') == -1:
        return
    if user_msg.lower().find('нейросеть') != -1 and message['chat']['type'] != "private" and message.reply_to_message:
        user_msg += " \"" + message.reply_to_message.text + "\""
    add_new_message_to_history(message["from"]["username"], user_msg)
    text = ai_answer()
    await bot.send_message(message.chat.id, text, reply_to_message_id=message.message_id)
    add_new_message_to_history("AI", text)


def add_new_message_to_history(name, text):
    conversation.append({"role": "system", "content": name + " : " + text})


# @bot_controller.message_handler(content_types=["voice"])
# async def audio_message(message: types.Message):
#     voice = message.voice
#     file_info = await tests.get_file(voice.file_id)
#     response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(config.TELEGRAMBOTTOKEN,
#                                                                               file_info.file_path))
#     voice = Path('./input/voice.ogg')
#     voice.write_bytes(response.content)
#     AudioSegment.from_file("/input/voice").export("/output/audio", format="mp3")
#     audio = whisper.load_audio("/output/audio.mp3")
#     audio = whisper.pad_or_trim(audio)
#     mel = whisper.log_mel_spectrogram(audio).to(model.device)
#
#     _, probs = model.detect_language(mel)
#     print(f"Detected language: {max(probs, key=probs.get)}")
#     options = whisper.DecodingOptions()
#     result = whisper.decode(model, mel, options)
#
#     await tests.send_message(message.chat.id, result.text)


if __name__ == '__main__':
    executor.start_polling(bot_controller, skip_updates=True)
