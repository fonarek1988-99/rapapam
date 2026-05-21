users = set()
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "8806700052:AAEjw1sXodhTJjQbbLuRHToxhbQVk8YB7Sw"
ADMIN_ID = 8324273257

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище данных пользователей
user_data = {}
user_state = {}

# --- КНОПКИ ---

age_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Мне есть 18 лет", callback_data="age_confirm")]
    ]
)

start_form_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Заполнить анкету", callback_data="start_form")]
    ]
)

experience_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data="exp_yes")],
        [InlineKeyboardButton(text="Нет", callback_data="exp_no")],
    ]
)

format_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пара М+Ж", callback_data="couple")],
        [InlineKeyboardButton(text="Одинокая девушка", callback_data="girl")],
        [InlineKeyboardButton(text="Одинокий мужчина", callback_data="man")],
    ]
)

final_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Отправить анкету", callback_data="send_form")],
        [InlineKeyboardButton(text="Заполнить заново", callback_data="restart_form")],
    ]
)

# --- START ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id

    new_user = user_id not in users
    users.add(user_id)

    if new_user:
        await bot.send_message(
            ADMIN_ID,
            f"👤 Новый пользователь\nID: {user_id}\nВсего пользователей: {len(users)}"
        )

    await message.answer(
        "🔞 Нажимая кнопку, вы подтверждаете что вам исполнилось 18 лет.",
        reply_markup=age_kb
    )
   

# --- CALLBACKS ---

# --- CALLBACKS ---

@dp.callback_query()
async def callbacks(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    # 18+
    if callback.data == "age_confirm":

        await bot.send_message(
            ADMIN_ID,
            f"Пользователь подтвердил 18+: {user_id}"
        )

        await callback.message.answer(
            "👋 Добро пожаловать!\n\n❗️Для получения актуальных мероприятий в вашем городе необходимо заполнить короткую анкету.",
            reply_markup=start_form_kb
        )

    # старт анкеты
    elif callback.data == "start_form":

        user_data[user_id] = {}
        user_state[user_id] = "name"

        await callback.message.answer(
            "❓ Вопрос 1 из 5\n\n● Ваше имя?"
        )

    # опыт посещения
    elif callback.data in ["exp_yes", "exp_no"]:

        if callback.data == "exp_yes":
            user_data[user_id]["experience"] = "Да"
        else:
            user_data[user_id]["experience"] = "Нет"

        user_state[user_id] = "format"

        await callback.message.answer(
            "❓ Вопрос 5 из 5\n\n● Выберите формат участия",
            reply_markup=format_kb
        )

    # формат
    elif callback.data in ["couple", "girl", "man"]:

        mapping = {
            "couple": "Пара М+Ж",
            "girl": "Одинокая девушка",
            "man": "Одинокий мужчина"
        }

        user_data[user_id]["format"] = mapping[callback.data]

        data = user_data[user_id]

        text = f"""📋 Ваша анкета:

1. ● Ваше имя?
   ➜ {data.get("name")}

2. ● Ваш город?
   ➜ {data.get("city")}

3. ● Ваш возраст?
   ➜ {data.get("age")}

4. ● Был ли опыт посещения свингер вечеринок?
   ➜ {data.get("experience")}

5. ● Выберите формат участия
   ➜ {data.get("format")}"""

        await callback.message.answer(
            text,
            reply_markup=final_kb
        )

    # отправка анкеты
    elif callback.data == "send_form":

        data = user_data[user_id]

        text = f"""📩 Новая анкета:

Имя: {data.get("name")}
Город: {data.get("city")}
Возраст: {data.get("age")}
Опыт посещения: {data.get("experience")}
Формат: {data.get("format")}
ID: {user_id}"""

        # админу
        await bot.send_message(ADMIN_ID, text)

        # пользователю
        await callback.message.answer(
            "🔎 Подбираем актуальные мероприятия для вашего города..."
        )

        await asyncio.sleep(5)

        await callback.message.answer(
            "🎉 Готово! Вот ваша ссылка:\n\nhttps://t.me/svingercluborgazm"
        )

    # Заполнить заново
    elif callback.data == "restart_form":

        user_state[user_id] = "name"
        user_data[user_id] = {}

        await callback.message.answer(
            "❓ Вопрос 1 из 5\n\n● Ваше имя?"
        )

    await callback.answer()


# --- ТЕКСТОВЫЕ ОТВЕТЫ ---

@dp.message()
async def handle_answers(message: types.Message):
    user_id = message.from_user.id

    if user_id not in user_state:
        return

    state = user_state[user_id]

    if state == "name":
        user_data[user_id]["name"] = message.text
        user_state[user_id] = "city"

        await message.answer("❓ Вопрос 2 из 5\n\n● Ваш город?")

    elif state == "city":
        user_data[user_id]["city"] = message.text
        user_state[user_id] = "age"

        await message.answer("❓ Вопрос 3 из 5\n\n● Ваш возраст?")

    elif state == "age":
        user_data[user_id]["age"] = message.text
        user_state[user_id] = "experience"

        await message.answer(
            "❓ Вопрос 4 из 5\n\n● Был ли опыт посещения свингер вечеринок?",
            reply_markup=experience_kb
        )
# --- ЗАПУСК ---

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())