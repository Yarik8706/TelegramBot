import logging
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram import Bot, Dispatcher, types, executor
from parser import *
import config

logging.basicConfig(level=logging.INFO)

bot = Bot(config.TELEGRAMBOTTOKEN)
dp = Dispatcher(bot)

tournaments_data = []
tournament_text = types.Message
tournament_img = types.Message
next_tournaments_button = InlineKeyboardButton(text=">>", callback_data="next_tournament")
prev_tournaments_button = InlineKeyboardButton(text="<<", callback_data="prev_tournament")
exit_tournaments_button = InlineKeyboardButton(text="Назад", callback_data="exit_tournament")
index_tournaments = 0
tournaments_buttons = InlineKeyboardMarkup()
tournaments_buttons.add(prev_tournaments_button, next_tournaments_button, exit_tournaments_button)


@dp.callback_query_handler()
async def generate_text(call: types.CallbackQuery):
    await bot.answer_callback_query(call.id)
    global index_tournaments

    if call.data == "next_tournament":
        index_tournaments += 1
    elif call.data == "prev_tournament":
        index_tournaments -= 1
    if index_tournaments < 0 or index_tournaments >= len(tournaments_data):
        index_tournaments = 0
    await change_tournament_info(tournaments_data, index_tournaments, tournament_img, tournament_text)


@dp.message_handler(commands=["start"], commands_prefix="!/")
async def start(message: types.Message):
    await message.reply('Привет, {0}!'.format(message.from_user.first_name))


@dp.message_handler(commands=["check_tournaments"], commands_prefix="!/")
async def check_tournaments(message: types.Message):
    data = WotBlitzTournaments().get_completed_tournaments()
    print(data)
    if len(data) == 0:
        await message.answer("Ошибка!")
        return
    await message.answer("Прошедшие турниры!")
    global tournaments_data
    global tournament_img
    global tournament_text
    tournaments_data = data

    media = types.MediaGroup()
    media.attach_photo(data[0]["img"])
    tournament_img = (await message.answer_media_group(media))[0]
    tournament_text = await message.answer(f" 🧷<b>Название: {data[0]['title']}</b>🧷 \n\n"
                                           f" ⏳<b>Начиналось в: </b>{data[0]['start_at']}⏳ \n\n"
                                           f" ⌛<b>Заканчилось в: </b>{data[0]['end_at']}⌛ \n\n"
                                           f" 💵<b>Максимальная награда: </b> {data[0]['max_prize']}💵\n\n "
                                           f" 🔍<b><a href='https://na.wotblitz.com/ru/tournaments/#/tournament/"
                                           f"{data[0]['id']}/description/'>Ссылка на турнир</a></b>🔍",
                                           parse_mode="html",
                                           reply_markup=tournaments_buttons,
                                           disable_web_page_preview=True)


async def change_tournament_info(data, i, img, text):
    media = types.MediaGroup()
    media.attach_photo(data[i]["img"])
    # //await img.edit_media(media)
    await text.edit_text(f" 🧷<b>Название: {data[i]['title']}</b>🧷 \n\n"
                         f" ⏳<b>Начиналось в: </b>{data[i]['start_at']}⏳ \n\n"
                         f" ⌛<b>Заканчилось в: </b>{data[i]['end_at']}⌛ \n\n"
                         f" 💵<b>Максимальная награда: </b> {data[i]['max_prize']}💵\n\n "
                         f" 🔍<b><a href='https://na.wotblitz.com/ru/tournaments/#/tournament/{data[i]['id']}"
                         f"/description/'>Ссылка на турнир</a></b>🔍",
                         parse_mode="html",
                         reply_markup=tournaments_buttons,
                         disable_web_page_preview=True)


@dp.message_handler(commands=["check_planned_tournaments"], commands_prefix="!/")
async def planned_tournaments(message: types.Message):
    data = WotBlitzTournaments().get_planned_tournaments()
    if len(data) == 0:
        await message.answer("Активных турниров и тех которые будут в ближайшее время пока нет!")
        return
    await message.answer("Турниры на сегодня!")
    for i in data:
        await message.answer(
            f" Название: {i['title']} \n ⌛Начинает в: {i['start_at']} \n ⏳Заканчивается в: {i['end_at']}")


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=False)
