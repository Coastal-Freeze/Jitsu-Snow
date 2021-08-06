from snow.constants import URLConstants
from snow.data.ninja import PenguinCardCollection
from snow.events import event, TagPacket, allow_once, has_attribute
import ujson
from loguru import logger

from snow.data.penguin import Penguin


@event.on(TagPacket("/place_ready"))
@has_attribute("joined_world")
@allow_once
async def handle_screen_ready(p):
    await p.send_tag("O_HERE", 4, "0:1", 5, 2.5, 0, 1, 0, 0, 0, "", "0:1", 0, 1, 0)
    await p.send_tag("O_PLAYER", 4, "")
    await p.send_tag("P_CAMERA", 4.48438, 2.48438, 0, 0, 1)
    await p.send_tag("P_ZOOM", "1.000000")
    await p.send_tag("P_LOCKZOOM", 1)
    await p.send_tag("P_LOCKCAMERA", 1)

    p.place_ready = True


@event.on(TagPacket("/ready"))
@has_attribute("joined_world")
@allow_once
async def handle_penguin_ready(p):
    # [W_INPUT]|use|4375706:1|2|3|0|use|
    await p.send_tag("W_INPUT", "use", "4375706:1", 2, 3, 0, "use")
    # input id | script id | mouse target | key mouse type | key modifier | command

    for sprite in p.server.default_sprites:
        await p.send_tag("S_LOADSPRITE", f"0:{sprite}")

    await p.send_tag(
        "UI_CROSSWORLDSWFREF",
        101,
        0,
        "WindowManagerSwf",
        0,
        0,
        0,
        0,
        0,
        p.media_url + URLConstants.window_manager.value,
        "#",
    )
    await p.send_tag("UI_ALIGN", 101, 0, 0, "center", "scale_none")

    await p.send_tag("W_PLACE", "0:0", 1, 0)
    # tile
    await p.send_tag(
        "P_MAPBLOCK",
        "t",
        1,
        1,
        "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=",
    )
    # height
    await p.send_tag(
        "P_MAPBLOCK",
        "h",
        1,
        1,
        "iVBORw0KGgoAAAANSUhEUgAAAAkAAAAFCAAAAACyOJm3AAAADklEQVQImWNghgEGIlkADWEAiDEh28IAAAAASUVORK5CYII=",
    )
    await p.send_tag("P_ZOOMLIMIT", "-1.000000", "-1.000000")
    await p.send_tag("P_RENDERFLAGS", 0, 48)
    await p.send_tag("P_SIZE", 9, 5)
    await p.send_tag("P_VIEW", 5)
    await p.send_tag("P_START", 5, 2.5, 0)
    await p.send_tag("P_LOCKVIEW", 0)
    await p.send_tag("P_TILESIZE", 100)
    await p.send_tag("P_ELEVSCALE", "0.031250")
    await p.send_tag("P_RELIEF", 1)
    await p.send_tag("P_LOCKSCROLL", 1, 0, 0, 0)
    await p.send_tag("P_HEIGHTMAPSCALE", 0.5, 0)
    await p.send_tag("P_HEIGHTMAPDIVISIONS", 1)
    await p.send_tag(
        "P_CAMERA3D",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        0,
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "0.000000",
        "864397819904.000000",
        "0.000000",
        0,
        0,
    )
    await p.send_tag("UI_BGCOLOR", 34, 164, 243)
    await p.send_tag("P_DRAG", 0)
    await p.send_tag("P_CAMLIMITS", 0, 0, 0, 0)
    await p.send_tag("P_LOCKRENDERSIZE", 0, 1024, 768)
    await p.send_tag("P_LOCKOBJECTS", 0)
    await p.send_tag("UI_BGSPRITE", "-1:-1", 0, "0.000000", "0.000000")

    await p.send_tag(
        "P_TILE", 0, "", 0, 0, 1, "0:2", "Empty Tile", 0, 0, 0, "0:7940006"
    )
    await p.send_tag("P_TILE", 1, "", 0, 0, 1, "0:2", "blankblue", 0, 0, 0, "0:7940007")
    await p.send_tag(
        "P_TILE", 2, "", 0, 0, 1, "0:3", "blankgreen", 0, 0, 0, "0:7940008"
    )
    await p.send_tag("P_TILE", 3, "", 0, 0, 1, "0:4", "blankgrey", 0, 0, 0, "0:7940009")
    await p.send_tag(
        "P_TILE", 4, "", 0, 0, 1, "0:5", "blankpurpl", 0, 0, 0, "0:7940010"
    )
    await p.send_tag(
        "P_TILE", 5, "", 0, 0, 1, "0:6", "blankwhite", 0, 0, 0, "0:7940011"
    )

    await p.send_tag("P_PHYSICS", 0, 0, 0, 0, 0, 0, 0, 1)
    await p.send_tag("P_ASSETSCOMPLETE", p.id)
