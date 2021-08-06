from snow.constants import TipType, WaterNinja, FireNinja, SnowNinja, URLConstants
from snow.events import event, TagPacket, allow_once, has_attribute, FrameworkPacket
import asyncio

from snow.managers.battleroom import BattleRoom
from loguru import logger


async def join_battle(p):
    p.ninja = FireNinja
    if p.element_id == 2:
        p.ninja = WaterNinja
    elif p.element_id == 4:
        p.ninja = SnowNinja

    if p.session_id not in p.server.battles:
        p.server.battles[p.session_id] = BattleRoom(p.server)

    await p.server.battles[p.session_id].add_penguin(p)
    while len(p.room.penguins) < 3:
        logger.info("Waiting for Ninjas to join the Battle")
        p.wait += 1
        if p.wait > 200:
            break
        await asyncio.sleep(1)

    p.server.penguins_by_id[p.id] = p
    p.server.penguins_by_username[p.username] = p

    p.room.object_manager.update_player_coordinates(p)
    await p.send_tag(
        "O_SPRITE", "10", "0:100380", "0", ""
    )  # 6740003 - craig valley bg / 0:6740006 - forest
    await p.send_tag(
        "O_SPRITE", "11", "0:1", "0", ""
    )  # 6740004 - foreground / 0:6740007
    await p.room.object_manager.send_map(p)
    await p.send_json(
        action="closeCjsnowRoomToRoom",
        targetWindow="cardjitsu_snowplayerselect.swf",
        type="immediateAction",
    )
    await p.send_tag("FX_PLAYSOUND", "0:1840002", 1, 1, 75, -1, 0, -1)


@event.on(FrameworkPacket("windowReady"))
async def handle_ready_window(p, windowId=None, **data):
    if windowId == "cardjitsu_snowtimer.swf":
        p.timer_ready = True
        if p.room.is_ready("timer_ready"):
            await p.room.object_manager.show_moveable_tiles()

            await p.room.round_manager.begin_timer()
            if p.tip_mode:
                await p.room.show_tip(TipType.MOVE.value)
    elif windowId == "cardjitsu_snowclose.swf":
        asyncio.create_task(join_battle(p))


@event.on(FrameworkPacket("windowManagerReady"))
@has_attribute("joined_world")
@allow_once
async def handle_window_manager_ready(p, **data):
    fire_cnt, water_cnt, snow_cnt = 0, 0, 0
    for card in p.cards.values():
        card_info = p.server.attributes["cards"][card.card_id]
        if card_info.power_id > 0:
            if card_info.element == "f":
                fire_cnt += card.quantity
            elif card_info.element == "w":
                water_cnt += card.quantity
            elif card_info.element == "s":
                snow_cnt += card.quantity

    await p.send_json(type="immediateAction", action="setWorldId", worldId=1)
    await p.send_json(
        type="immediateAction",
        action="setBaseAssetUrl",
        baseAssetUrl=p.media_url + URLConstants.base_assets.value,
    )
    await p.send_json(
        type="immediateAction",
        action="setFontPath",
        defaultFontPath=p.media_url + URLConstants.base_fonts.value,
    )
    await p.send_json(
        type="playAction",
        action="skinRoomToRoom",
        url=p.media_url + URLConstants.loading_screen.value,
        className="",
        variant=0,
    )
    await p.send_json(
        action="loadWindow",
        assetPath="",
        initializationPayload=[None],
        layerName="bottomLayer",
        loadDescription="",
        type="playAction",
        windowUrl=p.media_url + URLConstants.error_handler.value,
        xPercent=0,
        yPercent=0,
    )
    await p.send_json(
        action="loadWindow",
        assetPath="",
        initializationPayload={
            "game": "snow",
            "name": p.safe_name,
            "powerCardsFire": fire_cnt,
            "powerCardsWater": water_cnt,
            "powerCardsSnow": snow_cnt,
        },
        layerName="topLayer",
        loadDescription="",
        type="playAction",
        windowUrl=p.media_url + URLConstants.player_selection.value,
        xPercent=0,
        yPercent=0,
    )


@event.on(FrameworkPacket("quit"))
async def handle_quit(p, **data):
    await p.send_json(
        action="loadWindow",
        assetPath="",
        initializationPayload=[None],
        layerName="toolLayer",
        loadDescription="",
        type="playAction",
        windowUrl=p.media_url + URLConstants.external_interface.value,
        xPercent=0,
        yPercent=0,
    )
    if p.room is not None:
        await p.room.player_manager.player_death(p)
