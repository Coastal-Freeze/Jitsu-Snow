import random

from snow.constants import URLConstants, CJ_SNOW_STAMPS
from snow.data import penguin
from snow.core.client import Client
from snow.data.ninja import PenguinCardCollection
from snow.managers.battleroom import BattleRoom
from loguru import logger

import json


class Penguin(Client, penguin.Penguin):
    __slots__ = (
        "attributes",
        "muted",
        "event_num",
        "ready",
        "place_ready",
        "finished_loading",
        "timer_ready",
        "screen_closed",
        "round_closed",
        "wait",
        "damage",
        "stamina",
        "tile",
        "ninja",
        "current_target",
        "heal_target",
        "deck",
        "target_objects",
        "heal_target_objects",
        "last_object",
        "modified_objects",
        "powercard_objects",
        "tip_mode",
        "confirm",
        "muted",
        "cards_depleted",
        "login_key",
        "start_xp",
        
        "powercard_element_symbol",
        "powercard_grid",
        "powercard_position",
        
        "combo",
        "selected_card"
        
        
    )

    room: BattleRoom
    cards: PenguinCardCollection

    def __init__(self, *args):
        super().__init__(*args)

        self.attributes = {}

        self.muted = False
        self.event_num = 101

        self.session_id = None
        self.is_member = False

        self.ready = False
        self.place_ready = False
        self.finished_loading = False
        self.timer_ready = False
        self.screen_closed = False
        self.round_closed = False

        self.wait = 0
        self.damage = 0
        self.stamina = 0

        self.tile = None
        self.ninja = None

        self.current_target = None
        self.heal_target = None

        self.deck = []

        self.target_objects = []
        self.heal_target_objects = []
        self.last_object = None
        self.modified_objects = []
        self.powercard_objects = []
        
        self.powercard_element_symbol = None
        self.powercard_grid = None
        self.powercard_position = (0, 0)
        self.selected_card = None

        self.tip_mode = False
        self.confirm = False
        self.muted = False
        self.cards_depleted = False
        self.combo = False
        

        

    @property
    def safe_name(self):
        return self.safe_nickname(self.server.config.lang)

    @property
    def is_alive(self):
        return int(self.damage <= self.ninja.health_points.value)

    @property
    def member(self):
        return int(self.is_member)

    def __getitem__(self, item):
        return getattr(self, item)

    async def show_end_game(self, round):
        game_stamps = [stamp for stamp in self.server.attributes["stamps"].values() if stamp.group_id == p.room.stamp_group]
        collected_stamps = [stamp for stamp in game_stamps if stamp.id in p.stamps]

        total_stamps = len([stamp for stamp in p.stamps.values() if p.server.attributes["stamps"][stamp.stamp_id].group_id])
        total_collected_stamps = len(collected_stamps)
        total_game_stamps = len(game_stamps)

        stamps = [{"_id": stamp.id, "new": stamp.recent} for stamp in collected_stamps]
        
        self.start_xp = self.snow_ninja_progress.copy()
        
        await self.update(snow_ninja_progress=self.snow_ninja_progress + 5)
        if self.snow_ninja_progress >= 100:
            await self.update(snow_ninja_rank=self.snow_ninja_rank + 1)
           
        stamp_init_payload = {
            "coinsEarned": 0,
            "xpStart": self.start_xp,
            "xpEnd": self.snow_ninja_progress,
            "rank": self.snow_ninja_rank,
            "doubleCoins": True if total_game_stamps == total_collected_stamps else False,
            "isBoss": 0,
            "round": round + 1,
            "damage": self.damage,
            "showItems": 0,
            "stamps": stamps,
            "stampList": CJ_SNOW_STAMPS,
        }
        await self.send_json(
            action="loadWindow",
            assetPath="",
            initializationPayload=stamp_init_payload,
            layerName="bottomLayer",
            loadDescription="",
            type="playAction",
            windowUrl=self.media_url + URLConstants.snow_payout.value,
            xPercent=0.08,
            yPercent=0.05,
        )

    async def add_stamp(self, stamp, notify=True):
        if stamp.id in self.stamps:
            return False

        await self.stamps.insert(stamp_id=stamp.id)

        rank_tokens = {1: "easy", 2: "medium", 3: "hard", 4: "extreme"}

        stamp_init_payload = {
            "description": f"global_content.stamps.{stamp.id}.description",
            "is_member": self.member,
            "name": f"global_content.stamps.{stamp.id}.name",
            "parent_group_id": 8,
            "rank": stamp.rank,
            "rank_token": rank_tokens[stamp.rank],
            "stampGroupId": stamp.group_id,
            "stamp_id": stamp.id,
        }

        if notify:
            await self.send_json(
                action="loadWindow",
                assetPath="",
                initializationPayload=stamp_init_payload,
                layerName="bottomLayer",
                loadDescription="",
                type="playAction",
                windowUrl=self.media_url + URLConstants.stamp_earned.value,
                xPercent=0.1,
                yPercent=0,
            )

        logger.info(f"{self.username} earned stamp '{stamp.name}'")
        self.server.cache.delete(f"stamps.{self.id}")

        return True

    async def add_stamina(self, stamina):
        self.stamina += stamina
        payload = {"cycle": False, "stamina": self.stamina}
        if self.stamina == 12 and self.cards and len(self.deck) < 4:
            self.stamina = 0
            card = self.add_powercard()
            payload["cycle"] = True
            payload["cardData"] = card

        await self.send_json(
            action="jsonPayload",
            jsonPayload=payload,
            targetWindow=self.media_url + URLConstants.snow_ui.value,
            triggerName="updateStamina",
            type="immediateAction",
        )

    def add_powercard(self):
        if len(self.cards) == 0:
            self.cards_depleted = True

        card = random.choice(self.cards)
        self.cards.remove(card)
        self.deck.append(card)
        card_data = dict(
            asset="",
            card_id=card.id,
            color=card.color,
            description=card.description,
            element=card.element,
            is_active=str(bool(self.is_alive)),
            label=card.name,
            name=card.name,
            power_id=card.power_id,
            prompt=card.name,
            set_id=card.set_id,
            value=card.value,
        )
        return card_data

    async def show_ui(self):
        await self.send_json(
            action="loadWindow",
            assetPath="",
            initializationPayload={
                "cardsAssetPath": f"{self.media_url}minigames/cjsnow/en_US/deploy/",
                "element": self.ninja.element.value,
                "isMember": self.is_member,
            },
            layerName="bottomLayer",
            loadDescription="",
            type="playAction",
            windowUrl=self.media_url + URLConstants.snow_ui.value,
            xPercent=0.5,
            yPercent=1,
        )

    async def show_timer(self):
        await self.send_json(
            action="loadWindow",
            assetPath="",
            initializationPayload={"element": self.ninja.element.value},
            layerName="bottomLayer",
            loadDescription="",
            type="playAction",
            windowUrl=self.media_url + URLConstants.snow_timer.value,
            xPercent=0.5,
            yPercent=0,
        )

    async def show_timer_confirm(self):
        await self.room.send_json(
            action="jsonPayload",
            jsonPayload={"isEnabled": self.is_alive},
            targetWindow=self.media_url + URLConstants.snow_timer.value,
            triggerName="enableConfirm",
            type="immediateAction",
        )

    async def show_round_notice(self, round_num, bonus_criteria, remaining_time=0):
        await self.send_json(
            action="loadWindow",
            assetPath="",
            initializationPayload={
                "bonusCriteria": bonus_criteria,
                "roundNumber": round_num,
                "remainingTime": remaining_time,
            },
            layerName="bottomLayer",
            loadDescription="",
            type="playAction",
            windowUrl=f"{self.media_url}minigames/cjsnow/en_US/deploy/swf/ui/windows"
            f"/cardjitsu_snowrounds.swf",
            xPercent=0.2,
            yPercent=0.1,
        )

    async def show_tip(self, tip_name, bypass_tipmode=False):
        if bypass_tipmode or self.tip_mode:
            await self.send_json(
                action="loadWindow",
                assetPath="",
                initializationPayload={
                    "element": self.ninja.element.value,
                    "phase": tip_name,
                },
                layerName="bottomLayer",
                loadDescription="",
                type="playAction",
                windowUrl=f"{self.media_url}minigames/cjsnow/en_US/deploy/swf/ui/windows"
                f"/cardjitsu_snowinfotip.swf",
                xPercent=0.1,
                yPercent=0,
            )

    def __repr__(self):
        if self.id is not None:
            return f"<Penguin ID='{self.id}' Username='{self.username}'>"
        return super().__repr__()
