from gtts import gTTS
import speech_recognition as sr
from pygame import mixer
import random


def talk(audio):
    print(audio)
    for line in audio.splitlines():
        text_to_speech = gTTS(text=audio, lang='en-uk')
        text_to_speech.save('audio.mp3')
        mixer.init()
        mixer.music.load("audio.mp3")
        mixer.music.play()


def myCommand():
    # Initialize the recognizer
    # The primary purpose of a Recognizer instance is, of course, to recognize speech.
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print('Hello. I am Ava. How may I help you today?')
        r.pause_threshold = 2
        # wait for a second to let the recognizer adjust the
        # energy threshold based on the surrounding noise level
        r.adjust_for_ambient_noise(source, duration=1)
        # listens for the user's input
        audio = r.listen(source)

    try:
        command = r.recognize_google(audio).lower()
        print('You said: ' + command + '\n')

    # loop back to continue to listen for commands if unrecognizable speech is received
    except sr.UnknownValueError:
        print('Your last command couldn\'t be heard')
        command = myCommand()
    return command


def avva(command):
    errors = [
        "Didn't hear you. Can you repeat yourself?",
        "I don't understand what you mean",
        "Can you repeat it please?",
    ]
    if 'hello' or 'hi' or 'Ava' in command:
        talk('Hello! I am Ava. How can I help you?')
    else:
        error = random.choice(errors)
        talk(error)


talk('Hello. I am Ava.')

# loop to continue executing multiple commands
while True:
    avva(myCommand())
