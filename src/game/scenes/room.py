from src.core import *

from src.game.sprites.item import Item
from src.game.sprites.dust import Dust
from src.game.sprites.furniture import Furniture, InteractableFurniture
from src.game.sprites.interaction_target import InteractionTarget
from src.game.cutscenes.cutscene import Cutscene
from .summary import Summary

class Room(Scene):
    def __init__(self, game: Game, game_data: GameData | None, name: str) -> None:
        super().__init__(game)

        if game_data is not None:
            self.game_data = game_data
            self.player = game_data.player
            self.add(self.player)
            self.camera = game_data.camera
            self.add(self.camera)
            self.clipboard = game_data.clipboard
            self.mom_slider = game_data.mom_slider
            self.add(self.mom_slider)

        self.data = RoomData.get(name)
        self.furnitures: set[Furniture] = set()

        self.interaction_targets: set[InteractionTarget] = set()
        self.items: set[Item] = set()
        self.dusts: set[Dust] = set()
        self.boundary: list[VecLike] = []
        self.interactable_furniture: dict[str, type[Furniture]] = {}

        self.clipboard_visible = False
        self.flash_clipboard = False
        self.flash_clipboard_timer = LoopTimer(0.5)
        self.flash_clipboard_bright = True

        self.cutscene: Cutscene | None = None

    def load_furniture(self) -> None:
        for name, positions in self.data["positions"].items():
            for pos in positions:
                image = self.data["images"][name]
                hitbox = None
                if name in self.data["hitboxes"]:
                    hitbox = self.data["hitboxes"][name]
                if name in self.interactable_furniture:
                    _type = self.interactable_furniture[name]
                    furniture = _type(self, name, pos, image, hitbox)
                else:
                    furniture = Furniture(self, name, pos, image, hitbox)
                self.add_furniture(furniture)

    def update(self) -> None:
        if self.cutscene is not None:
            self.cutscene.update()

        self.sprite_manager.update()

        self.sprite_manager.d_groups[DGroup.ROOM].sort(self.objects_sort_key)

        if self.game.keydown == pygame.K_c and self.cutscene is None:
            if not self.clipboard_visible:
                self.clipboard.slide_in()
                self.clipboard_visible = True
            else:
                self.clipboard.slide_out()
                self.clipboard_visible = False

        if __debug__:
            if self.game.keydown == pygame.K_RETURN:
                summary = Summary(self.game, self.game_data)
                self.game.set_scene(summary)

        if self.game_data.scores["hamsters"] == self.game_data.max_scores["hamsters"]:
            self.clipboard.cross_out("hamsters")

        watch("cutscene", self.cutscene)

    def start_cutscene(self, cutscene: Cutscene) -> None:
        self.cutscene = cutscene
        cutscene.start()

    def find_furniture(self, name: str) -> Furniture:
        for furniture in self.furnitures:
            if furniture.name == name:
                return furniture
        raise ValueError(f"No furniture named {name}.")

    def find_all_furniture(self, name: str) -> list[Furniture]:
        return [furniture for furniture in self.furnitures if furniture.name == name]

    def objects_sort_key(self, item: tuple[int, Sprite]) -> float:
        sprite = item[1]
        if isinstance(sprite, Furniture):
            if sprite.hitbox is not None:
                return sprite.hitbox.topcenter.y
            else:
                return sprite.pos.y + sprite.image.height / 2
        else:
            return sprite.pos.y

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(COLOR1)

        screen.blit(self.data["background"], -self.camera.pos // 1)

        self.sprite_manager.draw(screen)

        if not self.clipboard_visible and self.cutscene is None:
            img = Image.get("clipboard_icon")
            pos = Vec(WIDTH - img.width - 4, 4)
            if self.flash_clipboard:
                if self.flash_clipboard_timer.done:
                    self.flash_clipboard_bright = not self.flash_clipboard_bright
                if self.flash_clipboard_bright:
                    screen.blit(outline(img, (255, 255, 255)), pos - (1, 1))
            screen.blit(img, pos)

    def set_interactable_furniture(self, d: dict[str, type[Furniture]]) -> None:
        self.interactable_furniture = d

    def set_boundary(self, boundary: list[VecLike]) -> None:
        self.boundary = boundary

    def contains_point(self, point: VecLike, margin: float = 0) -> bool:
        if not point_in_polygon(point, self.boundary):
            return False
        if margin > 0 and distance_to_polygon_edges(point, self.boundary) < margin:
            return False
        return True

    def add_item(self, item: Item) -> None:
        self.items.add(item)
        self.add(item)
        self.interaction_targets.add(item.interaction_target)

    def remove_item(self, item: Item) -> None:
        self.items.remove(item)
        self.remove(item)
        self.interaction_targets.remove(item.interaction_target)

    def add_dust(self, dust: Dust) -> None:
        self.dusts.add(dust)
        self.add(dust)

    def remove_dust(self, dust: Dust) -> None:
        self.dusts.remove(dust)
        self.remove(dust)

    def add_furniture(self, furniture: Furniture) -> None:
        self.furnitures.add(furniture)
        self.add(furniture)
        if isinstance(furniture, InteractableFurniture):
            self.interaction_targets.add(furniture.interaction_target)

    def remove_furniture(self, furniture: Furniture) -> None:
        self.furnitures.remove(furniture)
        self.remove(furniture)
        if isinstance(furniture, InteractableFurniture):
            self.interaction_targets.remove(furniture.interaction_target)
