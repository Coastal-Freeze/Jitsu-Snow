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
    Hitpoints = 30
    Range = 2
    Attack = 8
    Move = 2
    Element = 'fire'
    AttackAnimation = ''
    MoveAnimation = '0:100341'
    MoveAnimationDuration = 600
    MoveAnimationSound = '0:1840016'
    SpecialAnimation = ''
    IdleAnimation = '0:100340'
    IdleAnimationDuration = 800
    SelectedTileAnimation = '0:30070'


class WaterNinja(enum.Enum):
    Hitpoints = 38
    Range = 1
    Attack = 10
    Move = 2
    Element = 'water'
    AttackAnimation = ''
    MoveAnimation = '0:100323'
    MoveAnimationDuration = 700
    MoveAnimationSound = '0:1840017'
    SpecialAnimation = ''
    IdleAnimation = '0:100322'
    IdleAnimationDuration = 700
    SelectedTileAnimation = '0:30044'


class SnowNinja(enum.Enum):
    Hitpoints = 28
    Range = 3
    Attack = 6
    Move = 3
    Element = 'snow'
    AttackAnimation = '0:100362'
    AttackAnimationDuration = 1330
    AttackAnimationSound = '0:1840020'
    MoveAnimation = '0:100367'
    MoveAnimationDuration = 670
    MoveAnimationSound = '0:1840017'
    SpecialAnimation = ''
    IdleAnimation = '0:100361'
    IdleAnimationDuration = 1100
    SelectedTileAnimation = '0:100018'


##########################

class EnemySly(enum.Enum):
    Name = 'Sly'
    Hitpoints = 30
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


class EnemyTank(enum.Enum):
    Name = 'Tank'
    Hitpoints = 60
    Design = 81
    Range = 1
    Attack = 10
    Move = 1
    AttackAnimation = ''
    MoveAnimation = '0:100303'
    MoveAnimationDuration = 1100
    MoveAnimationSound = '0:1840013'
    IdleAnimation = '0:100297'
    IdleAnimationDuration = 1100


class EnemyScrap(enum.Enum):
    Name = 'Scrap'
    Hitpoints = 45
    Design = 82
    Range = 2
    Attack = 5
    Move = 2
    AttackAnimation = ''
    MoveAnimation = '0:100319'
    MoveAnimationDuration = 1200
    MoveAnimationSound = '0:1840015'
    IdleAnimation = '0:100311'
    IdleAnimationDuration = 1675  # NOT SURE


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


import enum


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
    ExternalInterface = 'minigames/cjsnow/en_US/deploy/swf/ui/windows' \
                        '/cardjitsu_snowexternalinterfaceconnector.swf '
    LoadingScreen = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/../assets/cjsnow_loadingscreenassets.swf'
    PlayerSelection = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowplayerselect.swf'
    SnowTimer = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowtimer.swf'
    SnowUI = 'minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowui.swf'
    WindowManager = 'minigames/cjsnow/en_US/deploy/swf/windowManager/windowmanager.swf'
