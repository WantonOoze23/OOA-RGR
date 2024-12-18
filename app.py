from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from gtts import gTTS
import os
import uuid

class AudioService:
    # Папка для тимчасових аудіофайлів
    TEMP_AUDIO_PATH = 'static/'

    @staticmethod
    def remove_old_audio_files():
        """Видалення старих аудіофайлів з тимчасової папки"""
        for filename in os.listdir(AudioService.TEMP_AUDIO_PATH):
            file_path = os.path.join(AudioService.TEMP_AUDIO_PATH, filename)
            if os.path.isfile(file_path) and filename.endswith('.mp3'):
                try:
                    os.remove(file_path)
                    print(f"Deleted old audio file: {filename}")
                except Exception as e:
                    print(f"Error deleting file {filename}: {e}")

    @staticmethod
    def text_to_speech(text, language='uk', speed=1.0):
        """Перетворення тексту в аудіо"""
        try:
            # Використовуємо slow для налаштування швидкості
            slow = speed < 1.0
            tts = gTTS(text=text, lang=language, slow=slow)
            
            # Генерація унікального імені для файлу
            filename = f"static/{uuid.uuid4()}.mp3"
            
            # Видалення старих аудіофайлів перед створенням нового
            AudioService.remove_old_audio_files()
            
            # Збереження нового аудіо файлу
            tts.save(filename)
            
            return filename
        except Exception as e:
            print(f"Error in text-to-speech conversion: {e}")
            return None

    @staticmethod
    def speech_to_text(language='uk-UA'):
        """Розпізнавання мови в текст"""
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say something...")
            audio = recognizer.listen(source)
        try:
            print("You said: " + recognizer.recognize_google(audio, language=language))
            return recognizer.recognize_google(audio, language=language)
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
            return "Sorry, I could not understand the audio."
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return "Error in speech recognition."

class AppService:
    def __init__(self):
        self.app = Flask(__name__)

        # Ініціалізація маршрутів
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/text_to_speech', 'text_to_speech', self.text_to_speech_route, methods=['POST'])
        self.app.add_url_rule('/speech_to_text', 'speech_to_text', self.speech_to_text_route, methods=['POST'])

    def index(self):
        """Головна сторінка"""
        return render_template('index.html')

    def text_to_speech_route(self):
        """Маршрут для тексту в мову"""
        text = request.form['text']
        speed = float(request.form['speed'])
        language = request.form.get('language', 'uk')
        audio_file = AudioService.text_to_speech(text, language=language, speed=speed)
        if audio_file:
            return jsonify({'audio_url': audio_file})
        else:
            return jsonify({'error': 'Error in generating audio.'})

    def speech_to_text_route(self):
        """Маршрут для голосу в текст"""
        language = request.form.get('language', 'uk-UA')
        recognized_text = AudioService.speech_to_text(language=language)
        return jsonify({'recognized_text': recognized_text})

    def run(self):
        """Запуск Flask додатку"""
        self.app.run(debug=True)

if __name__ == '__main__':
    app_service = AppService()
    app_service.run()
