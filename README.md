# Telegram-bot
Этот код реализует работу telegram-bot'а для генерации изображений и аудио файлов.
Для генерации изображений используется библиотека MukeshAPI, которая автоматизиует отправку запросов на API и получение пользователем ответа. При отправке запросов использование АНГЛИЙСКОГО языка будет выдавать наиболее точные ответы.
При генерации аудио отправляется запрос в видео-хостинг YouTube и скачивается первое видео найденное по запросу в формате .mp3

Для задачи токенов для API, хранения URL и тд, рекомендуется использовать файл .env
Здесь есть его пример, нужно лишь заменить значения на реальные.

1. Клонирование репозитория 

```git clone https://github.com/meganis0-0/test_bot.git```

2. Создание виртуального окружения

```python3 -m venv venv```

3. Активация виртуального окружения

```source venv/bin/activate```

4. Установка зависимостей

```pip3 install -r requirements.txt```
