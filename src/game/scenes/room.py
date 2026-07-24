from src.core import *

from src.game.sprites.player import Player
from src.game.sprites.item import Item
from src.game.sprites.dust import Dust
from src.game.sprites.furniture import Furniture, InteractableFurniture
from src.game.sprites.interaction_target import InteractionTarget

class Room(Scene):
    def __init__(self, game: Game, name: str) -> None:
        super().__init__(game)

        self.data = RoomData.get(name)
        self.furnitures: set[Furniture] = set()

        self.interaction_targets: set[InteractionTarget] = set()
        self.items: set[Item] = set()
        self.dusts: set[Dust] = set()
        self.boundary: list[VecLike] = []
        self.interactable_furniture: dict[str, type[Furniture]] = {}

        self.player = Player(self)
        self.add(self.player)

    def load_furniture(self) -> None:
        for name, positions in self.data["positions"].items():
            for pos in positions:
                image = self.data["images"][name]
                hitbox = None
                if name in self.data["hitboxes"]:
                    hitbox = self.data["hitboxes"][name]
                if name in self.interactable_furniture:
                    _type = self.interactable_furniture[name]
                    furniture = _type(self, pos, image, hitbox)
                else:
                    furniture = Furniture(self, pos, image, hitbox)
                self.add_furniture(furniture)

    def update(self) -> None:
        self.sprite_manager.update()

        self.sprite_manager.d_groups[DGroup.ROOM].sort(self.objects_sort_key)

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

        screen.blit(self.data["background"])

        self.sprite_manager.draw(screen)

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
