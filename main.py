import os
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import speech_recognition as sr
import pyttsx3
import threading
from pygame import mixer
import sounddevice as sd
import soundfile as sf
import pyaudio
import RPi.GPIO as GPIO
import time

def bind_gpio_pins(pins_functions):
    GPIO.setmode(GPIO.BCM)
    for pin, function in pins_functions.items():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(pin, GPIO.FALLING, callback=function, bouncetime=300)

def unbind_gpio_pins(pins_functions):
    for pin, function in pins_functions.items():
        GPIO.remove_event_detect(pin)


class HomePage:

    def __init__(self, root):
        self.root = root
        self.pin_functions = {
			6: self.open_tts_functionality,
			19: self.open_stt_functionality,
			13: self.quit_application
		}

        self.attributes()


    def attributes(self):
        self.root.title("Speaking Glove")
        self.root.attributes("-fullscreen", True)

        bg_image_path = "images/home.png"  # Replace with the path to your image
        bg_image = Image.open(bg_image_path)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        bg_image = bg_image.resize((screen_width, screen_height), Image.ANTIALIAS)
        bg_image = ImageTk.PhotoImage(bg_image)

        label_bg = tk.Label(self.root, image=bg_image)
        label_bg.place(x=0, y=0, relwidth=1, relheight=1)


        bind_gpio_pins(self.pin_functions)
        self.root.focus_force()
    def open_tts_functionality(self, channel):
        unbind_gpio_pins(self.pin_functions)
        TTSPage(self.root, self.pin_functions)

    def open_stt_functionality(self, channel):
        unbind_gpio_pins(self.pin_functions)
        STTPage(self.root, self.pin_functions)

    def quit_application(self, channel):
        unbind_gpio_pins(self.pin_functions)
        self.root.destroy()

class TTSPage:
    def __init__(self, parent, pin_functions):
        self.parent = parent
        self.pin_functions = pin_functions
        self.tts_attributes()

    def tts_attributes(self):
        self.tts_window = tk.Toplevel(self.parent)
        self.tts_window.title("Text-to-Speech")
        self.tts_window.attributes("-fullscreen", True)

        background_image = tk.PhotoImage(file="images/saved_message.png")

        screen_width = self.tts_window.winfo_screenwidth()
        screen_height = self.tts_window.winfo_screenheight()

        canvas = tk.Canvas(self.tts_window, width=screen_width, height=screen_height)
        canvas.pack()

        canvas.create_image(0, 0, anchor=tk.NW, image=background_image)

        font_size = 40
        font_family = "Helvetica"
        self.input_text = tk.Text(self.tts_window, wrap=tk.WORD, font=(font_family, font_size), width=35, height=12)
        self.input_text.pack(expand=True)
        self.input_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.tts_window.focus_force()
        self.input_text.focus_set()

        self.tts_pin_function = {
            6 : self.speak_button_callback,
            13: self.go_back
        }

        bind_gpio_pins(self.tts_pin_function)

    def speak_button_callback(self, event=None):
        text = self.input_text.get("1.0", tk.END).strip()
        self.text_to_speech(text)

    def text_to_speech(self, text):
        # subprocess.call(["espeak-ng", "-v", "en+f3", "-s", "120", "-k", "0.8", text])
        subprocess.call(["espeak", "-v", "en+m2", "-s", "120", "-k", "0.8", text])

    def go_back(self, channel):
        unbind_gpio_pins(self.tts_pin_function)
        bind_gpio_pins(self.pin_functions)
        self.tts_window.destroy()


class STTPage:
    def __init__(self, parent, pin_functions):
        self.parent = parent
        self.pin_functions = pin_functions
        self.stt_attributes()

    def stt_attributes(self):
        self.stt_window = tk.Toplevel(self.parent)
        self.stt_window.title("STT-Glove")
        self.stt_window.geometry("800x600")
        self.stt_window.attributes("-fullscreen", True)

        background_image = tk.PhotoImage(file="images/background2.png")

        screen_width = self.stt_window.winfo_screenwidth()
        screen_height = self.stt_window.winfo_screenheight()

        canvas = tk.Canvas(self.stt_window, width=screen_width, height=screen_height)
        canvas.pack()

        canvas.create_image(0, 0, anchor=tk.NW, image=background_image)

        self.text_widget = tk.Text(self.stt_window, wrap=tk.WORD, font=("Sitka Small", 40), width=35, height=10)
        self.text_widget.pack(expand=False)
        self.text_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.recognizing_text = "Recognizing..."
        self.recognizing_fail = "Speech Transcription Failed !\nTry Again..."
        self.recognizer = sr.Recognizer()
        self.audio = pyaudio.PyAudio()

        self.is_recording = False
        self.audio_stream = None
        self.audio_segments = []

        # def go_back(event=None):
        #     if self.is_recording:
        #         self.toggle_recording()  # Stop recording if active
        #     self.unbin_key2()
        #     self.stt_window.destroy()
        #     HomePage.bind_key(self.homePageObject)

        image_path_record = "images/record_button.png"
        image_record = Image.open(image_path_record)
        image_record = image_record.resize((100, 100))  # Resize the image if needed
        self.photo_record = ImageTk.PhotoImage(image_record)
        print("fifth")

        record_button = tk.Button(self.stt_window, image=self.photo_record, borderwidth=0, highlightthickness=0)

        self.stt_pin_functions = {
            6 : self.toggle_recording,
            13 : self.go_back
        }


        bind_gpio_pins(self.stt_pin_functions)

        self.stt_window.focus_force()

    def go_back(self, channel):
        if self. is_recording:
            self.toggle_recording()  # Stop recording if active
        unbind_gpio_pins(self.stt_pin_functions)
        bind_gpio_pins(self.pin_functions)
        self.stt_window.destroy()


    def update_text_widget(self, text):
        self.text_widget.delete(1.0, tk.END)  # Clear existing text
        self.text_widget.insert(tk.END, text)  # Insert new text

    def toggle_recording(self, event=None):
        if not self.is_recording:
            # Start recording
            #self.record_button.place(x=10, y=self.stt_window.winfo_screenheight() - self.photo_record.height() - 10)
            self.is_recording = True
            self.audio_segments = []
            self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True,
                                                frames_per_buffer=1024, stream_callback=self.capture_audio)
            self.audio_stream.start_stream()
            self.update_text_widget(self.recognizing_text)
            print("Recording...")
        else:
            # Stop recording and transcribe audio
            self.is_recording = False
            print("Stopped recording.")
            self.record_button.forget()
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            try:
                combined_audio_data = b''.join(self.audio_segments)
                audio_data = sr.AudioData(combined_audio_data, 16000, 2)  # 2 represents sample width in bytes
                recognized_text = self.recognizer.recognize_google(audio_data)
                self.update_text_widget(recognized_text)
            except sr.UnknownValueError:
                self.update_text_widget(self.recognizing_fail)
                print("Google Speech Recognition could not understand audio")
            except sr.RequestError as e:
                print("Could not request results from Google Speech Recognition service; {0}".format(e))

    def capture_audio(self, in_data, frame_count, time_info, status):
        if self.is_recording:
            self.audio_segments.append(in_data)
        return in_data, pyaudio.paContinue



"""class ImagesToSpeechPage:
    def __init__(self, homePageObject, parent):
        self.parent = parent
        self.homePageObject = homePageObject
        self.hmi_window = tk.Toplevel(self.parent)
        self.hmi_window.title("HMI-Viwer")
        self.hmi_window.attributes("-fullscreen", True)

        self.image_path = "images/images/main.png"
        screen_width = self.hmi_window.winfo_screenwidth()
        screen_height = self.hmi_window.winfo_screenheight()
        pil_image = Image.open(self.image_path).resize((screen_width,screen_height), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(pil_image)
        self.label = tk.Label(self.hmi_window, image=self.photo)
        self.label.pack(fill=tk.BOTH, expand=tk.YES)
        self.hmi_window.focus_force()

        #self.hmi_window.image_path = "images/home.png"  # Replace with the path to your image
        #self.hmi_image = Image.open(self.hmi_window.image_path)
        #screen_width = self.hmi_window.winfo_screenwidth()
        #screen_height = self.hmi_window.winfo_screenheight()
        #self.hmi_image = self.hmi_image.resize((screen_width, screen_height), Image.ANTIALIAS)
        #self.hmi_image = ImageTk.PhotoImage(self.hmi_image)

        #self.hmi_window.image_path = "images/images/main.png"
        #self.hmi_window.photo = tk.PhotoImage(file=self.hmi_window.image_path)
        #self.hmi_window.label = tk.Label(self.hmi_window, image=self.hmi_window.photo)
        #self.hmi_window.label.pack(fill=tk.BOTH, expand=tk.YES)
        #self.hmi_window.focus_force()
        self.process_running = False

        self.back_button = 6
        self.binding_button = 13

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.back_button, self.binding_button], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection for GPIO pins
        GPIO.add_event_detect(self.back_button, GPIO.FALLING, callback=self.go_back(), bouncetime=2000)
        GPIO.add_event_detect(self.binding_button, GPIO.FALLING, callback=self.default_binding(), bouncetime=2000)


        self.hmi_window.bind('1', self.open_general_functionality)
        self.hmi_window.bind('2', self.open_emergency_functionality)
        self.hmi_window.bind('3', self.open_food_functionality)
        self.hmi_window.bind('4', self.open_travel_functionality)
        self.hmi_window.bind('5', self.open_family_functionality)

    def set_female_voice(self, engine, voice_index):
        voices = engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
        else:
            print("Invalid voice index.")

    def go_back(self, event=None):
        self.unbind_key()
        self.hmi_window.destroy()
        HomePage.bind_key(self.homePageObject)

    def unbind_key(self):
        GPIO.remove_event_detect(self.back_button)
        GPIO.remove_event_detect(self.binding_button)

    def display_image(self, image_path):
        #photo = tk.PhotoImage(file=image_path)
        #self.label.configure(image=photo)
        #self.label.image = photo
        screen_width = self.hmi_window.winfo_screenwidth()
        screen_height = self.hmi_window.winfo_screenheight()

        pil_image = Image.open(image_path).resize((screen_width, screen_height))
        photo = ImageTk.PhotoImage(pil_image)

        self.label.configure(image=photo)
        self.label.image = photo

    def display_icon_and_speak(self, icon, text_to_speak, image_after):
        self.display_image(icon)
        self.play_audio(text_to_speak)
        self.hmi_window.after(100, lambda: self.display_image(image_after))
        self.process_running = False

    def play_audio(self, text):
        engine = pyttsx3.init()
        #self.set_female_voice(engine, 1)
        engine.say(text)
        engine.runAndWait()

    def default_binding(self, event=None):
        # Reset the default bindings
        self.hmi_window.bind('1', self.open_general_functionality)
        self.hmi_window.bind('2', self.open_emergency_functionality)
        self.hmi_window.bind('3', self.open_food_functionality)
        self.hmi_window.bind('4', self.open_travel_functionality)
        self.hmi_window.bind('5', self.open_family_functionality)
        self.hmi_window.unbind('6')
        self.display_image(self.hmi_window.image_path)
        self.process_running = False

    def open_general_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/images/general-icon.png", "general", "images/general.png")).start()
            # Rebind keys '1', '2', '3', and '4' to speak specific texts
            self.hmi_window.unbind('5')
            self.hmi_window.bind('1', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/toilet-icon.png", "i   want   to   go   to   toilet", "images/general.png")).start())
            self.hmi_window.bind('2', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/hungry-icon.png", "i am Hungry", "images/general.png")).start())
            self.hmi_window.bind('3', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/sleepy-icon.png", "i   am   Sleepy", "images/general.png")).start())
            self.hmi_window.bind('4', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/pain-icon.png", "i   am   in   Pain", "images/general.png")).start())

    def open_emergency_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/images/emergency-icon.png", "emergency", "images/emergency.png")).start()
            self.hmi_window.unbind('5')
            self.hmi_window.bind('1', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/policestation-icon.png", "call the Police", "images/emergency.png")).start())
            self.hmi_window.bind('2', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/hospital-icon.png", "take me to the hospital", "images/emergency.png")).start())
            self.hmi_window.bind('3', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/ambulanceicon.png", "call the Ambulance", "images/emergency.png")).start())
            self.hmi_window.bind('4', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/firedept-icon.png", "call the Fire Force", "images/emergency.png")).start())

    def open_food_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/food-icon.png", "food", "images/food.png")).start()
            self.hmi_window.unbind('5')
            self.hmi_window.bind('1', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/water-icon.png", "i need a glass of water", "images/food.png")).start())
            self.hmi_window.bind('2', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/tea-icon.png", "i would like some tea", "images/food.png")).start())
            self.hmi_window.bind('3', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/juice-icon.png", "i would love some juice", "images/food.png")).start())
            self.hmi_window.bind('4', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/breakfast-icon.png", "i would like some breakfast", "images/food.png")).start())
            self.hmi_window.bind('5', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/lunch-icon.png", "i am ready to have lunch", "images/food.png")).start())
            self.hmi_window.bind('6', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/dinner-icon.png", "i am in the mood for dinner", "images/food.png")).start())

    def open_travel_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/travel-icon.png", "travel", "images/travel.png")).start()
            self.hmi_window.unbind('5')
            self.hmi_window.bind('1', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/busstop-icon.png", "Bus Stop", "images/travel.png")).start())
            self.hmi_window.bind('2', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/auto-icon.png", "Auto Rickshaw", "images/travel.png")).start())
            self.hmi_window.bind('3', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/taxi-icon.png", "Taxi", "images/travel.png")).start())
            self.hmi_window.bind('4', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/trainstation-icon.png", "take me to the Railway Station", "images/travel.png")).start())

    def open_family_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/family-icon.png", "family", "images/family.png")).start()
            self.hmi_window.bind('1', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/dad.png", "hi   dad", "images/family.png")).start())
            self.hmi_window.bind('2', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/mom.png", "hi  mum me", "images/family.png")).start())
            self.hmi_window.bind('3', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/brother.png", "hi    bro", "images/family.png")).start())
            self.hmi_window.bind('4', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/sister.png", "hi    sis", "images/family.png")).start())
            self.hmi_window.bind('5', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/grandpa.png", "hi    grandpa", "images/family.png")).start())
            self.hmi_window.bind('6', lambda event: threading.Thread(target=self.display_icon_and_speak, args=("images/grandma.png", "hi    grandma", "images/family.png")).start())
class SavedMessagesPage:
    def __init__(self, homePageObject, parent):
        self.parent = parent
        self.homePageObject = homePageObject
        self.sm_window = tk.Toplevel(self.parent)
        self.sm_window.title("Saved")
        self.sm_window.attributes("-fullscreen", True)


        self.bg_image_path = "images/saved_message.png"
        screen_width = self.sm_window.winfo_screenwidth()
        screen_height = self.sm_window.winfo_screenheight()
        pil_image = Image.open(self.bg_image_path).resize((screen_width,screen_height), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(pil_image)
        self.label = tk.Label(self.sm_window, image=self.photo)
        self.label.pack(fill=tk.BOTH, expand=tk.YES)

        # Set the background image
        #bg_image_path = "images/saved_message.png"  # Replace with the path to your image
        #self.bg_image = Image.open(bg_image_path)
        #self.bg_image = ImageTk.PhotoImage(self.bg_image)

        #self.label_bg = tk.Label(self.sm_window, image=self.bg_image)
        #self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

        #self.label_title = tk.Label(self.sm_window, text="Saved Messages", font=("Helvetica", 20))
        #self.label_title.pack()

        self.sm_window.focus_force()

        self.audio_button = 6
        self.text_button = 13
        self.back_button = 26

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([self.audio_button, self.text_button, self.back_button], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Add event detection for GPIO pins
        GPIO.add_event_detect(self.audio_button, GPIO.FALLING, callback=self.show_audio_files(), bouncetime=2000)
        GPIO.add_event_detect(self.text_button, GPIO.FALLING, callback=self.show_text_files(), bouncetime=2000)
        GPIO.add_event_detect(self.back_button, GPIO.FALLING, callback=self.go_back(), bouncetime=2000)

        # self.sm_window.bind('1', lambda event: self.show_audio_files())
        # self.sm_window.bind('2', lambda event: self.show_text_files())
        # self.sm_window.bind('<Control_R>', lambda event: self.go_back())
    def go_back(self, channel):
        self.unbind_key()
        self.sm_window.destroy()
        HomePage.bind_key(self.homePageObject)

    def unbind_key(self):
        GPIO.remove_event_detect(self.audio_button)
        GPIO.remove_event_detect(self.text_button)
        GPIO.remove_event_detect(self.back_button)


    def show_text_files(self, event=None):
        self.sm_window.unbind("<Key>")
        self.sm_window.destroy()
        TextViewer(self.parent)
    def show_audio_files(self, event=None):
        self.sm_window.unbind("<Key>")
        self.sm_window.destroy()
        AudioViewer(self.parent)


class AudioViewer :
    CHUNK = 1024
    FORMAT = 'wav'
    CHANNELS = 1
    #RATE = 44100
    def __init__(self, parent):
        print("First")
        self.parent = parent
        self.audio_viewer = tk.Toplevel(self.parent)
        self.audio_viewer.title("Audio-Files-Viewer")
        self.audio_viewer.attributes("-fullscreen", True)
        self.active_key = None
        self.recording = None
        self.number_keys = ['1', '2', '3', '4']
        self.file_mapping = {'1': "file1.wav", '2': "file2.wav", '3': "file3.wav", '4': "file4.wav"}
        self.audio_file_paths = [os.path.join("audio", self.file_mapping[key]) for key in self.number_keys]

        self.image_label = tk.Label(self.audio_viewer)
        self.image_label.pack()

        self.display_image("images/audio.png")
        self.audio_viewer.focus_force()

        image_path_stop = "images/stop_record_button.png"
        self.image_stop = Image.open(image_path_stop)
        self.image_stop = self.image_stop.resize((100, 100))  # Resize the image if needed
        self.photo_stop = ImageTk.PhotoImage(self.image_stop)

        self.stop_button = tk.Button(self.audio_viewer, image=self.photo_stop, command=self.stop_audio, borderwidth=0)

        self.audio_viewer.bind("<KeyPress>", self.on_key_press)

    def play_audio(self):
        audio_file = self.audio_file_paths[self.number_keys.index(self.active_key)]

        def audio_player():
            print('play')
            data, fs = sf.read(audio_file)
            sd.play(data, fs)
            sd.wait()

        audio_thread = threading.Thread(target=audio_player)
        audio_thread.start()

    def record_audio(self):
        self.stop_button.pack(side=tk.BOTTOM, anchor=tk.CENTER)
        key = self.active_key.lower()
        self.stop_button.config(state=tk.NORMAL)
        self.record = self.number_keys.index(key)
        print("recording begins")
        self.recording = sd.rec(int(10 * 44100), samplerate=44100, channels=1)

    def stop_audio(self):
        self.stop_button.forget()
        print("stop")
        sd.stop()
        file_path = self.audio_file_paths[self.record]
        sf.write(file_path, self.recording, 44100)
        self.recording = None
        self.stop_button.config(state=tk.DISABLED)
        self.stop_button.pack_forget()

    def display_image(self,image_path):


        screen_width = self.audio_viewer.winfo_screenwidth()
        screen_height = self.audio_viewer.winfo_screenheight()
        image = Image.open(image_path).resize((screen_width,screen_height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.image_label.pack(fill=tk.BOTH, expand=tk.YES)

    def on_key_press(self, event):
        key = event.keysym
        if key in self.number_keys:
            if key == "1":
                self.common_image_path = "images/audio1.png"
            elif key == "2":
                self.common_image_path = "images/audio2.png"
            elif key == "3":
                self.common_image_path = "images/audio3.png"
            elif key == "4":
                self.common_image_path = "images/audio4.png"
            self.display_image(self.common_image_path)

            self.active_key = key  # Store the active key for recording

        elif key == "Escape":

            initial_image_path = "images/audio.png"
            self.display_image(initial_image_path)

        elif key == "Control_L":
            self.play_audio()
        elif key == "Shift_L":
            self.record_audio()
        elif key == "Alt_L":
            self.stop_audio()
        elif key == "Control_R" :
            self.go_back()

    def go_back(self, event=None):
        print("go back")
        self.audio_viewer.unbind("<Key>")
        self.audio_viewer.destroy()
        SavedMessagesPage(self.parent)


class TextViewer :

    def __init__(self, parent) :
        self.parent = parent
        #self.parent.withdraw()  # Hide the parent window
        self.text_viewer = tk.Toplevel(self.parent)
        self.text_viewer.title("Text-Files-Viewer")
        self.text_viewer.attributes("-fullscreen", True)
        bg1_image_path = "images/text.png"  # Replace with the path to your image
        self.bg1_image = Image.open(bg1_image_path)
        screen_width = self.text_viewer.winfo_screenwidth()
        screen_height = self.text_viewer.winfo_screenheight()
        self.bg1_image = self.bg1_image.resize((screen_width, screen_height), Image.ANTIALIAS)
        self.text_viewer.focus_force()
        self.bg1_image_tk = ImageTk.PhotoImage(self.bg1_image)
        self.label_image = tk.Label(self.text_viewer, image=self.bg1_image_tk)
        self.label_image.pack()
        self.text_widget = None

        # Bind keys '1' to '5' to corresponding functions
        self.text_viewer.bind('1', lambda event: self.show_text_file(1))
        self.text_viewer.bind('2', lambda event: self.show_text_file(2))
        self.text_viewer.bind('3', lambda event: self.show_text_file(3))
        self.text_viewer.bind('4', lambda event: self.show_text_file(4))
        self.text_viewer.bind('<Control_R>', self.go_back)

        self.current_file_number = 0
        self.editing_enabled = False

    def show_text_file(self, file_number):
        if file_number == 1:
            file_path = "text/file1.txt"
        elif file_number == 2:
            file_path = "text/file2.txt"
        elif file_number == 3:
            file_path = "text/file3.txt"
        elif file_number == 4:
            file_path = "text/file4.txt"
        else :

            return
        # Hide the image
        self.label_image.pack_forget()

        # Open the text file and display its content in a text widget
        with open(file_path, "r") as file:
            content = file.read()

        # Clear existing content
        if self.text_widget:
            self.text_widget.pack_forget()

        screen_width = self.text_viewer.winfo_screenwidth()
        screen_height = self.text_viewer.winfo_screenheight()
        bg_image_path = f"images/text{file_number}.png"
        self.background_image = tk.PhotoImage(file=bg_image_path)

        self.canvas = tk.Canvas(self.text_viewer, width=screen_width, height=screen_height, background = "blue")
        self.canvas.pack()
        self.canvas.create_image(screen_width // 2, screen_height // 2, anchor=tk.CENTER, image=self.background_image)

        self.text_widget = tk.Text(self.text_viewer, wrap=tk.WORD, font=("Sitka Small", 40), width=32, height=9)
        self.text_widget.insert(tk.END, content)
        self.text_widget.pack()
        self.text_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.current_file_number = file_number
        # Disable text widget editing by default
        self.text_widget.config(state=tk.DISABLED)

        # Bind left shift to enable editing
        self.text_viewer.bind('<Shift_L>', self.enable_editing)
        # Bind right shift to save changes
        self.text_viewer.bind('<Alt_L>', self.save_changes)
        # Bind escape key to go back to the image
        self.text_viewer.bind('<Escape>', self.go_back_to_image)

        self.text_viewer.unbind('1')
        self.text_viewer.unbind('2')
        self.text_viewer.unbind('3')
        self.text_viewer.unbind('4')



    def enable_editing(self, event):
        # Enable text widget editing when shift is pressed
        self.editing_enabled = True
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.configure(insertwidth=1)
        self.text_widget.focus_set()

    def save_changes(self, event):
        print("haha")
        # Save the changes made to the text file when right shift is pressed
        if self.editing_enabled:
            # Replace the file_path with the path to the currently displayed text file
            folder_path = "text"
            file_name = f"file{self.current_file_number}.txt"
            file_path = os.path.join(folder_path, file_name)
            print("veendum")
            content = self.text_widget.get(1.0, tk.END)

            with open(file_path, "w") as file:
                file.write(content)

            self.text_widget.config(state=tk.DISABLED)  # Disable text widget editing after saving
            self.editing_enabled = False
            # Hide the cursor after saving
            self.text_viewer.config(cursor="")

    def go_back_to_image(self, event):
        print("escape")
        # Go back to the image viewer window when esc is pressed
        #if self.text_widget:
        self.canvas.forget()
        bg1_image_path = "images/text.png"  # Replace with the path to your image
        self.bg1_image = Image.open(bg1_image_path)
        screen_width = self.text_viewer.winfo_screenwidth()
        screen_height = self.text_viewer.winfo_screenheight()
        self.bg1_image = self.bg1_image.resize((screen_width, screen_height), Image.ANTIALIAS)
        self.text_viewer.focus_force()
        self.bg1_image_tk = ImageTk.PhotoImage(self.bg1_image)
        self.label_image = tk.Label(self.text_viewer, image=self.bg1_image_tk)
        self.label_image.pack()

        self.text_viewer.unbind('<Shift_L>')
        self.text_viewer.unbind('<Shift_R>')
        self.text_viewer.unbind('<Escape>')
        self.text_viewer.bind('1', lambda event: self.show_text_file(1))
        self.text_viewer.bind('2', lambda event: self.show_text_file(2))
        self.text_viewer.bind('3', lambda event: self.show_text_file(3))
        self.text_viewer.bind('4', lambda event: self.show_text_file(4))


    def go_back(self, event=None):
        print("go back")
        self.text_viewer.unbind("<Key>")
        self.text_viewer.destroy()
        SavedMessagesPage(self.parent)"""

if __name__ == '__main__':
    root = tk.Tk()
    home_page = HomePage(root)
    root.mainloop()
