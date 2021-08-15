import asyncio
import random

from snow.constants import (
    BonusRoundType,
    RoundState,
    OccupiedEnemySpawnTile,
    URLConstants,
    CJ_SNOW_STAMPS,
)
from loguru import logger


class RoundManager:
    def __init__(self, room):
        self.room = room
        self.started = False
        self.round = 0
        self.state = RoundState.NEW_ROUND
        self.bonus_criteria = None
        self.bonus_time = None
        self.dealt = False

        self.ticks = None
        self.callback = None

        self.randomize_bonus_criteria()

    def randomize_bonus_criteria(self):
        self.bonus_criteria = random.choice(
            [BonusRoundType.NO_NINJAS_DOWN, BonusRoundType.FULL_HEALTH]
        )

    def deal(self):
        for penguin in self.room.penguins:
            penguin_element = penguin.ninja.card_element.value
            card_temp = [
                penguin.server.attributes["cards"][card.card_id]
                for card in penguin.cards.values()
                for _ in range(card.quantity + card.member_quantity)
            ]
            penguin.cards = [
                card
                for card in card_temp
                if card.power_id != 0 and card.element == penguin_element
            ]
            logger.error(penguin.cards)
            self.dealt = True

    async def start_round(self):
        self.state = RoundState.NINJA_TURN

        self.room.enemy_manager.generate_enemies()
        await self.spawn_enemies()

        await self.load_timer()
        await self.load_ui()
        for p in self.room.penguins:
            p.round_closed = False

        if not self.dealt:
            self.deal()

        if self.round == 2:
            await self.end_game()

    async def end_game(self):
        for p in self.room.penguins:
            await penguin.show_end_game(self.round)

    async def spawn_enemies(self):
        for i, enemy_obj in enumerate(self.room.object_manager.enemies):
            enemy_hp_obj = self.room.object_manager.enemy_hpbars[i]

            adjusted_x = round(
                enemy_obj.x + enemy_obj.parent.x_coordinate_offset.value,
                enemy_obj.parent.x_coordinate_decimals.value,
            )
            adjusted_y = round(
                enemy_obj.y + enemy_obj.parent.y_coordinate_offset.value,
                enemy_obj.parent.y_coordinate_decimals.value,
            )

            await self.room.send_tag("O_HERE", enemy_obj.id, enemy_obj.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0, enemy_obj.name, enemy_obj.template_id, 0, 1, 0)
            await self.room.send_tag("P_TILECHANGE", enemy_obj.x, enemy_obj.y, OccupiedEnemySpawnTile.tile_url.value)
            await self.room.send_tag("O_HERE", enemy_hp_obj.id, enemy_hp_obj.art_index, adjusted_x, adjusted_y, 0, 1, 0, 0, 0, enemy_hp_obj.name, enemy_hp_obj.template_id, 0, 1, 0)
            await self.room.send_tag(
                "O_SPRITEANIM", enemy_hp_obj.id, 1, 1, 0, "play_once", 0
            )
            await self.room.send_tag("O_SPRITE", enemy_hp_obj.id, "0:100395", 1, "")

            await self.room.animation_manager.play_animation(
                enemy_obj, "0:100379", "play_once", 700
            )

            await self.room.sound_manager.play_sound("0:1840009")
            await self.room.animation_manager.play_animation(
                enemy_obj,
                enemy_obj.owner.idle_animation.value,
                "loop",
                enemy_obj.owner.idle_animation_duration.value,
            )
        # 0 :100305: sly , 0:100297:tank, 0:100311: scrap

    async def show_round_notice(self):
        logger.info(self.room.penguins)
        for penguin in self.room.penguins:
            await penguin.show_round_notice(self.round, self.bonus_criteria.value)

    async def increase_movement_stamina(self):
        for penguin in self.room.penguins:
            if penguin.last_object is not None:
                await penguin.add_stamina(2)

    async def begin_timer(self):
        await self.show_timer()
        self.callback = asyncio.create_task(self.timer_callback())

    async def timer_callback(self):
        try:
            await asyncio.sleep(2)  # catch up
            self.ticks = 9
            while True:
                await self.room.send_json(
                    action="jsonPayload",
                    jsonPayload={"tick": self.ticks},
                    targetWindow=self.room.penguins[0].media_url
                    + URLConstants.snow_timer.value,
                    triggerName="update",
                    type="immediateAction",
                )

                await asyncio.sleep(1)
                self.ticks -= 1

                if self.ticks < 0:
                    await self.expire_timer()
                    break

        except asyncio.CancelledError:
            pass

    async def expire_timer(self):
        for p in self.room.object_manager.get_alive_ninjas():
            p.confirm = False
        await self.room.send_tag("S_LOADSPRITE", "0:100324")
        await self.room.send_tag("S_LOADSPRITE", "0:100342")
        await self.room.send_tag("S_LOADSPRITE", "0:100364")
        await self.increase_movement_stamina()
        await self.hide_timer()
        await self.room.object_manager.do_move_action()
        await asyncio.sleep(3)
        await self.room.enemy_manager.do_enemy_turn()
        await asyncio.sleep(3)  # need to show tiles too
        if len(self.room.penguins) > 1:
            await self.room.object_manager.show_moveable_tiles()
            await self.begin_timer()

    async def show_timer(self):
        await self.room.send_json(
            action="jsonPayload",
            jsonPayload=[None],
            targetWindow=self.room.penguins[0].media_url + URLConstants.snow_ui.value,
            triggerName="enableCards",
            type="immediateAction",
        )
        await self.show_timer_confirm()
        await self.room.send_json(
            action="jsonPayload",
            jsonPayload=[None],
            targetWindow=self.room.penguins[0].media_url
            + URLConstants.snow_timer.value,
            triggerName="Timer_Start",
            type="immediateAction",
        )

    async def hide_timer(self):
        await self.room.send_json(
            action="jsonPayload",
            jsonPayload=[None],
            targetWindow=self.room.penguins[0].media_url
            + URLConstants.snow_timer.value,
            triggerName="skipToTransitionOut",
            type="immediateAction",
        )

        await self.room.send_json(
            action="jsonPayload",
            jsonPayload=[None],
            targetWindow=self.room.penguins[0].media_url + URLConstants.snow_ui.value,
            triggerName="disableCards",
            type="immediateAction",
        )
        await self.room.send_json(
            action="jsonPayload",
            jsonPayload=[None],
            targetWindow=self.room.penguins[0].media_url
            + URLConstants.snow_timer.value,
            triggerName="disableConfirm",
            type="immediateAction",
        )

        await self.room.object_manager.remove_movement_plans()

    async def load_ui(self):
        for penguin in self.room.penguins:
            await penguin.show_ui()

    async def load_timer(self):
        for penguin in self.room.penguins:
            await penguin.show_timer()

    async def show_timer_confirm(self):
        for penguin in self.room.penguins:
            await penguin.show_timer_confirm()
