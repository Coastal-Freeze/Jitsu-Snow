from houdini import handlers
from houdini.handlers import login, FrameworkPacket, TagPacket, DummyEventPacket
from houdini.constants import FireNinja, WaterNinja, SnowNinja, URLConstants, TipType
import asyncio
    
      
@handlers.handler(FrameworkPacket('roomToRoomComplete'), pre_login=True)
async def handle_joined_room(p, **kwargs):
    if p.server.snow_world:
        for sprite in p.server.default_sprites:	
            await p.send_tag('S_LOADSPRITE', f'0:{sprite}')	
            
            
        await p.send_json(action='loadWindow', assetPath='', initializationPayload=[None], layerName='bottomLayer', \
                            loadDescription='', type='playAction', windowUrl=p.media_url + URLConstants.CloseWindow.value, \
                            xPercent=1, yPercent=0) 
        await p.send_tag('O_HERE', 13, '0:1', 4.5, 2.5, 0, 1, 0, 0, 0, '', '0:1', 0, 1, 0)
    

@handlers.handler(FrameworkPacket('windowClosed'))
async def handle_window_closed(p, windowId, **data):
    if windowId == 'cardjitsu_snowrounds.swf':
        p.snow_ninja.ready_object['round_closed'] = True
        if p.room.is_ready('round_closed'):
            await p.room.round_manager.start_round()
     
@handlers.handler(FrameworkPacket('roomToRoomScreenClosed'))
async def handle_successful_close(p, **kwargs):
    p.snow_ninja.ready_object['screen_closed'] = True
    if p.room.is_ready('screen_closed'):
        await p.room.round_manager.show_round_notice()