from snow.data.ninja import CardCollection, CardStarterDeck
from snow.events import event, FrameworkPacket


@event.on('boot')
async def gather_cards(server):
    server.attrib['cards'] = await CardCollection.get_collection()
    server.logger.info(f'Loaded {len(server.attrib["cards"])} ninja cards')


@event.on(FrameworkPacket('cardClick'))
async def handle_select_card(p, cardId: int = 0, element: str = None, **data):
    ninja_element = p.ninja.card_element.value
    if element != ninja_element and element is None and not cardId:
        return await p.send_tag('O_WOW', 'you have no job don\'t you')

    p.selected_card = p.server.cards[cardId]
