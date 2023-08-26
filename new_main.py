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
import time

def bind_keys(key_function_map, parent_window):
    print("haha")
    for key, callback in key_function_map.items():
        parent_window.bind(key, lambda event, cb=callback: cb())

def unbind_keys(key_function_map, parent_window):
    for key, callback in key_function_map.items():
        parent_window.unbind(key)


def setBGImage(file_source, parent_window):
    bg_image_path = file_source
    bg_image = Image.open(bg_image_path)
    new_size = (1400, 800)
    bg_image = bg_image.resize(new_size, Image.LANCZOS)
    bg_image = ImageTk.PhotoImage(bg_image)
    label_bg = tk.Label(parent_window, image=bg_image)
    label_bg.image = bg_image
    label_bg.place(x=0, y=0, relwidth=1, relheight=1)

def setTEXTBG(file_source, parent_window):
    original_image = Image.open(file_source)
    canvas_width = parent_window.winfo_screenwidth()
    canvas_height = parent_window.winfo_screenheight()
    resized_image = original_image.resize((canvas_width, canvas_height), Image.LANCZOS)
    background_image = ImageTk.PhotoImage(resized_image)
    canvas = tk.Canvas(parent_window, width=canvas_width, height=canvas_height)
    canvas.pack()
    canvas.background = background_image
    canvas.create_image(0, 0, anchor=tk.NW, image=background_image)
    return canvas

def setTEXT(parent_window):
    input_text = tk.Text(parent_window, wrap=tk.WORD, font=("Helvetica", 40), width=43, height=12)
    input_text.pack(expand=True)
    input_text.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    return input_text


class HomePage:

    def __init__(self, root):
        self.root = root
        self.key_function_map = {
            '1': self.open_tts_functionality,
            '2': self.open_stt_functionality,
            '3': self.open_images_to_speech_functionality,
            '4': self.open_saved_messages_functionality,
            '<Control-q>': self.quit_application
        }
        self.setup_attributes()


    def setup_attributes(self):
        self.root.title("Speaking Glove")
        self.root.attributes("-fullscreen", True)
        self.bind_pins()
        setBGImage(
            "images/home.png",
            self.root)
        self.root.focus_force()

    def bind_pins(self):
        bind_keys(self.key_function_map, self.root)
        pass


    def open_tts_functionality(self):
        self.root.unbind("<Key>")
        TTSPage(self.root)

    def open_stt_functionality(self):
        self.root.unbind("<Key>")
        STTPage(self.root)

    def open_images_to_speech_functionality(self):
        self.root.unbind("<Key>")
        ImagesToSpeechPage(self.root)

    def open_saved_messages_functionality(self):
        self.root.unbind("<Key>")
        SavedMessagesPage(self.root)

    def quit_application(self):
        self.root.unbind("<Key>")
        self.root.destroy()

class TTSPage(HomePage):
    def __init__(self, parent):
        self.parent = parent
        self.key_function_map_tts = {
            "<Return>": self.speak_button_callback,
            "<Control_R>": self.go_back
        }
        self.tts_setup_attributes()

    def tts_setup_attributes(self):
        # self.tts_window = tk.Toplevel(self.parent)
        # self.tts_window.title("Text-to-Speech")
        # self.tts_window.attributes("-fullscreen", True)
        #
        # bind_keys(self.key_function_map_tts, self.tts_window)
        # self.input_text = setTEXT(self.tts_window)
        # self.tts_window.focus_force()
        # self.input_text.focus_set()
        # setTEXTBG(
        #     "images/saved_message.png",
        #     self.tts_window
        # )
        self.tts_window = tk.Toplevel(self.parent)
        self.tts_window.title("Text-to-Speech")
        self.tts_window.attributes("-fullscreen", True)
        bind_keys(self.key_function_map_tts, self.tts_window)
        setTEXTBG(
            "images/back.png",
            self.tts_window
        )
        self.input_text = setTEXT(self.tts_window)
        self.tts_window.focus_force()
        self.input_text.focus_set()


    def speak_button_callback(self, event=None):
        text = self.input_text.get("1.0", tk.END).strip()
        self.text_to_speech(text)

    def text_to_speech(self, text):
        # subprocess.call(["espeak-ng", "-v", "en+f3", "-s", "120", "-k", "0.8", text])
        subprocess.call(["espeak", "-v", "en+m2", "-s", "120", "-k", "0.8", text])

    def go_back(self):
        print("back")
        #bind_keys(self.key_function_map)
        self.tts_window.destroy()


class STTPage(HomePage):
    def __init__(self, parent):
        self.parent = parent
        self.key_function_map_stt = {
            "<Return>": self.toggle_recording,
            "<Control_R>": self.go_back
        }
        self.recognizing_text = "Recognizing..."
        self.recognizing_fail = "Speech Transcription Failed !\nTry Again..."
        self.recognizer = sr.Recognizer()
        self.audio = pyaudio.PyAudio()
        self.is_recording = False
        self.audio_stream = None
        self.audio_segments = []
        self.stt_setup_attributes()

    def stt_setup_attributes(self):
        self.stt_window = tk.Toplevel(self.parent)
        self.stt_window.title("Speech-To-Text")
        self.stt_window.attributes("-fullscreen", True)
        bind_keys(self.key_function_map_stt, self.stt_window)
        setTEXTBG(
            "images/background2.png",
            self.stt_window
        )
        self.text_widget = setTEXT(self.stt_window)
        self.stt_window.focus_force()
        self.text_widget.focus_set()

        # image_path_record = "images/record_button.png"
        # image_record = Image.open(image_path_record)
        # image_record = image_record.resize((100, 100))  # Resize the image if needed
        # photo_record = ImageTk.PhotoImage(image_record)
        # self.record_button = tk.Button(self.stt_window, image=photo_record, borderwidth=0, highlightthickness=0)

        self.stt_window.focus_force()

    def go_back(self):
        print("back")
        if self. is_recording:
            self.toggle_recording()
        self.stt_window.unbind("<Key>")
        #bind_keys(self.key_function_map)
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

class ImagesToSpeechPage:

    def __init__(self, parent):
        self.parent = parent
        self.key_function_map_its = {
            '1': self.open_general_functionality,
            '2': self.open_emergency_functionality,
            '3': self.open_food_functionality,
            '4': self.open_travel_functionality,
            '5': self.open_family_functionality,
            '<Control_R>': self.go_back,
            '<Escape>': self.default_binding
            }
        self.its_setup_attributes()

    def its_setup_attributes(self):
        self.hmi_window = tk.Toplevel(self.parent)
        self.hmi_window.title("HMI-Viwer")
        self.hmi_window.attributes("-fullscreen", True)
        bind_keys(self.key_function_map_its, self.hmi_window)
        self.hmi_window.focus_force()
        self.hmi_window.image_path = "images/images/main.png"
        self.hmi_window.photo = tk.PhotoImage(file=self.hmi_window.image_path)
        self.hmi_window.label = tk.Label(self.hmi_window, image=self.hmi_window.photo)
        self.hmi_window.label.pack(fill=tk.BOTH, expand=tk.YES)
        self.hmi_window.focus_force()
        self.process_running = False

    def set_female_voice(self, engine, voice_index):
        voices = engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            engine.setProperty('voice', voices[voice_index].id)
        else:
            print("Invalid voice index.")

    def go_back(self, event=None):
        self.hmi_window.unbind("<Key>")
        # bind_keys(self.key_function_map)
        self.hmi_window.destroy()


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

    def bind_speak(self, key, image1, text, image2):
        self.hmi_window.bind(key, lambda event: threading.Thread(target=self.display_icon_and_speak, args=(
        image1, text, image2)).start())

    def open_general_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak,
            args=("images/images/general-icon.png", "general", "images/general.png")).start()
            self.hmi_window.unbind('5')
            self.hmi_window.unbind('6')
            self.bind_speak('1', "images/toilet-icon.png", "i   want   to   go   to   toilet", "images/general.png")
            self.bind_speak('2', "images/hungry-icon.png", "i am Hungry", "images/general.png")
            self.bind_speak('3', "images/sleepy-icon.png", "i   am   Sleepy", "images/general.png")
            self.bind_speak('4', "images/pain-icon.png", "i   am   in   Pain", "images/general.png")


    def open_emergency_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/images/emergency-icon.png", "emergency", "images/emergency.png")).start()
            self.hmi_window.unbind('5')
            self.hmi_window.unbind('6')
            self.bind_speak('1', "images/policestation-icon.png", "call the Police", "images/emergency.png")
            self.bind_speak('2', "images/hospital-icon.png", "take me to the hospital", "images/emergency.png")
            self.bind_speak('3', "images/ambulanceicon.png", "call the Ambulance", "images/emergency.png")
            self.bind_speak('4', "images/firedept-icon.png", "call the Fire Force", "images/emergency.png")
    def open_food_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/food-icon.png", "food", "images/food.png")).start()
            self.bind_speak('1', "images/water-icon.png", "i need a glass of water", "images/food.png")
            self.bind_speak('2', "images/tea-icon.png", "i would like some tea", "images/food.png")
            self.bind_speak('3', "images/juice-icon.png", "i would love some juice", "images/food.png")
            self.bind_speak('4', "images/breakfast-icon.png", "i would like some breakfast", "images/food.png")
            self.bind_speak('5', "images/lunch-icon.png", "i am ready to have lunch", "images/food.png")
            self.bind_speak('6', "images/dinner-icon.png", "i am in the mood for dinner", "images/food.png")

    def open_travel_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/travel-icon.png", "travel", "images/travel.png")).start()
            self.hmi_window.unbind('5')
            self.hmi_window.unbind('6')
            self.bind_speak('1', "images/busstop-icon.png", "Bus Stop", "images/travel.png")
            self.bind_speak('2', "images/auto-icon.png", "Auto Rickshaw", "images/travel.png")
            self.bind_speak('3', "images/taxi-icon.png", "Taxi", "images/travel.png")
            self.bind_speak('4', "images/trainstation-icon.png", "take me to the Railway Station", "images/travel.png")
    def open_family_functionality(self, event=None):
        if not self.process_running:
            self.process_running = True
            threading.Thread(target=self.display_icon_and_speak, args=("images/family-icon.png", "family", "images/family.png")).start()
            self.bind_speak('1', "images/dad.png", "hi   dad", "images/family.png")
            self.bind_speak('2', "images/mom.png", "hi  mum me", "images/family.png")
            self.bind_speak('3', "images/brother.png", "hi    bro", "images/family.png")
            self.bind_speak('4', "images/sister.png", "hi    sis", "images/family.png")
            self.bind_speak('5', "images/grandpa.png", "hi    grandpa", "images/family.png")
            self.bind_speak('6', "images/grandma.png", "hi    grandma", "images/family.png")

class SavedMessagesPage(HomePage):
    def __init__(self,parent):
        self.parent = parent
        self.key_function_map_sm = {
            '1': self.show_audio_files,
            '2': self.show_text_files,
            "<Control_R>": self.go_back
        }
        self.sm_setup_attributes()

    def sm_setup_attributes(self):
        self.sm_window = tk.Toplevel(self.parent)
        self.sm_window.title("Saved")
        self.sm_window.attributes("-fullscreen", True)
        bind_keys(self.key_function_map_sm, self.sm_window)
        setBGImage("images/saved_message.png", self.sm_window)
        self.sm_window.focus_force()

    def go_back(self):
        unbind_keys(self.key_function_map_sm, self.sm_window)
        # bind_keys(self.key_function_map)
        self.sm_window.destroy()

    def show_text_files(self, event=None):
        unbind_keys(self.key_function_map_sm, self.sm_window)
        self.sm_window.unbind("<Key>")
        self.sm_window.destroy()
        TextViewer(self.parent)
    def show_audio_files(self, event=None):
        unbind_keys(self.key_function_map_sm, self.sm_window)
        self.sm_window.unbind("<Key>")
        self.sm_window.destroy()
        AudioViewer(self.parent)


"""class AudioViewer :
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
        image = Image.open(image_path).resize((screen_width,screen_height), Image.LANCZOS)
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
        SavedMessagesPage(self.parent)"""

class AudioViewer:
    CHUNK = 1024
    FORMAT = 'wav'
    CHANNELS = 1

    def __init__(self, parent):
        self.parent = parent
        print("audio_viewer")
        self.key_function_map_audio = {
            '1': self.show_audio_file1,
            '2': self.show_audio_file2,
            '3': self.show_audio_file3,
            '4': self.show_audio_file4,
            "<Control_R>": self.go_back
        }
        self.key_function_map_audio1 = {
            "<Escape>": self.initial,
            "<Control_L>": self.play_audio,
            "<Shift_L>": self.record_audio,
            "<Alt_L>": self.stop_audio
        }
        self.audio_setup_attributes()

    def audio_setup_attributes(self):
        self.audio_viewer = tk.Toplevel(self.parent)
        self.audio_viewer.title("Audio-Files-Viewer")
        self.audio_viewer.attributes("-fullscreen", True)
        self.audio_viewer.focus_force()
        bind_keys(self.key_function_map_audio, self.audio_viewer)

        setBGImage("images/audio.png", self.audio_viewer)
        self.audio_viewer.focus_force()

        self.recording = None

        image_path_stop = "images/stop_record_button.png"
        self.image_stop = Image.open(image_path_stop)
        self.image_stop = self.image_stop.resize((100, 100))  # Resize the image if needed
        self.photo_stop = ImageTk.PhotoImage(self.image_stop)

        self.stop_button = tk.Button(self.audio_viewer, image=self.photo_stop, command=self.stop_audio, borderwidth=0)


    def play_audio(self):

        def audio_player():
            print('play')
            data, fs = sf.read(self.audio_file)
            sd.play(data, fs)
            sd.wait()

        audio_thread = threading.Thread(target=audio_player)
        audio_thread.start()

    def record_audio(self):
        self.stop_button.pack(side=tk.BOTTOM, anchor=tk.CENTER)
        self.stop_button.config(state=tk.NORMAL)
        self.record = self.key
        print("recording begins")
        self.recording = sd.rec(int(10 * 44100), samplerate=44100, channels=1)

    def stop_audio(self):
        self.stop_button.forget()
        sd.stop()
        file_path = self.audio_file
        sf.write(file_path, self.recording, 44100)
        self.recording = None
        self.stop_button.config(state=tk.DISABLED)
        self.stop_button.pack_forget()

    def show_audio_file1(self):
        self.key = 1
        file_path = "images/audio1.png"
        self.audio_file = "audio/file1.wav"
        self.audio_background(file_path)
    def show_audio_file2(self):
        self.key = 2
        file_path = "images/audio2.png"
        self.audio_file = "audio/file1.wav"
        self.audio_background(file_path)
    def show_audio_file3(self):
        self.key = 3
        file_path = "images/audio3.png"
        self.audio_file = "audio/file1.wav"
        self.audio_background(file_path)
    def show_audio_file4(self):
        self.key = 4
        file_path = "images/audio4.png"
        self.audio_file = "audio/file1.wav"
        self.audio_background(file_path)

    def audio_background(self, file_path):
        setBGImage(file_path, self.audio_viewer)
        unbind_keys(self.key_function_map_audio, self.audio_viewer)
        bind_keys(self.key_function_map_audio1, self.audio_viewer)

    def initial(self):
        unbind_keys(self.key_function_map_audio1, self.audio_viewer)
        bind_keys(self.key_function_map_audio, self.audio_viewer)
        setBGImage("images/audio.png", self.audio_viewer)

    def go_back(self, event=None):
        print("go back")
        unbind_keys(self.key_function_map_audio, self.audio_viewer)
        unbind_keys(self.key_function_map_audio1, self.audio_viewer)
        self.audio_viewer.destroy()
        SavedMessagesPage(self.parent)


class TextViewer :

    def __init__(self, parent):
        self.parent = parent
        self.key_function_map_text = {
            '1': self.show_text_file1,
            '2': self.show_text_file2,
            '3': self.show_text_file3,
            '4': self.show_text_file4,
            "<Control_R>": self.go_back
        }
        self.key_function_map_edit = {
            "<Shift_L>": self.enable_editing,
            "<Alt_L>": self.save_changes,
            "<Escape>": self.go_back_to_image
        }
        self.text_setup_attributes()

    def text_setup_attributes(self):

        self.text_viewer = tk.Toplevel(self.parent)
        self.text_viewer.title("Text-Files-Viewer")
        self.text_viewer.attributes("-fullscreen", True)
        setBGImage("images/text.png", self.text_viewer)
        bind_keys(self.key_function_map_text, self.text_viewer)
        self.text_viewer.focus_force()
        self.current_file_number = 0
        self.editing_enabled = False
        self.text_widget = None

    def show_text_file1(self):
        self.key = 1
        file_path = "images/text1.png"
        self.text_file = "text/file1.txt"
        self.text_background(file_path)

    def show_text_file2(self):
        self.key = 1
        file_path = "images/text2.png"
        self.text_file = "text/file2.txt"
        self.text_background(file_path)

    def show_text_file3(self):
        self.key = 1
        file_path = "images/text3.png"
        self.text_file = "text/file3.txt"
        self.text_background(file_path)

    def show_text_file4(self):
        self.key = 1
        file_path = "images/text4.png"
        self.text_file = "text/file4.txt"
        self.text_background(file_path)

    def text_background(self, file_path):
        unbind_keys(self.key_function_map_text, self.text_viewer)
        with open(self.text_file, "r") as file:
            content = file.read()

        if self.text_widget:
            self.text_widget.pack_forget()

        self.canvas = setTEXTBG(file_path, self.text_viewer)
        self.text_widget = setTEXT(self.text_viewer)
        self.text_widget.insert(tk.END, content)
        self.current_file_number = self.key
        self.text_widget.config(state=tk.DISABLED)
        bind_keys(self.key_function_map_edit, self.text_viewer)

    def enable_editing(self):
        # Enable text widget editing when shift is pressed
        self.editing_enabled = True
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.configure(insertwidth=1)
        self.text_widget.focus_set()

    def save_changes(self):
        if self.editing_enabled:
            file_path = self.text_file
            content = self.text_widget.get(1.0, tk.END)
            with open(file_path, "w") as file:
                file.write(content)
            self.text_widget.config(state=tk.DISABLED)  # Disable text widget editing after saving
            self.editing_enabled = False
            self.text_viewer.config(cursor="")

    def go_back_to_image(self):
        self.text_widget.pack_forget()
        self.canvas.forget()
        setBGImage("images/text.png", self.text_viewer)
        unbind_keys(self.key_function_map_edit, self.text_viewer)
        bind_keys(self.key_function_map_text, self.text_viewer)


    def go_back(self):
        self.text_viewer.unbind("<Key>")
        self.text_viewer.destroy()
        SavedMessagesPage(self.parent)

if __name__ == '__main__':
    root = tk.Tk()
    home_page = HomePage(root)
    root.mainloop()
