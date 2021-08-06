from snow.data.ninja import CardCollection, CardStarterDeck
from snow.events import event, FrameworkPacket
from loguru import logger


@event.on("boot")
async def gather_cards(server):
    server.attributes["cards"] = await CardCollection.get_collection()
    logger.info(f'Loaded {len(server.attributes["cards"])} ninja cards')
