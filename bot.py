import os
import yt_dlp
import MukeshAPI
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from PIL import Image
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Получение токена API из переменных окружения
API_TOKEN = os.getenv('API_TOKEN')
REPO_LINK = os.getenv('REPO_LINK')

# Создание экземпляра бота и диспетчера
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # Создание клавиатуры для выбора опции работы с ботом
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Работа с изображениями"))
    keyboard.add(KeyboardButton("Работа с аудио"))

    await message.reply("Привет! Я бот, который может отправлять изображения и аудиофайлы. Выберите опцию:", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["Работа с изображениями", "Работа с аудио"])
async def process_option(message: types.Message):
    # Обработка выбора пользователя: работа с изображениями или аудио
    if message.text == "Работа с изображениями":
        await message.reply("Введите запрос для генерации изображений")
        await dp.current_state(user=message.from_user.id).set_state('image_prompt')
        await message.answer("Нажмите 'Отмена' для отмены", reply_markup=get_cancel_keyboard())
    elif message.text == "Работа с аудио":
        await message.reply("Введите запрос для генерации аудиофайла")
        await dp.current_state(user=message.from_user.id).set_state('audio_prompt')
        await message.answer("Нажмите 'Отмена' для отмены", reply_markup=get_cancel_keyboard())

def get_cancel_keyboard():
    # Создание клавиатуры для отмены запроса
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Отмена"))
    return keyboard

def download_audio(audio_request):
    # Создание папки для загрузки аудиофайлов, если она не существует
    if not os.path.exists('downloads'):
        os.makedirs('downloads')

    ydl_opts = {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': f'downloads/{audio_request}.mp3',
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Поиск аудиофайлов по запросу пользователя
            search_results = ydl.extract_info(f"ytsearch:{audio_request}", download=True)
            if search_results['entries']:
                audio_file = f"downloads/{audio_request}.mp3"
                return audio_file if os.path.exists(audio_file) else None
            else:
                return None
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None

@dp.message_handler(state='image_prompt')
async def send_image(message: types.Message):
    if message.text == "Отмена":
        await cancel_request(message)
        return
    
    prompt = message.text  # Получаем текст запроса от пользователя

    try:
        # Используем Mukesh API для поиска изображений
        img = MukeshAPI.api.ai_image(prompt)
        await bot.send_photo(message.chat.id, img, message.text)  # Отправляем каждое изображение пользователю          

    except Exception as e:
        await message.reply(f"Произошла ошибка при получении изображений: {e}")

@dp.message_handler(state='audio_prompt')
async def send_audio(message: types.Message):
    if message.text == "Отмена":
        await cancel_request(message)
        return
    
    audio_request = message.text  # Получаем текст запроса от пользователя
    audio_file = download_audio(audio_request)

    if audio_file and os.path.exists(audio_file):
        with open(audio_file, 'rb') as audio:
            await bot.send_audio(message.chat.id, audio)  # Отправляем аудиофайл пользователю
        os.remove(audio_file)  # Удаляем файл после отправки
    else:
        await message.reply("Не удалось найти аудиофайл.")

async def cancel_request(message: types.Message):
    # Сброс состояния и возврат к главному меню
    await dp.current_state(user=message.from_user.id).reset_state()
    await message.reply("Запрос отменен. Выберите новую опцию:", reply_markup=get_main_keyboard())

def get_main_keyboard():
    # Создание главной клавиатуры для выбора опции работы с ботом
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Работа с изображениями"))
    keyboard.add(KeyboardButton("Работа с аудио"))
    return keyboard

@dp.message_handler(commands=['repo'])
async def send_repo_link(message: types.Message):
    # Отправка ссылки на репозиторий бота
    await message.reply(f"Вот ссылка на мой репозиторий: {REPO_LINK}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)  # Запуск бота в режиме опроса
