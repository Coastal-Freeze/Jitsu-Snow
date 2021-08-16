

class CardManager:

    def __init__(self, room):
        self.room = room
        self.object_manager = room.object_manager
        self.animation_manager = room.animation_manager
        self.sound_manager = room.sound_manager
        
        self.powercard_positions = []

    async def select_tile(self, p, tile):
    
        if p.powercard_element_symbol is not None:
            await p.send_tag('O_GONE', p.powercard_element_symbol.id)
            await p.send_tag('O_GONE', p.powercard_grid.id)
            self.powercard_positions.remove(p.powercard_position)
    
        width = height = 3

        if tile.x + 1 > 8 or tile.x - 1 < 0:
            width = 2

        if tile.y + 1 > 4 or tile.y - 1 < 0:
            height = 2
            
        sizes = {'2x2': '0:100269', '2x3': '0:100268', '3x2': '0:100267', '3x3': '0:100266'}
            
        elements = {'snow':'0:100121', 'water':'0:100122', 'fire':'0:100120'}
            
        element_object = self.object_manager.generate_object("0:1", "0:1", x, y, parent=p)
        p.powercard_element_symbol = element_object
        await self.room.send_tag('O_HERE', element_object.id, "0:1", tile.x, tile.y, 0, 1, 0, 0, 0, element_object.name, "0:1", 0, 1, 0)
        await self.room.send_tag('O_SPRITE', element_object.id, elements[p.ninja.element.value], 0)
           
        powercard_grid = self.object_manager.generate_object("0:1", "0:1", x, y)
        p.powercard_grid = powercard_grid
        await p.send_tag('O_HERE', powercard_grid.id, "0:1", tile.x, tile.y, 0, 1, 0, 0, 0, powercard_grid.name, "0:1", 0, 1, 0)
        await p.send_tag('O_SPRITE', powercard_grid.id, sizes[f'{width}x{height}'], 0)
        
        p.powercard_position = (tile.x, tile.y)
        self.powercard_positions.append(p.powercard_position)
        
    async def do_card_action(self):
        for p in self.room.penguins:
            if p.powercard_element_symbol is not None:
                card_x, card_y = p.powercard_position
                powercard_area = [(tile.x, tile.y) for tile in self.object_manager.get_tiles_from_range(card_x, card_y, 3)]
                elements = [p.ninja.element.value for p in self.room.penguins if p.powercard_position is not None and p.powercard_position in powercard_area]
               
        elements = []
        for i, pos in enumerate(self.powercard_positions):
            powercard_area = [(tile.x, tile.y) for tile in self.object_manager.get_tiles_from_range(x, y, 3)]
            els = [p.ninja.element.value for p in self.room.penguins if p.powercard_position is not None and p.powercard_position]
            for el in els:
                if el in elements:
                    continue
                
                elements.append(el)
                
        if len(elements) > 1:
            await self.room.send_json(
                windowUrl= f"{p.media_url}/minigames/cjsnow/en_US/deploy/swf/ui/windows/cardjitsu_snowcombos.swf",
                action='loadWindow',
                initializationPayload={"data":elements},
                layerName="bottomLayer",
                type="playAction,
                assetPath="",
                loadDescription="",
                yPercent=0.5,
                xPercent=0.5
            )
            
        
        