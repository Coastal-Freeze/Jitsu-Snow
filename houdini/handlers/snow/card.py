from houdini.constants import FireNinja, WaterNinja, SnowNinja
from houdini.handlers import FrameworkPacket, TagPacket
from houdini import handlers
            
@handlers.handler(FrameworkPacket('cardClick'))
async def handle_select_card(p, cardId: int = 0, element: str = None, **data):

    ninja_element = penguin.snow_ninja.ninja.CardElement.value
    if element != ninja_element or element is None or not cardId:
        return await p.send_tag('O_WOW', 'you have no job don\'t you')
    
    p.snow_ninja.selected_card = p.server.cards[cardId]