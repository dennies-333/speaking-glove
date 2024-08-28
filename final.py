import tkinter as tk
from PIL import Image, ImageTk
import RPi.GPIO as GPIO
from tkinter import messagebox
import subprocess
import pyaudio
import speech_recognition as sr
import pyttsx3
import threading
import sounddevice as sd
import soundfile as sf
import pygame
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave
import json
import socket
import time
import numpy as np

GPIO.setmode(GPIO.BCM)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(13, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(19, GPIO.IN, pull_up_down=GPIO.PUD_UP)

txt_text_widget = ''
input_text = ''
text_widget = ''
image_path = ''
process_running = False
is_recording_stt = ''
recording = None
image_path_stop = "images/stop_record_button.png"
audio_file = ''
key = ''
main_frame = ''
current_file_number = 0
editing_enabled = False
text_widget_sm = None
recognizer = sr.Recognizer()
audio = pyaudio.PyAudio()
text_key = ''
text_file = ''
recognizer_offline = None
microphone = None

recognizing_text = "Recognizing..."
recognizing_fail = "Speech Transcription Failed !\nTry Again..."
is_recording = False
audio_stream = None
audio_segments = []
CHUNK = 1024
FORMAT = 'wav'
CHANNELS = 1
sample_rate = 44100
increment_variable = 0
duration = 0
hmi_frame = ''
sm_frame = ''
record_frames = []
increment_thread = None
recording_stt = False
recognizer_stt = sr.Recognizer()
microphone_stt = sr.Microphone()


# def gpio_bind(pin):

def setBGImage(file_source, parent_window):
    bg_image_path = file_source
    bg_image = Image.open("/home/glove/main_final/final/speakin/" + bg_image_path)
    new_size = (1285, 720)
    bg_image = bg_image.resize(new_size, Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg_image)
    label_bg = tk.Label(parent_window, image=bg_image)
    label_bg.image = bg_image
    label_bg.place(x=0, y=0, relwidth=1, relheight=1)


def setTEXT(parent_window):
    input_text = tk.Text(parent_window, wrap=tk.WORD, font=("Helvetica", 40), width=33, height=12)
    input_text.pack(expand=True)
    input_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    return input_text


def quit_application(event=None):
    root.quit()
    GPIO.cleanup()


def show_text_to_speech_page(event=None):
    global main_frame
    main_frame.destroy()
    tts_frame = tk.Frame(root, name="tts_frame")
    tts_frame.pack(fill=tk.BOTH, expand=True)
    setBGImage("images/back.png", tts_frame)
    global input_text
    input_text = setTEXT(tts_frame)
    tts_frame.pack()

    input_text.focus_set()

    def back_to_main_page(channel):
        #GPIO.remove_event_detect(16)
        GPIO.remove_event_detect(13)
        # main_bind()
        tts_frame.destroy()
        create_main_page()

    def text_to_speech(text):
        # subprocess.call(["espeak-ng", "-v", "en+f3", "-s", "120", "-k", "0.8", text])
        subprocess.call(["espeak", "-v", "en+f3", "-s", "120", "-k", "0.8", "-p", "50", text])

    def speak_button_callback(channel):
        text = input_text.get("1.0", tk.END).strip()
        text_to_speech(text)

    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(13)
    GPIO.remove_event_detect(26)
    GPIO.remove_event_detect(16)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page, bouncetime=2000)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=speak_button_callback, bouncetime=2000)
    tts_frame.bind("<Escape>", back_to_main_page)
    tts_frame.focus_set()
    


# Add your Text to Speech code and widgets here

# Function to create and show the Speech to Text pag
def show_speech_to_text_page():
    global main_frame
    main_frame.destroy()
    stt_frame = tk.Frame(root, name="sst_frame")

    stt_frame.pack(fill=tk.BOTH, expand=True)
    setBGImage("images/background2.png", stt_frame)
    global text_widget
    text_widget = setTEXT(stt_frame)
    stt_frame.pack()

    def back_to_main_page(channel):
        GPIO.remove_event_detect(6)
        GPIO.remove_event_detect(13)
        # main_bind()
        stt_frame.destroy()
        create_main_page()
    
    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(13)
    GPIO.remove_event_detect(26)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page, bouncetime=2000)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=start_recording_stt, bouncetime=2000)
    stt_frame.bind("<Escape>", back_to_main_page)
    stt_frame.focus_set()

def update_text_widget(text):
    global text_widget
    text_widget.delete(1.0, tk.END)  # Clear existing text
    text_widget.insert(tk.END, text)  # Insert new text


def start_recording_stt(event=None):
    global recording_stt
    recording_stt = True
    update_text_widget("Recognizing...")
    threading.Thread(target=record_audio_stt).start()
    GPIO.remove_event_detect(13)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=stop_recording_stt, bouncetime=2000)


def stop_recording_stt(event=None):
    global recording_stt
    recording_stt = False
    GPIO.remove_event_detect(19)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=start_recording_stt, bouncetime=2000)


def record_audio_stt():
    global recording_stt
    global recognizer_stt

    with microphone_stt as source:
        recognizer_stt.adjust_for_ambient_noise(source)

        while recording_stt:
            try:
                audio = recognizer_stt.listen(source, timeout=1)
                text = recognizer_stt.recognize_google(audio)
                update_text_widget(text)
            except sr.WaitTimeoutError:
                update_text_widget("Speech Transcription Failed !\nTry Again...")
            except sr.RequestError:
                update_text_widget("Speech Transcription Failed !\nTry Again...")
            except sr.UnknownValueError:
                update_text_widget("Speech Transcription Failed !\nTry Again...")


def show_stt_offline():
    global main_frame
    main_frame.destroy()
    stto_frame = tk.Frame(root, name="sst_frame")

    stto_frame.pack(fill=tk.BOTH, expand=True)
    setBGImage("images/background2.png", stto_frame)
    global text_widget_off
    text_widget_off = setTEXT(stto_frame)
    stto_frame.pack()

    def go_back_off(channel):
        #GPIO.remove_event_detect(16)
        GPIO.remove_event_detect(13)
        stto_frame.destroy()
        create_main_page()
    
    
    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(13)
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(26)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=go_back_off, bouncetime=2000)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=start_capture, bouncetime=2000)
    global recognizer_offline, microphone
    recognizer_offline = sr.Recognizer()
    microphone = sr.Microphone()
    stto_frame.bind("<Escape>", go_back_off)
    stto_frame.focus_set()


def set_text(text):
    global text_widget_off
    text_widget_off.delete("1.0", tk.END)
    text_widget_off.insert(tk.END, text)


def clear():
    global text_widget_off
    text_widget_off.delete("1.0", tk.END)


def start_capture(channel):
    # self.submit_button.configure(state=tk.DISABLED)
    set_text("Please talk")
    threading.Thread(target=capture, daemon=True).start()


def capture():
    try:
        global microphone, recognizer_offline
        with microphone as source:
            audio_data = recognizer_offline.record(source, duration=5)
        set_text("Recognizing.....")

        with wave.open("audio.wav", "wb") as f:
            f.setnchannels(1)
            f.setsampwidth(2)
            f.setframerate(microphone.SAMPLE_RATE)  # Set the sampling rate to 16kHz
            f.writeframes(audio_data.get_wav_data())

        wf = wave.open("audio.wav", "rb")
        model = Model(lang="en-in")
        rec = KaldiRecognizer(model, wf.getframerate())
        rec.SetWords(True)
        rec.SetPartialWords(True)

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        if 'text' in result:
            text_value = result['text']
        else:
            text_value = "try again"
        set_text(text_value)

    except sr.UnknownValueError:
        set_text("Unable to recognize speech")

    except sr.RequestError as e:
        set_text("Error occurred: {}".format(e))


# function for images to speech--------------------------------------------------------------------------------------------
def show_images_to_speech_page(event=None):
    global main_frame
    main_frame.destroy()
    global hmi_frame
    hmi_frame = tk.Frame(root, name="hmi_frame")
    hmi_frame.pack(fill=tk.BOTH, expand=True)
    setBGImage("images/images/main.png", hmi_frame)
    hmi_frame.pack()

    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    #GPIO.remove_event_detect(16)
    GPIO.remove_event_detect(26)
    GPIO.remove_event_detect(13)
    hmi_frame.bind('1', open_general_functionality)
    hmi_frame.bind('2', open_emergency_functionality)
    hmi_frame.bind('3', open_food_functionality)
    hmi_frame.bind('4', open_travel_functionality)
    hmi_frame.bind('5', open_family_functionality)
    hmi_frame.bind("<Escape>", back_to_main_page)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page, bouncetime=2000)
    hmi_frame.focus_set()


def back_to_main_page(channel):
    #GPIO.remove_event_detect(16)
    global hmi_frame
    unbind_hmi()
    hmi_frame.destroy()
    create_main_page()


def display_image(image_path):
    global hmi_frame
    setBGImage(image_path, hmi_frame)


def display_icon_and_speak(icon, text_to_speak, image_after):
    display_image(icon)
    play_audio_sm(text_to_speak)
    global hmi_frame
    hmi_frame.after(100, lambda: display_image(image_after))
    global process_running
    process_running = False


def play_audio_sm(text):
    subprocess.call(["espeak", "-v", "en+f3", "-s", "120", "-k", "0.8", "-p", "50", text])


def default_binding(event=None):
    # Reset the default bindings
    global hmi_frame
    unbind_hmi()
    hmi_frame.bind('1', open_general_functionality)
    hmi_frame.bind('2', open_emergency_functionality)
    hmi_frame.bind('3', open_food_functionality)
    hmi_frame.bind('4', open_travel_functionality)
    hmi_frame.bind('5', open_family_functionality)
    hmi_frame.bind("<Escape>", back_to_main_page)
    hmi_frame.unbind('6')
    display_image("images/images/main.png")
    global process_running
    process_running = False


def bind_speak(key, image1, text, image2):
    global hmi_frame
    hmi_frame.bind(key, lambda event: threading.Thread(target=display_icon_and_speak, args=(
        image1, text, image2)).start())


def open_general_functionality(event=None):
    global process_running, hmi_frame
    if not process_running:
        process_running = True
        unbind_hmi()
        threading.Thread(target=display_icon_and_speak,
                         args=("images/images/general-icon.png", "general", "images/general.png")).start()
        hmi_frame.bind('<Escape>', default_binding)
        bind_speak('1', "images/toilet-icon.png", "i   want   to   go   to   toilet", "images/general.png")
        bind_speak('2', "images/hungry-icon.png", "i am Hungry", "images/general.png")
        bind_speak('3', "images/sleepy-icon.png", "i   am   Sleepy", "images/general.png")
        bind_speak('4', "images/pain-icon.png", "i   am   in   Pain", "images/general.png")


def open_emergency_functionality(event=None):
    global process_running, hmi_frame
    if not process_running:
        process_running = True
        unbind_hmi()
        threading.Thread(target=display_icon_and_speak,
                         args=("images/images/emergency-icon.png", "emergency", "images/emergency.png")).start()
        hmi_frame.bind('<Escape>', default_binding)
        bind_speak('1', "images/policestation-icon.png", "call the Police", "images/emergency.png")
        bind_speak('2', "images/hospital-icon.png", "take me to the hospital", "images/emergency.png")
        bind_speak('3', "images/ambulanceicon.png", "call the Ambulance", "images/emergency.png")
        bind_speak('4', "images/firedept-icon.png", "call the Fire Force", "images/emergency.png")


def open_food_functionality(event=None):
    global process_running, hmi_frame
    if not process_running:
        process_running = True
        unbind_hmi()
        threading.Thread(target=display_icon_and_speak,
                         args=("images/food-icon.png", "food", "images/food.png")).start()
        bind_speak('1', "images/water-icon.png", "i need a glass of water", "images/food.png")
        bind_speak('2', "images/tea-icon.png", "i would like some tea", "images/food.png")
        bind_speak('3', "images/juice-icon.png", "i would love some juice", "images/food.png")
        bind_speak('4', "images/breakfast-icon.png", "i would like some breakfast", "images/food.png")
        bind_speak('5', "images/lunch-icon.png", "i am ready to have lunch", "images/food.png")
        bind_speak('6', "images/dinner-icon.png", "i am in the mood for dinner", "images/food.png")
        hmi_frame.bind('<Escape>', default_binding)


def open_travel_functionality(event=None):
    global process_running, hmi_frame
    if not process_running:
        process_running = True
        unbind_hmi()
        threading.Thread(target=display_icon_and_speak,
                         args=("images/travel-icon.png", "travel", "images/travel.png")).start()
        bind_speak('1', "images/busstop-icon.png", "Bus Stop", "images/travel.png")
        bind_speak('2', "images/auto-icon.png", "Auto Rickshaw", "images/travel.png")
        bind_speak('3', "images/taxi-icon.png", "Taxi", "images/travel.png")
        bind_speak('4', "images/trainstation-icon.png", "take me to the Railway Station", "images/travel.png")
        hmi_frame.bind('<Escape>', default_binding)


def open_family_functionality(event=None):
    global process_running, hmi_frame
    if not process_running:
        process_running = True
        unbind_hmi()
        threading.Thread(target=display_icon_and_speak,
                         args=("images/family-icon.png", "family", "images/family.png")).start()
        bind_speak('1', "images/dad.png", "hi   dad", "images/family.png")
        bind_speak('2', "images/mom.png", "hi  mum me", "images/family.png")
        bind_speak('3', "images/brother.png", "hi    bro", "images/family.png")
        bind_speak('4', "images/sister.png", "hi    sis", "images/family.png")
        bind_speak('5', "images/grandpa.png", "hi    grandpa", "images/family.png")
        bind_speak('6', "images/grandma.png", "hi    grandma", "images/family.png")
        hmi_frame.bind('<Escape>', default_binding)


def unbind_hmi():
    global hmi_frame
    hmi_frame.unbind('1')
    hmi_frame.unbind('2')
    hmi_frame.unbind('3')
    hmi_frame.unbind('4')
    hmi_frame.unbind('5')
    hmi_frame.unbind('6')
    hmi_frame.unbind('<Escape>')
    # default_binding()


# SAVED MESSAGES ____________________________________________________________________________________________________________________
# ________________________________________________________________________________________________________________________

def show_saved_messages_page(event=None):
    global main_frame
    main_frame.destroy()
    global sm_frame
    sm_frame = tk.Frame(root, name="sm_frame")
    sm_frame.pack(fill=tk.BOTH, expand=True)
    setBGImage("images/saved_message.png", sm_frame)
    sm_frame.pack()
    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(13)
    GPIO.remove_event_detect(26)
    #GPIO.remove_event_detect(16)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page_sm, bouncetime=2000)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=audio_setup_attributes, bouncetime=2000)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=text_setup_attributes, bouncetime=2000)
    #sm_frame.bind('1', back_to_main_page_sm)
    sm_frame.bind("<Escape>", back_to_main_page_sm)
    sm_frame.focus_set()


def back_to_main_page_sm(event=None):
    global sm_frame
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(6)
    #GPIO.remove_event_detect(16)
    sm_frame.destroy()
    create_main_page()


def audio_setup_attributes(event=None):
    global sm_frame
    setBGImage("images/audio.png", sm_frame)
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(6)
    #GPIO.remove_event_detect(16)
    bind_audio_key()
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=go_back_audio, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", go_back_audio)
    sm_frame.focus_set()


def play_audio(channel):
    pygame.mixer.init()
    global audio_file
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()


def record():
    global recording, record_frames, is_recording
    print("Recording...")
    recording = None
    # Allocate a buffer for the recording
    recording = np.zeros((int(sample_rate * 60 * 5), 1), dtype='int16')  # Adjust the time according to your needs
    with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16', callback=audio_callback):
        while is_recording:
            sd.sleep(1000)  # Wait for 1 second
        save_recording()


def audio_callback(indata, frames, time, status):
    global record_frames
    if status:
        print(status)
    record_frames.append((indata.copy(), frames))


def save_recording():
    global recording, record_frames, audio_file, sample_rate
    print("Saving the recording...")
    start_idx = 0
    for block, frames in record_frames:
        end_idx = start_idx + frames
        recording[start_idx:end_idx] = block
        start_idx = end_idx
    sf.write(audio_file, recording[:end_idx], sample_rate)
    print(f"Recording saved to {audio_file}")
    record_frames = []


def toggle_recording(channel):
    global is_recording, record_frames
    is_recording = not is_recording
    if is_recording:
        # Clear previous recordings
        record_frames = []
        record_thread = threading.Thread(target=record)
        record_thread.start()
    else:
        # Will trigger the recording to stop and be saved
        is_recording = False


def show_audio_file1(event=None):
    global key, file_path, audio_file
    key = 1
    file_path = "images/audio1.png"
    audio_file = "/home/glove/main_final/final/speakin/audio/file1.wav"
    print("hahahahha")
    audio_background(file_path)


def show_audio_file2(event=None):
    global key, file_path, audio_file
    key = 2
    file_path = "images/audio2.png"
    audio_file = "/home/glove/main_final/final/speakin/file2.wav";
    audio_background(file_path)


def show_audio_file3(event=None):
    global key, file_path, audio_file
    key = 3
    file_path = "images/audio3.png"
    audio_file = "/home/glove/main_final/final/speakin/audio/file3.wav"
    audio_background(file_path)


def show_audio_file4(event=None):
    global key, file_path, audio_file
    key = 4
    file_path = "images/audio4.png"
    audio_file = "/home/glove/main_final/final/speakin/audio/file4.wav"
    audio_background(file_path)


def audio_background(file_path):
    global sm_frame
    setBGImage(file_path, sm_frame)
    #GPIO.remove_event_detect(16)
    unbind_audio_key()
    GPIO.add_event_detect(13, GPIO.FALLING, callback=play_audio, bouncetime=2000)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=toggle_recording, bouncetime=2000)
    # GPIO.add_event_detect(6, GPIO.FALLING, callback=stop_audio, bouncetime=2000)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=initial, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", initial)
    sm_frame.focus_set()


def initial(event=None):
    global sm_frame
    setBGImage("images/audio.png", sm_frame)
    GPIO.remove_event_detect(13)
    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    #GPIO.remove_event_detect(16)
    bind_audio_key()
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=go_back_audio, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", go_back_audio)
    sm_frame.focus_set()


def go_back_audio(event=None):
    unbind_audio_key()
    GPIO.remove_event_detect(16)
    global sm_frame
    setBGImage("images/saved_message.png", sm_frame)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page_sm, bouncetime=2000)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=audio_setup_attributes, bouncetime=2000)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=text_setup_attributes, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", back_to_main_page_sm)
    sm_frame.focus_set()


def bind_audio_key():
    global sm_frame
    sm_frame.bind('1', show_audio_file1)
    sm_frame.bind('2', show_audio_file2)
    sm_frame.bind('3', show_audio_file3)
    sm_frame.bind('4', show_audio_file4)
    sm_frame.focus_set()


def unbind_audio_key():
    global sm_frame
    sm_frame.unbind('1')
    sm_frame.unbind('2')
    sm_frame.unbind('3')
    sm_frame.unbind('4')


def text_setup_attributes(event=None):
    global sm_frame
    setBGImage("images/text.png", sm_frame)
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(6)
    #GPIO.remove_event_detect(16)
    bind_text_key()
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=go_back_txt, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", go_back_txt)
    sm_frame.focus_set()


def show_text_file1(event=None):
    global text_key, text_file
    text_key = 1
    file_path = "images/audio_back.png"
    text_file = "/home/glove/main_final/final/speakin/text/file1.txt"
    text_background(file_path)


def show_text_file2(event=None):
    global text_key, text_file
    text_key = 1
    file_path = "images/audio_back.png"
    text_file = "/home/glove/main_final/final/speakin/text/file2.txt"
    text_background(file_path)


def show_text_file3(event=None):
    global text_key, text_file
    text_key = 1
    file_path = "images/audio_back.png"
    text_file = "/home/glove/main_final/final/speakin/text/file3.txt"
    text_background(file_path)


def show_text_file4(event=None):
    global text_key, text_file
    text_key = 1
    file_path = "images/audio_back.png"
    text_file = "/home/glove/main_final/final/speakin/text/file4.txt"
    text_background(file_path)


def text_background(file_path):
    # Implement text_background functionality
    global sm_frame
    setBGImage(file_path, sm_frame)
    unbind_text_key()
    #GPIO.remove_event_detect(16)
    global text_file
    with open(text_file, "r") as file:
        content = file.read()
    global txt_text_widget, text_key
    if txt_text_widget:
        txt_text_widget.pack_forget()
    txt_text_widget = setTEXT(sm_frame)
    txt_text_widget.insert(tk.END, content)
    current_file_number = key
    txt_text_widget.config(state=tk.DISABLED)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=enable_editing, bouncetime=2000)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=save_changes, bouncetime=2000)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=go_back_to_image, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", go_back_to_image)
    sm_frame.focus_set()


def enable_editing(event=None):
    # Implement enable_editing functionality
    global editing_enabled, txt_text_widget
    editing_enabled = True
    txt_text_widget.config(state=tk.NORMAL)
    txt_text_widget.configure(insertwidth=1)
    txt_text_widget.focus_set()


def save_changes(event=None):
    # Implement save_changes functionality
    global editing_enabled, text_file, txt_text_widget
    if editing_enabled:
        file_path = text_file
        content = txt_text_widget.get(1.0, tk.END)
        with open(file_path, "w") as file:
            file.write(content)
        txt_text_widget.config(state=tk.DISABLED)
        editing_enabled = False
        # parent.config(cursor="")


def go_back_to_image(event=None):
    # Implement go_back_to_image functionality
    global txt_text_widget, sm_frame
    txt_text_widget.pack_forget()
    setBGImage("images/text.png", sm_frame)
    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    # GPIO.remove_event_detect(3)
    #GPIO.remove_event_detect(16)
    bind_text_key()
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=go_back_txt, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", go_back_txt)
    sm_frame.focus_set()


def go_back_txt(event=None):
    # Implement go_back functionality
    unbind_text_key()
    #GPIO.remove_event_detect(16)
    global sm_frame
    setBGImage("images/saved_message.png", sm_frame)
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page_sm, bouncetime=2000)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=audio_setup_attributes, bouncetime=2000)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=text_setup_attributes, bouncetime=2000)
    sm_frame.unbind('<Escape>')
    sm_frame.bind("<Escape>", back_to_main_page_sm)
    sm_frame.focus_set()
    


def bind_text_key():
    global sm_frame
    sm_frame.bind('1', show_text_file1)
    sm_frame.bind('2', show_text_file2)
    sm_frame.bind('3', show_text_file3)
    sm_frame.bind('4', show_text_file4)
    sm_frame.focus_set()


def unbind_text_key():
    global sm_frame
    sm_frame.unbind('1')
    sm_frame.unbind('2')
    sm_frame.unbind('3')
    sm_frame.unbind('4')


# -----------------------------------------------------------------------------------
# ------------------------------------------------------------------------


def show_contact(event=None):
    global main_frame
    main_frame.destroy()
    ct_frame = tk.Frame(root, name="ct_frame")

    ct_frame.pack(fill=tk.BOTH, expand=True)
    setBGImage("images/contact.png", ct_frame)
    ct_frame.pack()
    GPIO.remove_event_detect(6)
    GPIO.remove_event_detect(19)
    #GPIO.remove_event_detect(16)
    GPIO.remove_event_detect(26)
    GPIO.remove_event_detect(13)

    def back_to_main_page(channel):
        GPIO.remove_event_detect(16)
        ct_frame.destroy()
        create_main_page()

    #GPIO.add_event_detect(16, GPIO.FALLING, callback=back_to_main_page, bouncetime=2000)
    ct_frame.bind("<Escape>", back_to_main_page)


# -----------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------
# Function to handle GPIO events
def gpio_callback(channel):
    def check_network_status():
        try:
            socket.create_connection(("8.8.8.8", 53))
            return 1
        except OSError:
            return 2
    status = check_network_status()
    if status == 1:
        show_speech_to_text_page()
    else:
        show_stt_offline()


def main_unbind():
    GPIO.remove_event_detect(6)
    main_frame.unbind('2')
    GPIO.remove_event_detect(19)
    GPIO.remove_event_detect(16)
    GPIO.remove_event_detect(26)
    GPIO.remove_event_detect(13)


def main_bind():
    #GPIO.add_event_detect(16, GPIO.FALLING, callback=gpio_callback, bouncetime=2000)
    GPIO.add_event_detect(19, GPIO.FALLING, callback=show_images_to_speech_page, bouncetime=2000)
    GPIO.add_event_detect(26, GPIO.FALLING, callback=show_text_to_speech_page, bouncetime=2000)
    # GPIO.add_event_detect(26, GPIO.FALLING, callback=quit_application, bouncetime=2000)
    GPIO.add_event_detect(13, GPIO.FALLING, callback=show_contact, bouncetime=2000)
    GPIO.add_event_detect(6, GPIO.FALLING, callback=show_saved_messages_page, bouncetime=2000)


# Function to create the main page
def create_main_page():
    global main_frame
    main_frame = tk.Frame(root)
    main_bind()
    # GPIO.add_event_detect(26, GPIO.FALLING, callback=show_saved_messages_page, bouncetime=2000)
    main_frame.pack()
    main_frame.bind('2', gpio_callback)
    main_frame.focus_set()


# Create the main tkinter window
root = tk.Tk()
root.title("Speech and Text Converter")
root.attributes("-fullscreen", True)
setBGImage("images/home.png", root)
# main_bind()

# Create the main page
create_main_page()

# Main loop
root.mainloop()

# Cleanup GPIO settings when the application exits
GPIO.cleanup()
