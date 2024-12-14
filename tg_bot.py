import os
import telebot
import speech_recognition
from pydub import AudioSegment
from bot_secret_token import bot_secret_token
from PIL import Image, ImageEnhance, ImageFilter

token = bot_secret_token  # <<< Ваш токен

bot = telebot.TeleBot(token)


def transform_image(input_filename, output_filename):
    # Функция обработки изображения
    source_image = Image.open(input_filename)
    enhanced_image = source_image.filter(ImageFilter.EMBOSS)
    enhanced_image = enhanced_image.convert('RGB')
    enhanced_image.save(output_filename)
    return output_filename


def compress_image(input_filename, output_filename):
    source_image = Image.open(input_filename)
    width = source_image.size[0]
    height = source_image.size[1]
    resized_image = source_image.resize((width // 5, height // 5))
    resized_image.save(output_filename)
    return output_filename


@bot.message_handler(content_types=['photo'])
def resend_photo(message):
    files_to_delete = []

    # Функция отправки обработанного изображения
    file_id = message.photo[-1].file_id
    filename = download_file(bot, file_id)
    files_to_delete.append(filename)

    # Трансформируем изображение
    transform_image(filename, 'transformed_image.jpg')
    image = open('transformed_image.jpg', 'rb')
    bot.send_photo(message.chat.id, image)
    image.close()
    files_to_delete.append('transformed_image.jpg')

    # сжимаем изображение
    compress_image(filename, 'compressed_image.jpg')
    image = open('compressed_image.jpg', 'rb')
    bot.send_photo(message.chat.id, image)
    image.close()
    files_to_delete.append('compressed_image.jpg')

    # Не забываем удалять ненужные изображения
    for filename in files_to_delete:
        if os.path.exists(filename):
            os.remove(filename)


def oga2wav(filename):
    # Конвертация формата файлов
    new_filename = filename.replace('.oga', '.wav')
    audio = AudioSegment.from_file(filename)
    audio.export(new_filename, format='wav')
    return new_filename


def recognize_speech(oga_filename):
    # Перевод голоса в текст + удаление использованных файлов
    wav_filename = oga2wav(oga_filename)
    recognizer = speech_recognition.Recognizer()

    with speech_recognition.WavFile(wav_filename) as source:
        wav_audio = recognizer.record(source)

    text = recognizer.recognize_google(wav_audio, language='ru')

    if os.path.exists(oga_filename):
        os.remove(oga_filename)

    if os.path.exists(wav_filename):
        os.remove(wav_filename)

    return text


def download_file(bot, file_id):
    # Скачивание файла, который прислал пользователь
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    filename = file_id + file_info.file_path
    filename = filename.replace('/', '_')
    with open(filename, 'wb') as f:
        f.write(downloaded_file)
    return filename


@bot.message_handler(commands=['start'])
def say_hi(message):
    # Функция, отправляющая "Привет" в ответ на команду /start
    bot.send_message(message.chat.id, 'Привет')


@bot.message_handler(commands=['gosling'])
def send_sticker(message):
    # функция отправки стикера по команде /gosling
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEK42hnXDRxJliD6xDGI9pbNyRz8RvVmAACUi0AAmTKMUuFI84cWwwXfTYE')


@bot.message_handler(content_types=['voice'])
def transcript(message):
    # Функция, отправляющая текст в ответ на голосовое
    filename = download_file(bot, message.voice.file_id)
    text = recognize_speech(filename)
    bot.send_message(message.chat.id, text)


# Запускаем бота. Он будет работать до тех пор, пока работает ячейка
# (крутится значок слева).
# Остановим ячейку - остановится бот
print('bot running')
bot.polling()
