import logging
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Bot tokenini shu yerga yozing
API_TOKEN = '8627333339:AAE1LLR3ICahpnsqezKdRuzSyXKnT31hPaA'

# Logging va Botni sozlash
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchilar o'yin ma'lumotlari
user_games = {}


def yangi_oyin_yarat(user_id):
    xarita = [["~" for _ in range(5)] for _ in range(5)]
    kema_qator = random.randint(0, 4)
    kema_ustun = random.randint(0, 4)

    user_games[user_id] = {
        "xarita": xarita,
        "kema": (kema_qator, kema_ustun),
        "imkoniyatlar": 5,
        "oyin_tugadi": False
    }


def xarita_keyboard(user_id):
    game = user_games[user_id]
    xarita = game["xarita"]

    builder = InlineKeyboardBuilder()

    for r in range(5):
        for c in range(5):
            belgi = xarita[r][c]
            text = "🌊" if belgi == "~" else ("💨" if belgi == "*" else "💥")
            builder.button(text=text, callback_data=f"otish_{r}_{c}")

    builder.adjust(5)  # Har bir qatorda 5 tadan tugma bo'lsin

    if game["oyin_tugadi"]:
        builder.button(text="Yana o'ynash 🔄", callback_data="qayta_boshlash")
        builder.adjust(5, 1)  # Oxirgi tugmani alohida qatorga o'tkazish

    return builder.as_markup()


@dp.message(Command("start", "help"))
async def start_game(message: types.Message):
    user_id = message.from_user.id
    yangi_oyin_yarat(user_id)

    await message.answer(
        "🚢 **DENGIZ JANGI O'YINIGA XUSH KELIBSIZ!** 🚢\n\n"
        "Men 5x5 xaritaga 1 ta kema yashirdim. Uni topish uchun xaritadan bitta katakni tanlang.\n"
        "Sizda **5 ta imkoniyat** bor!",
        reply_markup=xarita_keyboard(user_id),
        parse_mode="Markdown"
    )


@dp.callback_query(F.data.startswith('otish_'))
async def process_shot(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id

    if user_id not in user_games:
        yangi_oyin_yarat(user_id)

    game = user_games[user_id]

    if game["oyin_tugadi"]:
        await callback_query.answer("O'yin tugagan! Yangi o'yin boshlang.", show_alert=True)
        return

    _, qator, ustun = callback_query.data.split("_")
    qator, ustun = int(qator), int(ustun)

    xarita = game["xarita"]
    kema_qator, kema_ustun = game["kema"]

    if xarita[qator][ustun] != "~":
        await callback_query.answer("Bu yerga oldin otgansiz!", show_alert=True)
        return

    if qator == kema_qator and ustun == kema_ustun:
        xarita[qator][ustun] = "X"
        game["oyin_tugadi"] = True
        matn = "URRAA! Kema portlatildi! Siz g'alaba qozondingiz! 🎉 💥"
    else:
        xarita[qator][ustun] = "*"
        game["imkoniyatlar"] -= 1

        if game["imkoniyatlar"] <= 0:
            game["oyin_tugadi"] = True
            xarita[kema_qator][kema_ustun] = "X"
            matn = f"O'yin tugadi! Imkoniyatlaringiz qolmadi. 😢\nKema [{kema_qator + 1}, {kema_ustun + 1}] katakda edi."
        else:
            matn = f"Afsus, o'q xato ketdi! 🌊\nQolgan imkoniyatlar: {game['imkoniyatlar']}"

    await callback_query.message.edit_text(
        text=matn,
        reply_markup=xarita_keyboard(user_id)
    )
    await callback_query.answer()


@dp.callback_query(F.data == 'qayta_boshlash')
async def restart_game(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    yangi_oyin_yarat(user_id)

    await callback_query.message.edit_text(
        text="Yangi o'yin boshlandi! Xaritadan katak tanlang. 🚢",
        reply_markup=xarita_keyboard(user_id)
    )
    await callback_query.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
