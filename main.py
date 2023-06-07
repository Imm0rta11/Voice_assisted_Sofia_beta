# imports
import json
import os
import pyaudio
from datetime import datetime
import webbrowser
import requests
from phraze import text_phraze

from gtts import gTTS
from vosk import Model, KaldiRecognizer

# variables
model = Model('vosk-model-small-uk-v3-small')
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()
sophia = True
run = False


# function (their purpose is specified in the function names)
def listen():
    while True:
        data = stream.read(4000, exception_on_overflow=False)
        if (rec.AcceptWaveform(data)) and (len(data) > 0):
            answer = json.loads(rec.Result())
            if answer['text']:
                yield answer['text']


def create_note():
    for i in listen():
        if i:
            print(f'Ви вказали наступний текст для замітки: {i}')
            text_file = open('/Users/xxxx/Desktop/note.txt', 'w+')
            text_file.write(i)
            text_file.close()
            print('Ассистент СОФІЯ: замітка була збережена на робочому столі !')
            speek(text='замітка була збережена на робочому столі')
            break


def how_now_time():
    current_time_hour = str(datetime.now().hour)
    current_time_minute = str(datetime.now().minute)
    current_time = f'Ассистент СОФІЯ: зараз {current_time_hour}годин і {current_time_minute}хвилин'
    print(current_time)


def activation():
    os.system('afplay on.mp3')
    print('====Ассистент СОФІЯ активований====')
    print(f'Ви сказали: {i}')
    print('Ассистент СОФІЯ: Я вас слухаю')


def deactivation():
    os.system('afplay off.mp3')
    print('====Ассистент СОФІЯ деактивований====')


def speek(text):
    tts = gTTS(text, lang='uk')
    tts.save('hello.mp3')
    os.system('afplay hello.mp3')


def how_now_weather():
    base_url = 'http://api.openweathermap.org/data/2.5/weather?'
    api_key = 'f039fbd75b1dc47f381248ddae467482'
    city = 'ukraine'
    url = base_url + 'appid=' + api_key + '&q=' + city
    respore = requests.get(url).json()
    weather = respore['weather']
    weather1 = weather[0]
    weather2 = weather1['main']
    if weather2 == 'Clouds':
        print('Ассистент СОФІЯ: зараз хмарно')
        speek(text='зараз хмарно')
    if weather2 == 'Rainy':
        print('Ассистент СОФІЯ: зараз дощ')
        speek(text='зараз дощ')
    if weather2 == 'Clear':
        print('Ассистент СОФІЯ: зараз сонячно')


for i in listen():
    # activation
    if i in text_phraze['activation']:
        activation()
        speek(text='я вас слухаю')
        run = True
        # listen
    if run and i not in text_phraze['activation']:
        print(f'Ви сказали: {i}')
        if i in text_phraze['command_how_now_time']:
            how_now_time()
            speek(text=current_time)
        # open google.com
        if i in text_phraze['command_open_site_google']:
            print('Ассистент СОФІЯ: відкриваю гугл')
            speek(text='відкриваю гугл')
            webbrowser.open('https://google.com')
        # open YouTube.com
        if i in text_phraze['command_open_site_youtube']:
            print('Ассистент СОФІЯ: відкриваю ютуб')
            speek(text='відкриваю ютуб')
            webbrowser.open('https://youtube.com')
        # create notes
        if i in text_phraze['command_create_notes']:
            print('Ассистент СОФІЯ: який текст має бути в замітці ?')
            speek(text='який текст має бути в замітці')
            create_note()
        if i in text_phraze['command_how_now_weather']:
            how_now_weather()
        # command thanks
        if i == 'дякую':
            print('Ассистент СОФІЯ: завжди будь ласка!')
            speek(text='завжди будь ласка')
        # deactivation
        if i in text_phraze['deactivation']:
            deactivation()
            run = False
