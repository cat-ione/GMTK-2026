from src.core import *

from .cutscene import Cutscene
from src.game.sprites.surprise import Surprise
from src.game.sprites.speech_bubble import SpeechBubble

class OpeningCutscene(Cutscene["LivingRoom"]):
    def __init__(self, scene: LivingRoom) -> None:
        super().__init__(scene)

        self.phase = 0
        self.timer = Timer(6, True)

        self.dialogue = [
            ("mom", "Hi Honey! Im heading home now, have you finished all chores I told you to do?"),
            ("daughter", "Y-yep... I'm just finishing up the last bit of cleaning..."),
            ("mom", "Alright, just dont forget anything, see you soon!"),
            ("daughter", "I won't mom, I promise..."),
        ]
        self.dialogue_index = -1
        self.current_dialogue = None

    def start(self) -> None:
        self.scene.player.disable_collision = True
        self.scene.player.animation.loop("sleeping")
        self.timer.reset()

    def update(self) -> None:
        self.skip_if_pressed()

        player = self.scene.player

        if self.phase == 0:
            if self.timer.done:
                self.phase = 1
        elif self.phase == 1:
            self.scene.player.pos = Vec(105, 41)
            self.scene.player.animation.loop("phone_2")
            self.scene.player.animation.one_shot("phone_1")
            Sound.get("ringtone").play()
            self.surprise = Surprise(self.scene, player.pos + (5, -30))
            self.scene.add(self.surprise)
            self.timer.reset(4.5)
            self.phase = 2
        elif self.phase == 2:
            if self.timer.done:
                self.scene.start_zoom_in()
                self.timer.reset(2.5)
                self.phase = 3
        elif self.phase == 3:
            self.scene.zoom_in(Vec(72, 20), 2, self.timer.progress)
            if self.timer.done:
                self.timer.reset(0)
                self.next_dialogue()
                self.phase = 4
        elif self.phase == 4:
            if self.game.keyup in {pygame.K_SPACE, pygame.K_RETURN, pygame.K_e} or any(self.game.mouse_just_pressed):
                self.next_dialogue()
                if self.dialogue_index >= len(self.dialogue):
                    self.timer.reset(2.5)
                    self.phase = 5
        elif self.phase == 5:
            self.scene.zoom_out(Vec(72, 20), 2, self.timer.progress_remaining)
            if self.timer.done:
                self.scene.end_zoom_out()
                self.scene.player.animation.loop("idle_down")
                self.timer.reset(1)
                self.phase = 6
        elif self.phase == 6:
            if self.timer.done:
                self.scene.player.disable_collision = False
                self.scene.player.pos.y += 2
                self.scene.cutscene = None
                self.scene.game_data.start_time = time.time()
                self.scene.mom_slider.start()
                pygame.mixer.music.load("res/sounds/background_music.wav")
                pygame.mixer.music.play(loops=-1, fade_ms=1000)

    def next_dialogue(self) -> None:
        if self.current_dialogue is not None:
            self.scene.remove(self.current_dialogue)
        self.dialogue_index += 1
        if self.dialogue_index >= len(self.dialogue): return
        person, text = self.dialogue[self.dialogue_index]
        pos = (125, 50) if person == "mom" else (53, 83)
        anchor = Anchor.BOTTOMRIGHT if person == "mom" else Anchor.TOPLEFT
        bubble = SpeechBubble(self.scene, pos, text, 110, anchor)
        self.scene.add(bubble)
        self.current_dialogue = bubble

    def cleanup(self) -> None:
        self.scene.player.disable_collision = False
        self.scene.hamster_cs_timer.resume()
