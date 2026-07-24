from src.core.util.debug.crash_handler import CrashHandler
from src.core.util.debug.watcher import Watcher
from src.resources import define_resources
from src.core.util import *
from src.settings import *
from .scene import Scene
import asyncio
import pygame

class AbortScene(Exception):
    def __str__(self):
        return "Scene aborted but not caught with a try/except block."

class AbortGame(Exception):
    def __str__(self):
        return "Game aborted but not caught with a try/except block."

class Game:
    def __init__(self, initial_scene: type[Scene]) -> None:
        self.initial_scene = initial_scene

        pygame.init()
        self.px_screen = pygame.Surface(SIZE)
        self.screen = pygame.display.set_mode(Vec(SIZE) * PX, pygame.SCALED)
        pygame.display.set_caption(TITLE)
        self.fullscreen = False

        self.frame_count = 0
        self.dt = 1 / FPS
        self.fps = 500

        if __debug__:
            Logger.init("game", self)
            Watcher.init("game", self)
            Watcher.step()
            CrashHandler.init("game")
            Overlay.init()

        self.f3_combo_pressed = False
        self.show_hitboxes = False

        define_resources()
        Resource.preload()

    async def run(self) -> None:
        exit_status = "clean"
        clock = pygame.time.Clock()
        self.scene = self.initial_scene(self)
        if __debug__:
            self.update_profiler = Profiler(self.scene.update)
            self.draw_profiler = Profiler(self.scene.draw)
            self.events_profiler = Profiler(self._poll_events)

        try:
            while True:
                await asyncio.sleep(0)
                self.dt = clock.tick(FPS) / 1000
                self.fps = clock.get_fps()
                self.frame_count += 1
                if __debug__:
                    Watcher.step()

                if __debug__:
                    watch("FPS", round(self.fps))
                    watch("Frame", self.frame_count)

                if __debug__:
                    self.events_profiler()
                else:
                    self._poll_events()

                try:
                    if __debug__:
                        self.update_profiler()
                    else:
                        self.scene.update()
                except AbortScene:
                    continue

                if __debug__:
                    self.draw_profiler(self.px_screen)
                else:
                    self.scene.draw(self.px_screen)
                scaled_screen = pygame.transform.scale_by(self.px_screen, PX)
                self.screen.blit(scaled_screen, (0, 0))
                if __debug__:
                    Overlay.draw(self.screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            exit_status = "keyboard_interrupt"
        except AbortGame:
            info("Game aborted normally")
        except Exception as e:
            if __debug__:
                CrashHandler.dump(self, e)
            exit_status = "crashed"
        finally:
            if __debug__:
                Watcher.dump(exit_status)
                Logger.dump(exit_status)
            pygame.quit()

    def set_scene(self, scene: Scene) -> Never:
        self.scene = scene
        if __debug__:
            self.update_profiler = Profiler(self.scene.update)
            self.draw_profiler = Profiler(self.scene.draw)
            self.events_profiler = Profiler(self._poll_events)
        raise AbortScene

    def _poll_events(self) -> None:
        self.events = {event.type: event for event in pygame.event.get()}
        self.keydown = -1
        if pygame.KEYDOWN in self.events:
            self.keydown = self.events[pygame.KEYDOWN].key
        self.keyup = -1
        if pygame.KEYUP in self.events:
            self.keyup = self.events[pygame.KEYUP].key

        self.keys = pygame.key.get_pressed()
        self.mouse_pos = Vec(pygame.mouse.get_pos())
        self.mouse_pressed = pygame.mouse.get_pressed()
        self.mouse_just_pressed = pygame.mouse.get_just_pressed()
        self.mouse_just_released = pygame.mouse.get_just_released()

        if pygame.QUIT in self.events:
            raise AbortGame

        if self.keyup == pygame.K_F11:
            self.fullscreen = not self.fullscreen
            if self.fullscreen:
                pygame.display.set_mode(SIZE, pygame.FULLSCREEN | pygame.SCALED)
            else:
                pygame.display.set_mode(SIZE, pygame.SCALED)
            info(f"Fullscreen: {["Off", "On"][self.fullscreen]}")

        if __debug__:
            if self.keyup == pygame.K_F3:
                if self.f3_combo_pressed:
                    self.f3_combo_pressed = False
                else:
                    Overlay.toggle()
                    info(f"Overlay: {["Off", "On"][Overlay.visible]}")
            if self.keys[pygame.K_F3]:
                if self.keydown not in {-1, pygame.K_F3}:
                    self.f3_combo_pressed = True
                if self.keydown == pygame.K_b:
                    self.show_hitboxes = not self.show_hitboxes
                    info(f"Show hitboxes: {["Off", "On"][self.show_hitboxes]}")

            Profiler.update(self.keydown)
