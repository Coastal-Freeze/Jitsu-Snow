class SoundManager:

    def __init__(self, room):
        self.room = room

        self.completed_sounds = {}
        self.sound_id = 5
    
    async def play_sound(self, sound_index):
        for player in self.room.penguins:
            if not player.snow_ninja.muted:
                await player.send_tag('FX_PLAYSOUND', sound_index, self.sound_id, 0, 100, -1, 0, -1)
        
        self.sound_id += 1
    
    async def play_individual_sound(self, player, sound_index):
        if not player.snow_ninja.muted:
            await player.send_tag('FX_PLAYSOUND', sound_index, self.sound_id, 0, 100, -1, 0, -1)
        
        self.sound_id += 1