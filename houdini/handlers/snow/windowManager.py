from houdini import handlers
from houdini.constants import FireNinja, WaterNinja, SnowNinja, URLConstants, TipType
from houdini.handlers import FrameworkPacket, TagPacket
from houdini.handlers.snow.battle import SnowBattle
import asyncio

async def join_battle(p):
    tr = p.server.redis.multi_exec()
    tr.get(f'{p.world_name}.{p.id}')
    tr.get(f'{p.world_name}.{p.id}.element')
    tr.delete(f'{p.world_name}.{p.id}', f'{p.world_name}.{p.id}.element')
    match_id, element, _ = await tr.execute()

    if match_id is None or element is None:
        return await p.close()

    match_id, element = int(match_id), int(element)

    p.snow_ninja.ninja = FireNinja
    if element == 2:
        p.snow_ninja.ninja = WaterNinja
    elif element == 4:
        p.snow_ninja.ninja = SnowNinja

    if match_id not in p.server.battles:
        p.server.battles[match_id] = SnowBattle(p.server)

    await p.server.battles[match_id].add_penguin(p)
    while len(p.room.penguins) < 3:
        p.logger.info('Waiting for Ninjas to join the Battle')
        p.snow_ninja.wait += 1
        if p.snow_ninja.wait > 200:
            break
        await asyncio.sleep(1)
    p.room.object_manager.update_player_coordinates(p)
    await p.send_tag('O_SPRITE', '10', '0:100380', '0', '')  # 6740003 - craig valley bg / 0:6740006 - forest
    await p.send_tag('O_SPRITE', '11', '0:1', '0', '')  # 6740004 - foreground / 0:6740007
    await p.room.object_manager.send_map(p)
    await p.send_json(action='closeCjsnowRoomToRoom', targetWindow='cardjitsu_snowplayerselect.swf',
                      type='immediateAction')
    await p.send_tag('FX_PLAYSOUND', '0:1840002', 1, 1, 75, -1, 0, -1)


@handlers.handler(FrameworkPacket('windowReady'))
async def handle_ready_window(p, windowId=None, **data):
    if windowId == 'cardjitsu_snowtimer.swf':
        p.snow_ninja.ready_object['timer_ready'] = True
        if p.room.is_ready('timer_ready'):
            await p.room.object_manager.show_moveable_tiles()

            await p.room.round_manager.begin_timer()
            if p.snow_ninja.tip_mode:
                await p.room.show_tip(TipType.MOVE.value)
    elif windowId == 'cardjitsu_snowclose.swf':
        asyncio.create_task(join_battle(p))
