from src.core.util.resource import Image, Spritesheet, Sound, Font, RoomData

def define_resources() -> None:
    Spritesheet("player_walk_back", "player/walk_back.png", 4)
    Spritesheet("player_walk_front", "player/walk_front.png", 4)
    Spritesheet("player_walk_side", "player/walk_side.png", 4)
    Spritesheet("player_walk_hold_front", "player/walk_hold_front.png", 4)
    Spritesheet("player_walk_hold_back", "player/walk_hold_back.png", 4)
    Spritesheet("player_walk_hold_side", "player/walk_hold_side.png", 4)

    Image("test_item", "items/test_item.png")
    Image("vacuum_world", "items/vacuum_world.png")
    Image("vacuum_front", "items/vacuum_front.png")
    Image("vacuum_side", "items/vacuum_side.png")
    Image("plate", "items/plate.png")
    Image("stack_of_plates_5", "rooms/living_room/stack_of_plates_5.png")
    Image("stack_of_plates_4", "rooms/living_room/stack_of_plates_4.png")
    Image("stack_of_plates_3", "rooms/living_room/stack_of_plates_3.png")
    Image("stack_of_plates_2", "rooms/living_room/stack_of_plates_2.png")
    Image("stack_of_plates_1", "rooms/living_room/stack_of_plates_1.png")

    RoomData("living_room", "living_room.json")
    RoomData("entrance", "entrance.json")
    RoomData("bedroom", "bedroom.json")
