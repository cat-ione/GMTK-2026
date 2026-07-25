from src.core import *
from .cutscene import Cutscene
from src.game.sprites.hamster import Hamster
from src.game.sprites.furniture import BedroomDoor

class HamsterCutscene(Cutscene["LivingRoom"]):
    def __init__(self, scene: LivingRoom) -> None:
        super().__init__(scene)

        self.phase = 0
        self.jump_timer = Timer(0.6, True)
        self.awe_timer = Timer(2, True)

    def start(self) -> None:
        self.jump_timer.resume()

        player = self.scene.player
        self.initial_drawbox = player.drawbox

        self.surprise = Surprise(self.scene, player.drawbox.topright - (4, 7))
        self.scene.add(self.surprise)

        self.hamster = Hamster(self.scene, (36, 80))
        self.scene.add(self.hamster)
        self.hamster.go_to(self.scene.find_furniture("couch"), 90)

        self.scene.camera.lerp_to_centered((70, 40))

    def update(self) -> None:
        player = self.scene.player

        if self.phase == 0:
            player.animation.loop(f"still_{player.direction_text}")
            if self.jump_timer.elapsed // 0.2 == 0:
                player.drawbox.pos.y = self.initial_drawbox.pos.y - 3
            elif self.jump_timer.elapsed // 0.2 == 1:
                player.drawbox.pos.y = self.initial_drawbox.pos.y
            if self.surprise.animation.done:
                self.phase = 1
        elif self.phase == 1:
            if player.pos.x > 37:
                player.keys[pygame.K_a] = True
                player._move()
                player._update_animation()
            elif player.pos.y < 80:
                player.keys[pygame.K_s] = True
                player._move()
                player._update_animation()
            else:
                self.scene.cutscene = None
                self.scene.camera.stop_lerp()
                living_room = self.scene.game_data.living_room
                bedroom = self.scene.game_data.bedroom
                bathroom = self.scene.game_data.bathroom
                for _ in range(7):
                    hamster = Hamster(bedroom, (50, 80))
                    bedroom.add(hamster)
                    hamster.go_to_random(90)
                for _ in range(2):
                    hamster = Hamster(bathroom, (30, 60))
                    bathroom.add(hamster)
                    hamster.go_to_random(90)
                for _ in range(2):
                    hamster = Hamster(living_room, (100, 60))
                    living_room.add(hamster)
                    hamster.go_to_random(90)

                door = cast(BedroomDoor, self.scene.find_furniture("door"))
                door.interact()

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
