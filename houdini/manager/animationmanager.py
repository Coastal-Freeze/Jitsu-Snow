import asyncio

class AnimationManager:

    def __init__(self, room):
        self.room = room

        #self.callbacks = {'fire': [], 'water': [], 'snow': []}

        self.completed_animations = {}
        self.animation_id = 15
    
    async def play_animation(self, obj, animation_index, frame, duration):
        for player in self.room.penguins:
            await player.send_tag('O_ANIM', obj.id, animation_index, frame, duration, \
                                    1, 0 if frame == 'play_once' else 1, obj.id, self.animation_id, 0, 0)
                                                                        # this 9 represents an object, shit
        
        self.animation_id += 1
    
    async def play_individual_animation(self, player, obj, animation_index, frame, duration):
        await player.send_tag('O_ANIM', obj.id, animation_index, frame, duration, \
                                1, 0 if frame == 'play_once' else 1, obj.id, self.animation_id, 0, 0)
        
        self.animation_id += 1
    
    async def display_target(self, player, target_obj):
        await player.send_tag('O_SPRITE', target_obj.id, target_obj.parent.SpriteAnimation.value, 1)
        await player.send_tag('O_SPRITEANIM', target_obj.id, 1, 6, 1, 'play_once', target_obj.parent.SpriteDuration.value)

        await asyncio.sleep(target_obj.parent.SpriteDuration.value * 0.001)

        await player.send_tag('O_SPRITE', target_obj.id, target_obj.parent.SpriteLoopAnimation.value, 1)
        await player.send_tag('O_SPRITEANIM', target_obj.id, 1, 60, 0, 'loop', target_obj.parent.SpriteLoopDuration.value)

    async def green_target(self, player, target_obj):
        await player.send_tag('O_SPRITE', target_obj.id, target_obj.parent.SpriteAnimation.value, 1)
        await player.send_tag('O_SPRITEANIM', target_obj.id, 1, 6, 0, 'play_once', target_obj.parent.SpriteDuration.value)
        await player.room.sound_manager.play_individual_sound(player, target_obj.parent.Sound.value)

        await asyncio.sleep(target_obj.parent.SpriteDuration.value * 0.001)

        await player.send_tag('O_SPRITE', target_obj.id, target_obj.parent.SpriteLoopAnimation.value, 1)
        await player.send_tag('O_SPRITEANIM', target_obj.id, 1, 60, 0, 'loop', target_obj.parent.SpriteLoopDuration.value)

