from snow.events import event, TagPacket, allow_once, has_attribute, FrameworkPacket
from snow.constants import TipType
import snow.events

@event.on(TagPacket('use'))
@has_attribute('joined_world')
async def handle_click_tile(p, tile_id: int, a: float, b: float, c: float, d: float):
    # p.logger.error('heal target: ' + p.room.object_manager.get_heal_target_by_id(p, tile_id))
    tile_id = int(tile_id)
    ninjas = [4, 12, 13]
    if tile_id in ninjas and p.room.object_manager.get_penguin_by_id(tile_id) is not None:
        await p.room.object_manager.heal_penguin(p, tile_id)

    elif tile_id <= p.room.object_manager.map[-1][-1].id:  # Is it a tile?
        tile = p.room.object_manager.get_tile_by_id(tile_id)

        if tile is not None and tile.id == tile_id:
            for sprite in p.server.move_sprites:
                await p.room.send_tag('S_LOADSPRITE', f'0:{sprite}')

            await p.room.object_manager.plan_movement(p, tile)
    elif p.room.object_manager.get_enemy_by_id(tile_id) is not None:
        await p.room.object_manager.select_enemy(p, tile_id)


@event.on(FrameworkPacket('confirmClicked'))
@has_attribute('joined_world')
async def handle_show_confirm(p, **data):
    await p.room.object_manager.check_mark(p)


@event.on(FrameworkPacket('ShowMemberCardInfoTip'))
@has_attribute('joined_world')
async def handle_member_revive_tip(p, **data):
    await p.show_tip(TipType.BONUS_REVIVE.value, bypass_tipmode=True)
    
@event.on(FrameworkPacket('cardClick'))
@has_attribute('joined_world')
async def handle_select_card(p, cardId: int = 0, element: str = None, **data):
    ninja_element = p.ninja.card_element.value
    if element != ninja_element and element is None and not cardId:
        return await p.send_tag('O_WOW', 'you have no job don\'t you')

    p.selected_card = p.server.attributes['cards'][cardId]