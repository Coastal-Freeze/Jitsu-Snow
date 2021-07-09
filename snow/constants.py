import enum


class Language(enum.IntEnum):
    En = 1
    Pt = 2
    Fr = 4
    Es = 8
    De = 32
    Ru = 64


##########################

class BonusRoundType(enum.Enum):
    NO_NINJAS_DOWN = 'no_ko'
    BEAT_THE_CLOCK = 'under_time'
    FULL_HEALTH = 'full_health'


class TipType(enum.Enum):
    move = 'Move'
    attack = 'attack'
    POWER_CARD = 'Card'
    HEAL = 'Heal'
    TIMER = 'Confirm'
    BONUS_REVIVE = 'MemberCard'


##########################

# 100018, 30044, 30070

class FireNinja(enum.Enum):
    health_points = 30
    multiplier = 2
    range = 2
    attack = 8
    move = 2
    element = 'fire'
    card_element = 'f'
    attack_animation = '0:100343'
    attack_animation_duration = 2100
    attack_animation_sound = '0:1840026'
    move_animation = '0:100341'
    move_animation_duration = 600
    move_animation_sound = '0:1840016'
    special_animation = ''
    hit_animation = '0:100342'
    hit_animation_duration = 1200
    hit_animation_sound = '0:1840008'
    idle_animation = '0:100340'
    idle_animation_duration = 800
    selected_tile_animation = '0:30070'
    knockout_animation = '0:100356'
    knockout_animation_loop = '0:100357'


class WaterNinja(enum.Enum):
    health_points = 38
    multiplier = 1.56
    range = 1
    attack = 10
    move = 2
    element = 'water'
    card_element = 'w'
    attack_animation = '0:100321'
    attack_animation_duration = 1330
    attack_animation_sound = '0:1840018'
    move_animation = '0:100323'
    move_animation_duration = 700
    move_animation_sound = '0:1840017'
    special_animation = ''
    hit_animation = '0:100324'
    hit_animation_duration = 870
    hit_animation_sound = '0:1840008'
    idle_animation = '0:100322'
    idle_animation_duration = 700
    selected_tile_animation = '0:30044'
    knockout_animation = '0:100325'
    knockout_animation_loop = '0:100326'
    revive_animation = '0:100332'


class SnowNinja(enum.Enum):
    health_points = 28
    multiplier = 2.15
    range = 3
    attack = 6
    move = 3
    element = 'snow'
    card_element = 's'
    attack_animation = '0:100362'
    attack_animation_duration = 1330
    attack_animation_sound = '0:1840020'
    move_animation = '0:100367'
    move_animation_duration = 670
    move_animation_sound = '0:1840017'
    special_animation = ''
    hit_animation = '0:100364'
    hit_animation_duration = 870
    hit_animation_sound = '0:1840008'
    idle_animation = '0:100361'
    idle_animation_duration = 1100
    selected_tile_animation = '0:100018'
    knockout_animation = '0:100365'
    knockout_animation_loop = '0:100366'
    heal_animation = '0:100363'
    heal_animation_duration = 1200


##########################

class EnemySly(enum.Enum):
    name = 'Sly'
    multiplier = 2
    health_points = 30
    design = 80
    range = 3
    attack = 4
    move = 3
    attack_animation = '0:100306'
    attack_animation_duration = 3350
    attack_animation_sound = '0:1840021'
    move_animation = '0:100307'
    move_animation_duration = 1200
    move_animation_sound = '0:1840014'
    idle_animation = '0:100305'
    idle_animation_duration = 1675
    hit_animation = '0:100308'
    hit_animation_duration = 1200
    hit_animation_sound = '0:1840004'
    knockout_animation = '0:100309'


class EnemyTank(enum.Enum):
    name = 'Tank'
    health_points = 60
    multiplier = 1
    design = 81
    range = 1
    attack = 10
    move = 1
    attack_animation = '0:100299'
    attack_animation_duration = 3350
    attack_animation_sound = '0:1840021'
    move_animation = '0:100303'
    move_animation_duration = 1100
    move_animation_sound = '0:1840013'
    idle_animation = '0:100297'
    idle_animation_duration = 1100
    hit_animation = '0:100302'
    hit_animation_duration = 1200
    hit_animation_sound = '0:1840003'
    knockout_animation = '0:100304'


class EnemyScrap(enum.Enum):
    name = 'Scrap'
    health_points = 45
    multiplier = 1.33
    design = 82
    range = 2
    attack = 5
    move = 2
    attack_animation = '0:100312'
    attack_animation_duration = 3350
    attack_animation_sound = '0:1840021'
    move_animation = '0:100319'
    move_animation_duration = 1200
    move_animation_sound = '0:1840015'
    idle_animation = '0:100311'
    idle_animation_duration = 1675  # NOT SURE
    hit_animation = '0:100318'
    hit_animation_duration = 1200
    hit_animation_sound = '0:1840005'
    knockout_animation = '0:100320'


##########################

class EmptyTile(enum.Enum):
    tile_url = 0
    tile_name = 'Empty Tile'
    tile_collection = '0:7940012'
    sprite_index = '0:2'


class OpenTile(enum.Enum):
    tile_url = 1
    tile_name = 'open'
    tile_collection = '0:7940013'
    sprite_index = '0:2'


class EnemyTile(enum.Enum):
    tile_url = 2
    tile_name = 'enemy'
    tile_collection = '0:7940014'
    sprite_index = '0:3'


class PenguinTile(enum.Enum):
    tile_url = 3
    tile_name = 'penguin'
    tile_collection = '0:7940015'
    sprite_index = '0:4'


class OccupiedPenguinSpawnTile(enum.Enum):
    tile_url = 4
    tile_name = 'penguin_spawn_occupied'
    tile_collection = '0:7940016'
    sprite_index = '0:100002'


class UnoccupiedPenguinSpawnTile(enum.Enum):
    tile_url = 5
    tile_name = 'penguin_spawn_unoccupied'
    tile_collection = '0:7940017'
    sprite_index = '0:6'


class UnoccupiedEnemySpawnTile(enum.Enum):
    tile_url = 7
    tile_name = 'enemy_spawn_unoccupied'
    tile_collection = '0:7940018'
    sprite_index = '0:10003'


class OccupiedEnemySpawnTile(enum.Enum):
    tile_url = 8
    tile_name = 'enemy_spawn_occupied'
    tile_collection = '0:7940019'
    sprite_index = '0:10004'


class MapConstants(enum.Enum):
    board_height = 5
    board_width = 9

    player_object_ids = (12, 13, 4)


class MovementTile(enum.Enum):
    art_index = '0:1'
    template_id = '0:30020'
    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 0.9998
    y_coordinate_decimals = 4


class EnemyObject(enum.Enum):
    art_index = '0:1'  # TODO: CHANGE
    template_id = '0:30010'  # or 30040? or 30010?
    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 1
    y_coordinate_decimals = 0


class PenguinObject(enum.Enum):
    art_index = '0:1'
    template_id = '0:30040'
    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 1
    y_coordinate_decimals = 0


class HPObject(enum.Enum):
    art_index = '0:1'
    template_id = '0:30040'
    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 1.0004
    y_coordinate_decimals = 4


class ObstacleObject(enum.Enum):
    art_index = '0:100394'  # Regular Mountain Rock
    template_id = '0:100145'
    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 1
    y_coordinate_decimals = 0

    default_locations = ((2, 0), (6, 0), (2, 4), (6, 4))


class PenguinTarget(enum.Enum):
    art_index = '0:1'
    template_id = '0:30033'
    sprite_animation = '0:100044'
    sprite_duration = 402
    sound = '0:1840039'

    sprite_loop_animation = '0:100045'
    sprite_loop_duration = 4020

    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 1.01
    y_coordinate_decimals = 2


class SelectedPenguinTarget(enum.Enum):
    art_index = '0:1'
    template_id = '0:30033'
    sprite_animation = '0:100046'
    sprite_duration = 402
    sound = '0:1840038'

    sprite_loop_animation = '0:100047'
    sprite_loop_duration = 4020


class EnemyTarget(enum.Enum):
    art_index = '0:1'
    template_id = '0:30033'
    sprite_animation = '0:100040'
    sprite_duration = 402
    sound = '0:1840039'

    sprite_loop_animation = '0:100041'
    sprite_loop_duration = 4020

    x_coordinate_offset = 0.5
    x_coordinate_decimals = 1
    y_coordinate_offset = 1.01
    y_coordinate_decimals = 2


class SelectedEnemyTarget(enum.Enum):
    art_index = '0:1'
    template_id = '0:30033'
    sprite_animation = '0:100042'
    sprite_duration = 402
    sound = '0:1840038'

    sprite_loop_animation = '0:100043'
    sprite_loop_duration = 4020


class ObstacleTile(enum.Enum):
    tile_url = 9
    tile_name = 'obstacle'
    tile_collection = '0:7940020'
    sprite_index = '0:10005'


#################

class RoundState(enum.IntEnum):
    NEW_ROUND = 0
    NINJA_TURN = 1
    ENEMY_TURN = 2


class URLConstants(enum.Enum):
    base_assets = ''
    base_fonts = 'fonts/'

    close_window = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowclose.swf'
    error_handler = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowerror_handler.swf'
    external_interface = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowexternal_interfaceconnector.swf'
    loading_screen = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/../assets/cjsnow_loading_screenassets.swf'
    player_selection = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowplayerselect.swf'
    snow_timer = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf'
    snow_ui = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowui.swf'
    window_manager = 'minigames/cjsnow/en_US/deploy/swf/windowManager/windowmanager.swf'


CJ_SNOW_STAMPS = [{
    "description": "global_content.stamps.478.description",
    "is_member": False,
    "name": "global_content.stamps.478.name",
    "rank": 2,
    "rank_token": "global_content.stamps.478.rank_token",
    "stamp_id": 478
}, {
    "description": "global_content.stamps.479.description",
    "is_member": False,
    "name": "global_content.stamps.479.name",
    "rank": 2,
    "rank_token": "global_content.stamps.479.rank_token",
    "stamp_id": 479
}, {
    "description": "global_content.stamps.480.description",
    "is_member": False,
    "name": "global_content.stamps.480.name",
    "rank": 3,
    "rank_token": "global_content.stamps.480.rank_token",
    "stamp_id": 480
}, {
    "description": "global_content.stamps.481.description",
    "is_member": False,
    "name": "global_content.stamps.481.name",
    "rank": 2,
    "rank_token": "global_content.stamps.481.rank_token",
    "stamp_id": 481
}, {
    "description": "global_content.stamps.482.description",
    "is_member": False,
    "name": "global_content.stamps.482.name",
    "rank": 3,
    "rank_token": "global_content.stamps.482.rank_token",
    "stamp_id": 482
}, {
    "description": "global_content.stamps.483.description",
    "is_member": False,
    "name": "global_content.stamps.483.name",
    "rank": 3,
    "rank_token": "global_content.stamps.483.rank_token",
    "stamp_id": 483
}, {
    "description": "global_content.stamps.484.description",
    "is_member": False,
    "name": "global_content.stamps.484.name",
    "rank": 2,
    "rank_token": "global_content.stamps.484.rank_token",
    "stamp_id": 484
}, {
    "description": "global_content.stamps.485.description",
    "is_member": False,
    "name": "global_content.stamps.485.name",
    "rank": 3,
    "rank_token": "global_content.stamps.485.rank_token",
    "stamp_id": 485
}, {
    "description": "global_content.stamps.486.description",
    "is_member": False,
    "name": "global_content.stamps.486.name",
    "rank": 4,
    "rank_token": "global_content.stamps.486.rank_token",
    "stamp_id": 486
}, {
    "description": "global_content.stamps.477.description",
    "is_member": False,
    "name": "global_content.stamps.477.name",
    "rank": 3,
    "rank_token": "global_content.stamps.477.rank_token",
    "stamp_id": 477
}, {
    "description": "global_content.stamps.476.description",
    "is_member": False,
    "name": "global_content.stamps.476.name",
    "rank": 3,
    "rank_token": "global_content.stamps.476.rank_token",
    "stamp_id": 476
}, {
    "description": "global_content.stamps.475.description",
    "is_member": False,
    "name": "global_content.stamps.475.name",
    "rank": 2,
    "rank_token": "global_content.stamps.475.rank_token",
    "stamp_id": 475
}, {
    "description": "global_content.stamps.467.description",
    "is_member": False,
    "name": "global_content.stamps.467.name",
    "rank": 2,
    "rank_token": "global_content.stamps.467.rank_token",
    "stamp_id": 467
}, {
    "description": "global_content.stamps.468.description",
    "is_member": False,
    "name": "global_content.stamps.468.name",
    "rank": 3,
    "rank_token": "global_content.stamps.468.rank_token",
    "stamp_id": 468
}, {
    "description": "global_content.stamps.469.description",
    "is_member": False,
    "name": "global_content.stamps.469.name",
    "rank": 1,
    "rank_token": "global_content.stamps.469.rank_token",
    "stamp_id": 469
}, {
    "description": "global_content.stamps.470.description",
    "is_member": False,
    "name": "global_content.stamps.470.name",
    "rank": 1,
    "rank_token": "global_content.stamps.470.rank_token",
    "stamp_id": 470
}, {
    "description": "global_content.stamps.471.description",
    "is_member": False,
    "name": "global_content.stamps.471.name",
    "rank": 1,
    "rank_token": "global_content.stamps.471.rank_token",
    "stamp_id": 471
}, {
    "description": "global_content.stamps.472.description",
    "is_member": False,
    "name": "global_content.stamps.472.name",
    "rank": 4,
    "rank_token": "global_content.stamps.472.rank_token",
    "stamp_id": 472
}, {
    "description": "global_content.stamps.473.description",
    "is_member": False,
    "name": "global_content.stamps.473.name",
    "rank": 4,
    "rank_token": "global_content.stamps.473.rank_token",
    "stamp_id": 473
}, {
    "description": "global_content.stamps.474.description",
    "is_member": False,
    "name": "global_content.stamps.474.name",
    "rank": 1,
    "rank_token": "global_content.stamps.474.rank_token",
    "stamp_id": 474
}, {
    "description": "global_content.stamps.487.description",
    "is_member": False,
    "name": "global_content.stamps.487.name",
    "rank": 2,
    "rank_token": "global_content.stamps.487.rank_token",
    "stamp_id": 487
}
]
