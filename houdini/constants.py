import enum


class StatusField(enum.IntEnum):
    OpenedIglooViewer = 1
    ActiveIglooLayoutOpenFlag = 2
    PuffleTreasureInfographic = 512
    PlayerOptInAbTestDayZero = 1024
    PlayerSwapPuffle = 2048
    MoreThanTenPufflesBackyardMessage = 4096
    VisitBackyardFirstTime = 8192
    HasWalkedPuffleFirstTime = 65536
    HasWalkedPuffleSecondTime = 131072


class ConflictResolution(enum.Enum):
    Silent = 0
    Append = 1
    Exception = 2


class Language(enum.IntEnum):
    En = 1
    Pt = 2
    Fr = 4
    Es = 8
    De = 32
    Ru = 64


class ClientType(enum.Enum):
    Legacy = 'legacy'
    Vanilla = 'vanilla'


##########################

class BonusRoundType(enum.Enum):
    NO_NINJAS_DOWN = 'no_ko'
    BEAT_THE_CLOCK = 'under_time'
    FULL_HEALTH = 'full_health'


class TipType(enum.Enum):
    MOVE = 'Move'
    ATTACK = 'Attack'
    POWER_CARD = 'Card'
    HEAL = 'Heal'
    TIMER = 'Confirm'
    BONUS_REVIVE = 'MemberCard'


##########################

# 100018, 30044, 30070

class FireNinja(enum.Enum):
    HealthPoints = 30
    Multiplier = 2
    Range = 2
    Attack = 8
    Move = 2
    Element = 'fire'
    CardElement = 'f'
    AttackAnimation = '0:100343'
    AttackAnimationDuration = 2100
    AttackAnimationSound = '0:1840026'
    MoveAnimation = '0:100341'
    MoveAnimationDuration = 600
    MoveAnimationSound = '0:1840016'
    SpecialAnimation = ''
    HitAnimation = '0:100342'
    HitAnimationDuration = 1200
    HitAnimationSound = '0:1840008'
    IdleAnimation = '0:100340'
    IdleAnimationDuration = 800
    SelectedTileAnimation = '0:30070'
    KnockoutAnimation = '0:100356'
    KnockoutAnimationLoop = '0:100357'


class WaterNinja(enum.Enum):
    HealthPoints = 38
    Multiplier = 1.56
    Range = 1
    Attack = 10
    Move = 2
    Element = 'water'
    CardElement = 'w'
    AttackAnimation = '0:100321'
    AttackAnimationDuration = 1330
    AttackAnimationSound = '0:1840018'
    MoveAnimation = '0:100323'
    MoveAnimationDuration = 700
    MoveAnimationSound = '0:1840017'
    SpecialAnimation = ''
    HitAnimation = '0:100324'
    HitAnimationDuration = 870
    HitAnimationSound = '0:1840008'
    IdleAnimation = '0:100322'
    IdleAnimationDuration = 700
    SelectedTileAnimation = '0:30044'
    KnockoutAnimation = '0:100325'
    KnockoutAnimationLoop = '0:100326'
    ReviveAnimation = '0:100332'



class SnowNinja(enum.Enum):
    HealthPoints = 28
    Multiplier = 2.15
    Range = 3
    Attack = 6
    Move = 3
    Element = 'snow'
    CardElement = 's'
    AttackAnimation = '0:100362'
    AttackAnimationDuration = 1330
    AttackAnimationSound = '0:1840020'
    MoveAnimation = '0:100367'
    MoveAnimationDuration = 670
    MoveAnimationSound = '0:1840017'
    SpecialAnimation = ''
    HitAnimation = '0:100364'
    HitAnimationDuration = 870
    HitAnimationSound = '0:1840008'
    IdleAnimation = '0:100361'
    IdleAnimationDuration = 1100
    SelectedTileAnimation = '0:100018'
    KnockoutAnimation = '0:100365'
    KnockoutAnimationLoop = '0:100366'
    HealAnimation = '0:100363'
    HealAnimationDuration = 1200


##########################

class EnemySly(enum.Enum):
    Name = 'Sly'
    Multiplier = 2
    HealthPoints = 30
    Design = 80
    Range = 3
    Attack = 4
    Move = 3
    AttackAnimation = '0:100306'
    AttackAnimationDuration = 3350
    AttackAnimationSound = '0:1840021'
    MoveAnimation = '0:100307'
    MoveAnimationDuration = 1200
    MoveAnimationSound = '0:1840014'
    IdleAnimation = '0:100305'
    IdleAnimationDuration = 1675
    HitAnimation = '0:100308'
    HitAnimationDuration = 1200
    HitAnimationSound = '0:1840004'
    KnockoutAnimation = '0:100309'


class EnemyTank(enum.Enum):
    Name = 'Tank'
    HealthPoints = 60
    Multiplier = 1
    Design = 81
    Range = 1
    Attack = 10
    Move = 1
    AttackAnimation = '0:100299'
    AttackAnimationDuration = 3350
    AttackAnimationSound = '0:1840021'
    MoveAnimation = '0:100303'
    MoveAnimationDuration = 1100
    MoveAnimationSound = '0:1840013'
    IdleAnimation = '0:100297'
    IdleAnimationDuration = 1100
    HitAnimation = '0:100302'
    HitAnimationDuration = 1200
    HitAnimationSound = '0:1840003'
    KnockoutAnimation = '0:100309'
    


class EnemyScrap(enum.Enum):
    Name = 'Scrap'
    HealthPoints = 45
    Multiplier = 1.33
    Design = 82
    Range = 2
    Attack = 5
    Move = 2
    AttackAnimation = '0:100312'
    AttackAnimationDuration = 3350
    AttackAnimationSound = '0:1840021'
    MoveAnimation = '0:100319'
    MoveAnimationDuration = 1200
    MoveAnimationSound = '0:1840015'
    IdleAnimation = '0:100311'
    IdleAnimationDuration = 1675  # NOT SURE
    HitAnimation = '0:100318'
    HitAnimationDuration = 1200
    HitAnimationSound = '0:1840005'
    KnockoutAnimation = '0:100309'
    


##########################

class EmptyTile(enum.Enum):
    TileUrl = 0
    TileName = 'Empty Tile'
    TileCollection = '0:7940012'
    SpriteIndex = '0:2'


class OpenTile(enum.Enum):
    TileUrl = 1
    TileName = 'open'
    TileCollection = '0:7940013'
    SpriteIndex = '0:2'


class EnemyTile(enum.Enum):
    TileUrl = 2
    TileName = 'enemy'
    TileCollection = '0:7940014'
    SpriteIndex = '0:3'


class PenguinTile(enum.Enum):
    TileUrl = 3
    TileName = 'penguin'
    TileCollection = '0:7940015'
    SpriteIndex = '0:4'


class OccupiedPenguinSpawnTile(enum.Enum):
    TileUrl = 4
    TileName = 'penguin_spawn_occupied'
    TileCollection = '0:7940016'
    SpriteIndex = '0:100002'


class UnoccupiedPenguinSpawnTile(enum.Enum):
    TileUrl = 5
    TileName = 'penguin_spawn_unoccupied'
    TileCollection = '0:7940017'
    SpriteIndex = '0:6'


class UnoccupiedEnemySpawnTile(enum.Enum):
    TileUrl = 7
    TileName = 'enemy_spawn_unoccupied'
    TileCollection = '0:7940018'
    SpriteIndex = '0:10003'


class OccupiedEnemySpawnTile(enum.Enum):
    TileUrl = 8
    TileName = 'enemy_spawn_occupied'
    TileCollection = '0:7940019'
    SpriteIndex = '0:10004'


class MapConstants(enum.Enum):
    BoardHeight = 5
    BoardWidth = 9

    PlayerObjectIds = (12, 13, 4)


class MovementTile(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30020'
    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 0.9998
    YCoordinateDecimals = 4


class EnemyObject(enum.Enum):
    ArtIndex = '0:1'  # TODO: CHANGE
    TemplateId = '0:30010'  # or 30040? or 30010?
    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 1
    YCoordinateDecimals = 0


class PenguinObject(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30040'
    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 1
    YCoordinateDecimals = 0


class HPObject(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30040'
    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 1.0004
    YCoordinateDecimals = 4


class ObstacleObject(enum.Enum):
    ArtIndex = '0:100394'  # Regular Mountain Rock
    TemplateId = '0:100145'
    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 1
    YCoordinateDecimals = 0

    DefaultLocations = ((2, 0), (6, 0), (2, 4), (6, 4))

class PenguinTarget(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30033'
    SpriteAnimation = '0:100044'
    SpriteDuration = 402
    Sound = '0:1840039'

    SpriteLoopAnimation = '0:100045'
    SpriteLoopDuration = 4020

    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 1.01
    YCoordinateDecimals = 2


class SelectedPenguinTarget(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30033'
    SpriteAnimation = '0:100046'
    SpriteDuration = 402
    Sound = '0:1840038'

    SpriteLoopAnimation = '0:100047'
    SpriteLoopDuration = 4020

class EnemyTarget(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30033'
    SpriteAnimation = '0:100040'
    SpriteDuration = 402
    Sound = '0:1840039'

    SpriteLoopAnimation = '0:100041'
    SpriteLoopDuration = 4020

    XCoordinateOffset = 0.5
    XCoordinateDecimals = 1
    YCoordinateOffset = 1.01
    YCoordinateDecimals = 2


class SelectedEnemyTarget(enum.Enum):
    ArtIndex = '0:1'
    TemplateId = '0:30033'
    SpriteAnimation = '0:100042'
    SpriteDuration = 402
    Sound = '0:1840038'

    SpriteLoopAnimation = '0:100043'
    SpriteLoopDuration = 4020


class ObstacleTile(enum.Enum):
    TileUrl = 9
    TileName = 'obstacle'
    TileCollection = '0:7940020'
    SpriteIndex = '0:10005'


#################

class RoundState(enum.IntEnum):
    NEW_ROUND = 0
    NINJA_TURN = 1
    ENEMY_TURN = 2


class URLConstants(enum.Enum):
    BaseAssets = ''
    BaseFonts = 'fonts/'

    CloseWindow = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowclose.swf'
    ErrorHandler = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowerrorhandler.swf'
    ExternalInterface = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowexternalinterfaceconnector.swf'
    LoadingScreen = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/../assets/cjsnow_loadingscreenassets.swf'
    PlayerSelection = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowplayerselect.swf'
    SnowTimer = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf'
    SnowUI = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowui.swf'
    WindowManager = 'minigames/cjsnow/en_US/deploy/swf/windowManager/windowmanager.swf'
    
    
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

