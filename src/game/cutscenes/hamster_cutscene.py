from src.core import *
from .cutscene import Cutscene

class HamsterCutscene(Cutscene["LivingRoom"]):
    def __init__(self, scene: LivingRoom) -> None:
        super().__init__(scene)

        self.phase = 0
        self.timer = Timer(4, True)

    def start(self) -> None:
        self.timer.resume()

        player = self.scene.player
        self.initial_drawbox = player.drawbox

        self.surprise = Surprise(self.scene, player.drawbox.topright - (4, 7))
        self.scene.add(self.surprise)

    def update(self) -> None:
        player = self.scene.player

        if self.phase == 0:
            player.animation.loop(f"still_{player.direction_text}")
            if self.timer.elapsed // 0.2 == 0:
                player.drawbox.pos.y = self.initial_drawbox.pos.y - 3
            elif self.timer.elapsed // 0.2 == 1:
                player.drawbox.pos.y = self.initial_drawbox.pos.y
            if self.timer.done:
                self.timer.reset(5)
                self.phase = 1
        elif self.phase == 1:
            # 1. Hamster run out from bedroom door to a hiding spot
            # 1.1. Simultaneously turn the player towards hamster
            # 2. Speech bubble appear: "My hamsters!"
            # 3. New item on todo: "Find all hamsters"
            # 4. Cutscene end
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
