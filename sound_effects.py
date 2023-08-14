from pygame import mixer
import time

mixer.init()

class Sound:
    """创建一个管理音效的类"""
    def __init__(self):
        """设置游戏音效"""
        self.start = mixer.Sound('sounds/MESSAGE-B_Accept.wav')
        self.start.set_volume(0.8)
        self.switch = mixer.Sound('sounds/switch5.wav')
        self.laser = mixer.Sound('sounds/laser6.mp3')
        self.explosion = mixer.Sound('sounds/explodemini.wav')
        self.explosion.set_volume(0.5)
        self.level = mixer.Sound('sounds/MENU A_Select.wav')
        self.level.set_volume(0.9)
        self.hit = mixer.Sound('sounds/negative.wav')

    def play_BGM(self):
        """设置游戏BGM"""
        mixer.music.load('sounds/fato_shadow_-_lunar_strings.mp3')
        mixer.music.set_volume(0.35)
        mixer.music.play(loops=-1)