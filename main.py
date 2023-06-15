# imports
import json
import os
import pyaudio
from datetime import datetime
import webbrowser
import requests
import sys
import multiprocessing
from multiprocessing import Process, Value
import threading
import pystray
import sys
import PIL.Image
from phraze import text_phraze

from gtts import gTTS
from vosk import Model, KaldiRecognizer

# variables
model = Model('vosk-model-small-uk-v3-small')
rec = KaldiRecognizer(model, 16000)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
stream.start_stream()
run_var = Value('b', False)
app_run_var = Value('b', True)

# virables weather
base_url = 'http://api.openweathermap.org/data/2.5/weather?'
api_key = 'f039fbd75b1dc47f381248ddae467482'
city = 'Ivano-Frankivsk'
url = base_url + 'appid=' + api_key + '&q=' + city
respore = requests.get(url).json()


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
    global current_time
    current_time_hour = str(datetime.now().hour)
    current_time_minute = str(datetime.now().minute)
    current_time = f'зараз {current_time_hour}годин і {current_time_minute}хвилин'
    print(f'Ассистент СОФІЯ: {current_time}')


def activation(run_var):
    os.system('afplay on.mp3')
    print('====Ассистент СОФІЯ активований====')
    print('Ассистент СОФІЯ: Я вас слухаю')
    speek(text='я вас слухаю')
    run_var.value = True


def deactivation(run_var):
    os.system('afplay off.mp3')
    print('====Ассистент СОФІЯ деактивований====')
    run_var.value = False


def speek(text):
    tts = gTTS(text, lang='uk')
    tts.save('hello.mp3')
    os.system('afplay hello.mp3')


def how_now_weather():
    weather = respore['weather'][0]['main']
    if weather == 'Clouds':
        print('Ассистент СОФІЯ: зараз хмарно')
        speek(text='зараз хмарно')
    elif weather == 'Rain':
        print('Ассистент СОФІЯ: зараз дощ')
        speek(text='зараз дощ')
    elif weather == 'Clear':
        print('Ассистент СОФІЯ: зараз сонячно')


def how_now_celsius():
    temp_kelvin = str(round(respore['main']['temp'] - 273.15))
    print(f'Ассистент СОФІЯ: зараз {temp_kelvin}°С')
    speek(text=f'зараз {temp_kelvin} градусів')


def activation_icon(run_var):
    def activation_on_trey():
        activation(run_var)

    def deactivation_on_trey():
        deactivation(run_var)

    icon = pystray.Icon('Neural', image, menu=pystray.Menu(
        pystray.MenuItem('Activate assistance', activation_on_trey),
        pystray.MenuItem('Deactivation assistance', deactivation_on_trey),
    ))
    icon.run()


def listen_wrapper(run_var):
    global i
    for i in listen():
        # activation
        if i in text_phraze['activation']:
            activation(run_var)
            # listen
        if run_var.value:
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
            # how now weather
            if i in text_phraze['command_how_now_weather']:
                how_now_weather()
            # how now celsius
            if i in text_phraze['command_how_now_celsius']:
                how_now_celsius()
            # command thanks
            if i == 'дякую':
                print('Ассистент СОФІЯ: завжди будь ласка!')
                speek(text='завжди будь ласка')
            # deactivation
            if i in text_phraze['deactivation']:
                deactivation(run_var)
                run_var.value = False


listen_process = Process(target=listen_wrapper, args=(run_var,))
activation_process = Process(target=activation_icon, args=(run_var,))
image = PIL.Image.open('icon.png')

if __name__ == '__main__':
    activation_process.start()
    listen_process.start()
    activation_process.join()
    listen_process.join()
