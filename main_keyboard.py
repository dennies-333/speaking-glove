import os
import tkinter as tk
from PIL import Image, ImageTk
import subprocess
import speech_recognition as sr
import pyttsx3
import threading
import socket
from pygame import mixer
import sounddevice as sd
import soundfile as sf
import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave
import json

class HomePage:
    def __init__(self, root):
        self.root = root
        self.root.title("Speaking Glove")
        self.root.attributes("-fullscreen", True)

        # Set the background image
        bg_image_path = "images/home.png"  # Replace with the path to your image
        self.bg_image = Image.open(bg_image_path)
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        self.label_bg = tk.Label(self.root, image=self.bg_image)
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

        # Rest of your code (buttons and functionality) goes here...

        # Bind key '1' to the TTS functionality
        self.root.bind('1', lambda event: self.open_tts_functionality())
        # Bind key '2' to the STT functionality
        self.root.bind('2', lambda event: self.open_stt_functionality())
        # Bind key '3' to the Images to Speech functionality
        self.root.bind('3', lambda event: self.open_images_to_speech_functionality())
        # Bind key '4' to the Save Messages functionality
        self.root.bind('4', lambda event: self.open_saved_messages_functionality())
        # Bind Ctrl+q to quit application
        self.root.bind("<Control-q>", self.quit_application)

        # Automatically focus the window
        self.root.focus_force()

    def open_tts_functionality(self, event=None):
        self.root.unbind("<Key>")
        TTSPage(self.root)

    def open_stt_functionality(self, event=None):

        def check_network_status():
            try:
                # Try to create a socket to a well-known server (Google's DNS server in this case)
                socket.create_connection(("8.8.8.8", 53))
                return 1
            except OSError:
                return 2

        status = check_network_status()
        if status == 1 :
            self.root.unbind("<Key>")
            STTPage(self.root)
        else :
            self.root.unbind("<Key>")
            App(self.root)



    def open_images_to_speech_functionality(self, event=None):
        self.root.unbind("<Key>")
        ImagesToSpeechPage(self.root)

    def open_saved_messages_functionality(self, event=None):
        self.root.unbind("<Key>")
        SavedMessagesPage(self.root)

    def quit_application(self, event=None):
        self.root.unbind("<Key>")
        self.root.destroy()

class TTSPage:
    def __init__(self, parent):
        self.parent = parent
        self.tts_window = tk.Toplevel(self.parent)
        self.tts_window.title("Text-to-Speech")
        self.tts_window.attributes("-fullscreen", True)

        self.background_image = tk.PhotoImage(file="images/background_tts.png")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Create a canvas to display the background image
        self.canvas = tk.Canvas(self.tts_window, width=screen_width, height=screen_height)
        self.canvas.pack()

        # Display the background image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        # Set the font for the input text
        font_size = 40  # You can adjust the font size as needed
        font_family = "Helvetica"
        self.input_text = tk.Text(self.tts_window, wrap=tk.WORD, font=(font_family, font_size), width=45, height=12)
        self.input_text.pack(expand=True)  #Use pack to center the text
        # Center the input_text widget both vertically and horizontally within the canvas
        self.input_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        #self.canvas.create_window(300, 200, window=self.input_text, anchor=tk.CENTER)
        self.tts_window.focus_force()

        self.input_text.focus_set()

        # Bind the Enter key to the Speak button
        self.tts_window.bind('<Return>', lambda event: self.speak_button_callback())
        # Bind the Control key to the Home button
        self.tts_window.bind('<Control_R>', lambda event: self.go_back())
    def speak_button_callback(self, event=None):
        text = self.input_text.get("1.0", tk.END).strip()
        self.text_to_speech(text)

    def text_to_speech(self, text):
        #espeak_path = r"C:\Program Files (x86)\eSpeak\TTSApp.exe"
        #subprocess.call(["espeak-ng", "-v", "en+f3", "-s", "120", "-k", "0.8", text])
        subprocess.call(["espeak-ng", "-v", "en+f5","-s", "120", "-k", "0.8", "-p", "30", "-a", "100", text])

    def go_back(self, event=None):
        self.tts_window.unbind("<Key>")
        self.tts_window.destroy()
        HomePage(self.parent)

class STTPage:
    def __init__(self, parent):
        self.parent = parent
        self.stt_window = tk.Toplevel(self.parent)
        self.stt_window.title("STT-Glove")
        self.stt_window.geometry("800x600")
        self.stt_window.attributes("-fullscreen", True)

        self.background_image = tk.PhotoImage(file="images/background2.png")

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Create a canvas to display the background image
        self.canvas = tk.Canvas(self.stt_window, width=screen_width, height=screen_height)
        self.canvas.pack()

        # Display the background image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)
        self.text_widget = tk.Text(self.stt_window, wrap=tk.WORD, font=("Sitka Small", 40), width=35, height=10)
        self.text_widget.pack(expand=False)
        self.text_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        #self.text_widget.config(width=40, height=40)
        self.recognizing_text = "Recognizing..."
        self.recognizing_fail = "Speech Transcription Failed !\nTry Again..."
        self.recognizer = sr.Recognizer()
        self.audio = pyaudio.PyAudio()

        self.is_recording = False
        self.audio_stream = None
        self.audio_segments = []

        def go_back(event=None):
            if self.is_recording:
                self.toggle_recording()  # Stop recording if active
            self.stt_window.unbind("<Key>")
            self.stt_window.destroy()
            HomePage(self.parent)


        # image_path_record = "images/record_button.png"
        # self.image_record = Image.open(image_path_record)
        # self.image_record = self.image_record.resize((100, 100))  # Resize the image if needed
        # self.photo_record = ImageTk.PhotoImage(self.image_record)
        #
        # self.record_button = tk.Button(self.stt_window, image=self.photo_record, borderwidth=0, highlightthickness=0)

        self.stt_window.bind("<Return>", self.toggle_recording)
        self.stt_window.bind("<Control_R>", go_back)  # Bind right control key to go back to home
        self.stt_window.focus_force()

    def update_text_widget(self, text):
        self.text_widget.delete(1.0, tk.END)  # Clear existing text
        self.text_widget.insert(tk.END, text) # Insert new text


    def toggle_recording(self, event=None):
        if not self.is_recording:
            # Start recording
            #self.record_button.place(x=10, y=self.stt_window.winfo_screenheight() - self.photo_record.height() - 10)
            self.is_recording = True
            self.audio_segments = []
            self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024, stream_callback=self.capture_audio)
            self.audio_stream.start_stream()
            self.update_text_widget(self.recognizing_text)
            print("Recording...")
        else:
            # Stop recording and transcribe audio
            self.is_recording = False
            print("Stopped recording.")
            #self.record_button.forget()
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

class App():
    def __init__(self, parent):
        self.parent = parent
        self.stto_window = tk.Toplevel(self.parent)
        self.stto_window.title("speech to text")
        self.stto_window.attributes("-fullscreen", True)
        self.create_widgets()
        self.initialize_recognizer()

        self.stto_window.bind("<Return>", lambda event=None: self.start_capture())
        self.stto_window.bind("<Shift-Left>", lambda event=None: self.clear())
        self.stto_window.bind("<Control_R>", lambda event=None: self.go_back())
        self.stto_window.focus_force()
    def create_widgets(self):

        # self.background_image = tk.PhotoImage(file="images/background2.png")
        #
        # screen_width = root.winfo_screenwidth()
        # screen_height = root.winfo_screenheight()
        #
        # # Create a canvas to display the background image
        # self.canvas = tk.Canvas(self.stto_window, width=screen_width, height=screen_height)
        # self.canvas.pack()
        #
        # # Display the background image on the canvas
        # self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

        self.background_image = tk.PhotoImage(file="images/background2.png")

        screen_width = self.stto_window.winfo_screenwidth()
        screen_height = self.stto_window.winfo_screenheight()

        # Create a canvas to display the background image
        self.canvas = tk.Canvas(self.stto_window, width=screen_width, height=screen_height)
        self.canvas.pack()

        # Display the background image on the canvas
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)


        self.text_widget = tk.Text(self.stto_window, wrap=tk.WORD, font=("Sitka Small", 40), width=35, height=10)
        self.text_widget.pack(expand=False)
        self.text_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # self.submit_button = tk.Button(self.stto_window, text="Talk", command=self.start_capture, font=("Arial", 16), bg="green", fg="white", padx=10, pady=5)
        # self.submit_button.pack(side=tk.BOTTOM, anchor="se")
        #
        # self.clear_button = tk.Button(self.stto_window, text="Clear", command=self.clear, font=("Arial", 16), bg="red", fg="white", padx=10, pady=5)
        # self.clear_button.pack(side=tk.BOTTOM, anchor="sw")
        # self.stto_window.bind("<Return>", self.start_capture())
        # self.stto_window.bind("<Control_R>", self.clear())

    def initialize_recognizer(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def set_text(self, text):
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert(tk.END, text)

    def clear(self):
        self.text_widget.delete("1.0", tk.END)

    def start_capture(self):
        # self.submit_button.configure(state=tk.DISABLED)
        self.set_text("Please talk")
        threading.Thread(target=self.capture, daemon=True).start()

    def capture(self):
        try:
            with self.microphone as source:
                audio_data = self.recognizer.record(source, duration=5)
            self.set_text("Recognizing.....")

            with wave.open("audio.wav", "wb") as f:
                f.setnchannels(1)
                f.setsampwidth(2)
                f.setframerate(source.SAMPLE_RATE)  # Set the sampling rate to 16kHz
                f.writeframes(audio_data.get_wav_data())

            wf = wave.open("audio.wav", "rb")
            model = Model(lang="en-in")  # Language model for English spoken by Keralites
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
                text_value = ""

            self.set_text(text_value)

        except sr.UnknownValueError:
            self.set_text("Unable to recognize speech")

        except sr.RequestError as e:
            self.set_text("Error occurred: {}".format(e))

        # self.submit_button.configure(state=tk.NORMAL)

    def go_back(self):
        self.stto_window.unbind("<key>")
        self.stto_window.destroy()
        HomePage(self.parent)


class ImagesToSpeechPage:
    def __init__(self, parent):
        self.parent = parent
        self.hmi_window = tk.Toplevel(self.parent)
        self.hmi_window.title("HMI-Viwer")
        self.hmi_window.attributes("-fullscreen", True)

        self.hmi_window.image_path = "images/images/main.png"
        self.hmi_window.photo = tk.PhotoImage(file=self.hmi_window.image_path)
        self.hmi_window.label = tk.Label(self.hmi_window, image=self.hmi_window.photo)
        self.hmi_window.label.pack(fill=tk.BOTH, expand=tk.YES)
        self.hmi_window.focus_force()
        self.process_running = False
        self.hmi_window.bind('<Control_R>', self.go_back)
        self.hmi_window.bind('<Escape>', self.default_binding)
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
        self.hmi_window.unbind("<Key>")
        self.hmi_window.destroy()
        HomePage(self.parent)

    def display_image(self, image_path):
        photo = tk.PhotoImage(file=image_path)
        self.hmi_window.label.configure(image=photo)
        self.hmi_window.label.image = photo

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
    def __init__(self, parent):
        self.parent = parent
        self.sm_window = tk.Toplevel(self.parent)
        self.sm_window.title("Saved")
        self.sm_window.attributes("-fullscreen", True)

        # Set the background image
        bg_image_path = "images/saved_message.png"  # Replace with the path to your image
        self.bg_image = Image.open(bg_image_path)
        self.bg_image = ImageTk.PhotoImage(self.bg_image)

        self.label_bg = tk.Label(self.sm_window, image=self.bg_image)
        self.label_bg.place(x=0, y=0, relwidth=1, relheight=1)

        self.label_title = tk.Label(self.sm_window, text="Saved Messages", font=("Helvetica", 20))
        self.label_title.pack()

        self.sm_window.focus_force()
        self.sm_window.bind('1', lambda event: self.show_audio_files())
        self.sm_window.bind('2', lambda event: self.show_text_files())
        self.sm_window.bind('<Control_R>', lambda event: self.go_back())
    def go_back(self, event=None):
        self.sm_window.unbind("<Key>")
        self.sm_window.destroy()
        HomePage(self.parent)

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

        # image_path_play = "images/play_button1.png"
        # self.image_play = Image.open(image_path_play)
        # self.image_play = self.image_play.resize((100, 100))  # Resize the image if needed
        # self.photo_play = ImageTk.PhotoImage(self.image_play)
        #
        # image_path_record = "images/record_button1.png"
        # self.image_record = Image.open(image_path_record)
        # self.image_record = self.image_record.resize((100, 100))  # Resize the image if needed
        # self.photo_record = ImageTk.PhotoImage(self.image_record)

        image_path_stop = "images/stop_record_button.png"
        self.image_stop = Image.open(image_path_stop)
        self.image_stop = self.image_stop.resize((100, 100))  # Resize the image if needed
        self.photo_stop = ImageTk.PhotoImage(self.image_stop)

        # image_path_back = "images/back_button.png"
        # self.image_back = Image.open(image_path_back)
        # self.image_back = self.image_back.resize((100, 100))  # Resize the image if needed
        # self.photo_back = ImageTk.PhotoImage(self.image_back)
        #
        # self.play_button = tk.Button(self.audio_viewer, image=self.photo_play, command=self.play_audio, borderwidth=0)
        # self.record_button = tk.Button(self.audio_viewer, image=self.photo_record, command=self.record_audio, borderwidth=0)
        self.stop_button = tk.Button(self.audio_viewer, image=self.photo_stop, command=self.stop_audio, borderwidth=0)
        #self.back_button = tk.Button(self.audio_viewer, image=self.photo_back, borderwidth=0)

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

    def display_image(self, image_path):
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Get the screen dimensions
        screen_width = self.audio_viewer.winfo_screenwidth()
        screen_height = self.audio_viewer.winfo_screenheight()

        # Calculate the position to center the image
        x_position = (screen_width - image.width) // 2
        y_position = (screen_height - image.height) // 2

        self.image_label.config(image=photo)
        self.image_label.image = photo
        self.image_label.place(x=x_position, y=y_position)

    def on_key_press(self, event):
        key = event.keysym
        self.common_image_path = ""
        if key in self.number_keys:
            if key == 1:
                self.common_image_path = "images/audio1.png"
            elif key == 2:
                self.common_image_path = "images/audio2.png"
            elif key == 3:
                self.common_image_path = "images/audio3.png"
            elif key == 4:
                self.common_image_path = "images/audio4.png"
            self.display_image(self.common_image_path)

            self.active_key = key  # Store the active key for recording

            #self.play_button["state"] = "normal"
            #self.record_button["state"] = "normal"
            #self.play_button.config(command=self.play_audio)
            #self.record_button.config(command=self.record_audio)
        elif key == "Escape":
            #self.play_button.forget()
            #self.record_button.forget()
            initial_image_path = "images/audio.png"
            self.display_image(initial_image_path)
            #self.play_button["state"] = "disabled"
            #self.record_button["state"] = "disabled"
        elif key == "Control_L":
            self.play_audio()
        elif key == "Shift_L":
            self.record_audio()
        elif key == "Shift_R":
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
        self.image_path = "images/text.png"  # Replace this with the path to your image
        self.image = Image.open(self.image_path)
        self.image = ImageTk.PhotoImage(self.image)
        self.text_viewer.focus_force()
        self.label_image = tk.Label(self.text_viewer, image=self.image)
        self.label_image.pack()
        self.text_widget = None

        # Bind keys '1' to '5' to corresponding functions
        self.text_viewer.bind('1', lambda event: self.show_text_file(1))
        self.text_viewer.bind('2', lambda event: self.show_text_file(2))
        self.text_viewer.bind('3', lambda event: self.show_text_file(3))
        self.text_viewer.bind('4', lambda event: self.show_text_file(4))
        self.text_viewer.bind('5', lambda event: self.show_text_file(5))
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
        elif file_number == 5:
            file_path = "text/file5.txt"
        else :

            return
        # Hide the image
        self.label_image.pack_forget()

        # Open the text file and display its content in a text widget
        with open(file_path, "r") as file:
            content = file.read()

        # Clear existing content
        if self.text_widget:
            self.text_widget.forget()

        #bg_image_path = f"images/text{file_number}.png"
        #self.background_image = tk.PhotoImage(file=bg_image_path)

        self.background_image = tk.PhotoImage(file="images/background_tts.png")  # Replace with your image path

        self.canvas = tk.Canvas(self.text_viewer, width=self.text_viewer.winfo_screenwidth(), height=self.text_viewer.winfo_screenheight())
        self.canvas.pack(fill=tk.BOTH, expand=True)  # Fill the entire window

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_image)

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
        self.text_viewer.bind('<Shift_R>', self.save_changes)
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
        # Save the changes made to the text file when right shift is pressed
        if self.editing_enabled:
            # Replace the file_path with the path to the currently displayed text file
            folder_path = "text"
            file_name = f"file{self.current_file_number}.txt"
            file_path = os.path.join(folder_path, file_name)

            content = self.text_widget.get(1.0, tk.END)

            with open(file_path, "w") as file:
                file.write(content)

            self.text_widget.config(state=tk.DISABLED)  # Disable text widget editing after saving
            self.editing_enabled = False
            # Hide the cursor after saving
            self.text_viewer.config(cursor="")

    def go_back_to_image(self, event):
        #self.text_widget = None
        print("hello")
        self.canvas.forget()
        self.text_widget.forget()

        self.image_path = "images/text.png"  # Replace this with the path to your image
        self.image = Image.open(self.image_path)
        self.image = ImageTk.PhotoImage(self.image)
        self.text_viewer.focus_force()
        self.label_image = tk.Label(self.text_viewer, image=self.image)
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
        SavedMessagesPage(self.parent)





if __name__ == '__main__':
    root = tk.Tk()
    home_page = HomePage(root)
    root.mainloop()
