import asyncio

import aioredis
from loguru import logger

from snow.constants import EmptyTile, OpenTile, EnemyTile, PenguinTile, OccupiedPenguinSpawnTile, \
    UnoccupiedPenguinSpawnTile, UnoccupiedEnemySpawnTile, OccupiedEnemySpawnTile, ObstacleTile
from snow.penguin import Penguin
from snow.data import db
from snow.events import event
from snow.events.module import hot_reload_module
import snow.handlers

try:
    import uvloop

    uvloop.install()
except ImportError:
    uvloop = None


class Server:

    def __init__(self, config):
        self.server = None
        self.redis = None
        self.cache = None
        self.config = config
        self.db = db
        self.peers_by_ip = {}
        
        self.attributes = {}

        self.client_class = Penguin

        self.penguins_by_id = {}
        self.penguins_by_username = {}

        self.tiles = [EmptyTile, OpenTile, EnemyTile, PenguinTile, OccupiedPenguinSpawnTile, UnoccupiedPenguinSpawnTile,
                      UnoccupiedEnemySpawnTile, OccupiedEnemySpawnTile, ObstacleTile]

        self.default_sprites = [100307, 100319, 100303, 100308, 100318, 100306, 100310, 100312, 100315, 100316, 100317,
                                100313, 100314, 100302, 100299, 100240, 100241, 100309, 100320, 100304, 1840011,
                                1840012, 1840010]
        self.move_sprites = [100341, 100367, 100323]

        self.battles = {}

    async def start(self):
        self.server = await asyncio.start_server(
            self.client_connected, self.config.address,
            self.config.port
        )

        await self.db.set_bind('postgresql://{}:{}@{}/{}'.format(
            self.config.database_username, self.config.database_password,
            self.config.database_address,
            self.config.database_name))
            
        self.redis = await aioredis.create_redis_pool('redis://{}:{}'.format(
            self.config.redis_address, self.config.redis_port),
            minsize=5, maxsize=10)

        logger.info('Booting Snow')

        await hot_reload_module(snow.handlers)

        await event.emit('boot', self)
 
        logger.info(f'Listening on {self.config.address}:{self.config.port}')

        async with self.server:
            await self.server.serve_forever()

    async def client_connected(self, reader, writer):
        client_object = self.client_class(self, reader, writer)
        await client_object.run()
