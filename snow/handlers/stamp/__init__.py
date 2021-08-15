from snow.data.stamp import StampCollection
from snow.events import event, FrameworkPacket
from loguru import logger


@event.on("boot")
async def gather_stamps(server):
    server.attributes["stamps"] = await StampCollection.get_collection()
    logger.info(f'Loaded {len(server.attributes["stamps"])} Stamps')
