from src.core import *
from .cutscene import Cutscene
from src.game.sprites.hamster import Hamster

class HamsterCutscene(Cutscene["LivingRoom"]):
    def __init__(self, scene: LivingRoom) -> None:
        super().__init__(scene)

        self.phase = 0
        self.timer = Timer(3.5, True)

    def start(self) -> None:
        self.timer.resume()

        player = self.scene.player
        self.initial_drawbox = player.drawbox

        self.surprise = Surprise(self.scene, player.drawbox.topright - (4, 7))
        self.scene.add(self.surprise)

        self.hamster = Hamster(self.scene, (36, 80))
        self.scene.add(self.hamster)
        self.hamster.go_to(self.scene.find_furniture("couch"), 90)

        self.scene.camera.lerp_to_centered((110, 80))

    def update(self) -> None:
        player = self.scene.player

        if self.phase == 0:
            player.animation.loop(f"still_{player.direction_text}")
            if self.timer.elapsed // 0.2 == 0:
                player.drawbox.pos.y = self.initial_drawbox.pos.y - 3
            elif self.timer.elapsed // 0.2 == 1:
                player.drawbox.pos.y = self.initial_drawbox.pos.y
            if self.timer.done:
                self.phase = 1
                self.timer.reset(5)
        elif self.phase == 1:
            self.scene.camera.lerp_to_centered_once(player.pos)
            self.scene.cutscene = None

class Surprise(Sprite["Room"]):
    update_group = UGroup.MAIN
    draw_group = DGroup.OVERLAY

    def __init__(self, scene: Room, pos: VecLike) -> None:
        super().__init__(scene)
        self.pos = Vec(pos)
        self.animation = Animation(Spritesheet.get("surprise"), 0.4)

    def update(self) -> None:
        self.animation.update()
        if self.animation.done:
            self.scene.remove(self)

    def draw(self, screen: pygame.Surface) -> None:
        screen.blit(self.animation.frame, self.screen_pos)
