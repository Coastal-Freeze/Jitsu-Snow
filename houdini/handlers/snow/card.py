from houdini import handlers
from houdini.handlers import FrameworkPacket


@handlers.handler(FrameworkPacket('cardClick'))
async def handle_select_card(p, cardId: int = 0, element: str = None, **data):
    ninja_element = p.snow_ninja.ninja.CardElement.value
    if element != ninja_element and element is None and not cardId:
        return await p.send_tag('O_WOW', 'you have no job don\'t you')

    p.snow_ninja.selected_card = p.server.cards[cardId]
