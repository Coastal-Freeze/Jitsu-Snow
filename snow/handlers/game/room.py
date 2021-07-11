from snow.constants import URLConstants
from snow.events import event, TagPacket, allow_once, has_attribute, FrameworkPacket


@event.on(FrameworkPacket('roomToRoomMinTime'))
@has_attribute('joined_world')
async def handle_joined_room(p, **kwargs):
    await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='bottomLayer', \
                      loadDescription='', type='playAction', windowUrl=p.media_url + URLConstants.close_window.value, \
                      xPercent=1, yPercent=0)
    await p.send_tag('O_HERE', 13, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    

@event.on(FrameworkPacket('roomToRoomComplete'))
@has_attribute('joined_world')
async def room_complete(p, **kwargs):
    for sprite in p.server.default_sprites:
        await p.send_tag('S_LOADSPRITE', f'0:{sprite}')
   


@event.on(FrameworkPacket('windowClosed'))
@has_attribute('joined_world')
async def handle_window_closed(p, windowId, **data):
    if windowId == 'cardjitsu_snowrounds.swf':
        p.round_closed = True
        if p.room.is_ready('round_closed'):
            await p.room.round_manager.start_round()


@event.on(FrameworkPacket('roomToRoomScreenClosed'))
@has_attribute('joined_world')
async def handle_successful_close(p, **kwargs):
    p.screen_closed = True
    if p.room.is_ready('screen_closed'):
        await p.room.round_manager.show_round_notice()
