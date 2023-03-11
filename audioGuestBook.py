#! /usr/bin/env python3

import audioInterface
import os
import yaml
import sys
import pygame

from datetime import datetime
from gpiozero import Button
from signal import pause
from pydub import AudioSegment
from pydub.playback import play

dir = '/home/pi/recordings/'
recordings = ['*.wav']

try:
    with open("config.yaml") as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError as e:
    print(
        f"Could not find the config.yaml file. FileNotFoundError: {e}. Check config location and retry."
    )
    sys.exit(1)

hook = Button(config["hook_gpio"])
back_button = Button(config["button_gpio"])


def off_hook() -> None:
    print("Phone off hook, ready to begin!")
    audio_interface = audioInterface.AudioInterface(config, hook)

    # playback voice message through speaker
    print("Playing voicemail message...")
    play(
        AudioSegment.from_wav(
            os.path.dirname(os.path.abspath(config["source_file"]))
            + "/sounds/voicemail.wav"
        )
        - config["playback_reduction"]
    )

    # start recording beep
    print("Playing beep...")
    play(
        AudioSegment.from_wav(
            os.path.dirname(os.path.abspath(config["source_file"])) + "/sounds/beep.wav"
        )
        - config["beep_reduction"]
    )

    # now, while phone is off the hook, record audio from the microphone
    print("recording")
    audio_interface.record()
    audio_interface.stop()
    output_file = (
        os.path.dirname(os.path.abspath(config["source_file"]))
        + "/recordings/"
        + f"{datetime.now().isoformat()}"
    )
    audio_interface.close(output_file + ".wav")
    print("Finished recording!")


def on_hook() -> None:
    print("Phone on hook.\nSleeping...")

def playback():
    # pygame setup
    pygame.mixier.init()
    speaker_volume = 0.5 # 50% Volume
    pygame.mixer.music.set_volume(speaker_volume)

    for recording in recordings:
        pygame.mixer.music.load(os.path.dirname(os.path.abspath(config["source_file"]))
        + "/recordings/" + recording)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() == True:
            continue

def main():
    hook.when_pressed = off_hook
    hook.when_released = on_hook
    back_button.when_pressed = playback
    pause()

if __name__ == "__main__":
    main()
