from houdini.constants import FireNinja, WaterNinja, SnowNinja
from houdini.handlers import FrameworkPacket, TagPacket
from houdini import handlers


@handlers.handler(FrameworkPacket('mmElementSelected'))
async def handle_select_element(p, tipMode=False, element=None, **data):
    p.snow_ninja.tip_mode = tipMode
    p.snow_ninja.current_object = FireNinja

    if element == 'water':
        p.snow_ninja.current_object = WaterNinja
    elif element == 'snow':
        p.snow_ninja.current_object = SnowNinja

    p.server.snow_match_making.add_penguin(p)
    
    
@handlers.handler(FrameworkPacket('mmCancel'))
async def handle_cancel_matchmaking(p, **data):
    p.server.snow_match_making.remove_penguin(p)