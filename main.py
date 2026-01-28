import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID", "@kp_club")
MINI_APP_URL = os.getenv("MINI_APP_URL")
REQUIRE_SUBSCRIPTION = False  # ← Новое!
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(","))) if os.getenv("ADMIN_IDS") else []

# =============== ИНИЦИАЛИЗАЦИЯ ===============
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# =============== ПРОВЕРКА ПОДПИСКИ ===============
async def check_subscription(user_id: int) -> bool:
    """Проверяет подписан ли пользователь на канал"""
    # ✅ Если проверка подписки отключена - возвращаем True
    if not REQUIRE_SUBSCRIPTION:
        return True
    
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logger.error(f"Ошибка проверки подписки: {e}")
        return False


# =============== КЛАВИАТУРЫ ===============
def get_main_keyboard(is_subscribed: bool) -> InlineKeyboardMarkup:
    """Главная клавиатура"""
    if is_subscribed:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="🚀 Открыть магазин",
                web_app=WebAppInfo(url=MINI_APP_URL)
            )],
            [InlineKeyboardButton(
                text="🔄 Проверить подписку",
                callback_data="check_sub"
            )] if REQUIRE_SUBSCRIPTION else []  # ← Показываем только если проверка включена
        ])
    else:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📢 Подписаться на канал",
                url="https://t.me/kp_club"
            )],
            [InlineKeyboardButton(
                text="✅ Проверить подписку",
                callback_data="check_sub"
            )]
        ])
    return keyboard


# =============== КОМАНДА /start ===============
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработка команды /start"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name or "пользователь"
    
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        if REQUIRE_SUBSCRIPTION:
            text = (
                f"👋 Привет, <b>{user_name}</b>!\n\n"
                f"✅ Вы подписаны на наш канал!\n\n"
                f"🛍 Добро пожаловать в магазин премиальных аксессуаров <b>KP EXCLUSIVE</b>\n\n"
                f"Нажмите кнопку ниже, чтобы начать покупки:"
            )
        else:
            text = (
                f"👋 Привет, <b>{user_name}</b>!\n\n"
                f"🛍 Добро пожаловать в магазин премиальных аксессуаров <b>KP EXCLUSIVE</b>\n\n"
                f"Нажмите кнопку ниже, чтобы начать покупки:"
            )
    else:
        text = (
            f"👋 Привет, <b>{user_name}</b>!\n\n"
            f"🛍 Добро пожаловать в магазин премиальных аксессуаров <b>KP EXCLUSIVE</b>\n\n"
            f"❗️ Для доступа к магазину необходимо подписаться на наш канал:\n"
            f"👉 @kp_club\n\n"
            f"После подписки нажмите «Проверить подписку»"
        )
    
    await message.answer(
        text=text,
        reply_markup=get_main_keyboard(is_subscribed),
        parse_mode="HTML"
    )


# =============== ПРОВЕРКА ПОДПИСКИ (CALLBACK) ===============
@dp.callback_query(F.data == "check_sub")
async def check_subscription_callback(callback: types.CallbackQuery):
    """Обработка нажатия кнопки проверки подписки"""
    user_id = callback.from_user.id
    user_name = callback.from_user.first_name or "пользователь"
    
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        text = (
            f"✅ Отлично, <b>{user_name}</b>!\n\n"
            f"Вы успешно подписались на канал.\n"
            f"Теперь вам доступен магазин KP EXCLUSIVE! 🎉"
        ) if REQUIRE_SUBSCRIPTION else (
            f"✅ <b>{user_name}</b>!\n\n"
            f"Магазин KP EXCLUSIVE доступен! 🎉"
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=get_main_keyboard(True),
            parse_mode="HTML"
        )
        await callback.answer("✅ Подписка подтверждена!")
    else:
        text = (
            f"❌ <b>{user_name}</b>, вы ещё не подписались на канал.\n\n"
            f"Пожалуйста, подпишитесь на @kp_club и нажмите «Проверить подписку» снова."
        )
        await callback.message.edit_text(
            text=text,
            reply_markup=get_main_keyboard(False),
            parse_mode="HTML"
        )
        await callback.answer("❌ Подписка не найдена", show_alert=True)


# =============== КОМАНДА /help ===============
# @dp.message(Command("help"))
# async def cmd_help(message: types.Message):
#     """Помощь"""
#     if REQUIRE_SUBSCRIPTION:
#         text = (
#             "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
#             "1️⃣ Подпишитесь на канал @kp_club\n"
#             "2️⃣ Нажмите «Проверить подписку»\n"
#             "3️⃣ Откройте магазин и выбирайте товары\n\n"
#             "💬 Вопросы? Пишите @kp_club"
#         )
#     else:
#         text = (
#             "ℹ️ <b>Как пользоваться ботом:</b>\n\n"
#             "1️⃣ Нажмите /start\n"
#             "2️⃣ Откройте магазин и выбирайте товары\n\n"
#             "💬 Вопросы? Пишите @kp_club"
#         )
#     await message.answer(text, parse_mode="HTML")


# =============== СТАТИСТИКА (только для админов) ===============
@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    """Статистика бота (только для админов)"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    sub_status = "✅ Включена" if REQUIRE_SUBSCRIPTION else "❌ Отключена"
    
    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"🔐 Проверка подписки: {sub_status}\n"
        "👥 Всего пользователей: -\n"
        "✅ Подписчиков: -\n"
        "❌ Не подписано: -\n\n"
        "<i>Для полной статистики подключите базу данных</i>"
    )
    await message.answer(text, parse_mode="HTML")


# =============== ОБРАБОТКА ДРУГИХ СООБЩЕНИЙ ===============
@dp.message()
async def handle_other_messages(message: types.Message):
    """Обработка всех остальных сообщений"""
    user_id = message.from_user.id
    is_subscribed = await check_subscription(user_id)
    
    if is_subscribed:
        text = "🛍 Для открытия магазина нажмите кнопку ниже:"
    else:
        text = "❗️ Для доступа к магазину подпишитесь на @kp_club"
    
    await message.answer(
        text=text,
        reply_markup=get_main_keyboard(is_subscribed)
    )


# =============== ЗАПУСК БОТА ===============
async def main():
    """Запуск бота"""
    logger.info("🤖 Бот запущен!")
    logger.info(f"🔐 Проверка подписки: {'ВКЛЮЧЕНА' if REQUIRE_SUBSCRIPTION else 'ОТКЛЮЧЕНА'}")
    
    # Устанавливаем команды в меню
    await bot.set_my_commands([
        types.BotCommand(command="start", description="🚀 Запустить бота"),
        # types.BotCommand(command="help", description="ℹ️ Помощь"),
    ])
    
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⛔️ Бот остановлен")
