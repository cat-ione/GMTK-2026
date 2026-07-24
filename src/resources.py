from src.core.util.resource import Image, Spritesheet, Sound, Font, RoomData

def define_resources() -> None:
    Spritesheet("player_idle_back", "player/idle_back.png", 2)
    Spritesheet("player_idle_front", "player/idle_front.png", 2)
    Spritesheet("player_idle_side", "player/idle_side.png", 2)
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

    Spritesheet("surprise", "surprise.png", 8)

    RoomData("living_room", "living_room.json")
    RoomData("bedroom", "bedroom.json")
    RoomData("bathroom", "bathroom.json")

    Spritesheet("title_text_scroll", "text_scroll.png", 15)
    Image("button_large", "button_large.png")
    Image("button_medium", "button_medium.png")
    Image("button_small", "button_small.png")
    Image("titlescreen_bg", "titlescreen_bg.png")
