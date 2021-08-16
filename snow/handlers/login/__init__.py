from snow.constants import URLConstants
from snow.data.ninja import PenguinCardCollection
from snow.events import TagPacket, event, has_attribute, allow_once
from loguru import logger
from snow.data.penguin import Penguin
import ujson


@event.on(TagPacket("/login"))
@has_attribute("place_context")
@allow_once
async def snow_login(p, environment, p_id: int, token: str):
    p_id = int(p_id)

    token = token.strip()
    server_token = ujson.loads(await p.server.redis.get(token))

    peng_id = int(server_token["player_id"])

    logger.info(repr(peng_id))
    logger.info(server_token)

    if server_token is None or peng_id != p_id:
        logger.error(f"{p_id} failed to login L")
        await p.send_tag("S_LOGINDEBUG", "user code 1000")
        await p.send_tag("S_ERROR", 900, "Error", -1, "No")
        return

    data = await Penguin.query.where(Penguin.id == p_id).gino.first()
    if data is not None:
        logger.info(f"{data.username} Is Logging IN!")
        p.update(**data.to_dict())

        p.muted = server_token["is_muted"]

        if p.id in p.server.penguins_by_id:  # thank you dote
            await p.send_tag("S_LOGINDEBUG", "Already logged in")
            await p.send_tag("S_LOGGEDIN")

            p.attributes["force_login_event"] = asyncio.Event()
            await wait_for_event(
                p.attributes["force_login_event"], 60
            )  # wait for next 60 sec

            if p.attributes["force_login_event"].is_set():
                try:
                    await user.close(msg="Force disconnect from another login")
                except Exception:
                    pass
                del p.attributes["force_login_event"]
            else:
                await p.close(msg="connection timeout")
                return

        p.cards = await PenguinCardCollection.get_collection(p.id)
        await p.send_tag("S_LOGINDEBUG", "Finalizing login")
        await p.send_tag("S_LOGIN", p_id)
        await p.send_tag("S_WORLDTYPE", 0, 1, 0)
        await p.send_tag(
            "S_WORLD",
            1,
            "cjsnow_0",
            "0:0",
            0,
            "none",
            0,
            p_id,
            "cjsnow_0",
            0,
            87.5309,
            0,
        )
        
        p.stamps = await PenguinStampCollection.get_collection(p.id)
        await p.send_tag("W_DISPLAYSTATE")
        await p.send_tag("W_ASSETSCOMPLETE", p_id)
        p.attributes["joined_world"] = True

        p.is_member = True


@event.on(TagPacket("/force_login"))
@has_attribute("force_login_event")
@allow_once
async def force_login(p, environment, p_id: int, token: str):
    p.attributes["force_login_event"].set()


async def wait_for_event(evt, timeout):
    try:
        await asyncio.wait_for(evt.wait(), timeout)
    except asyncio.TimeoutError:
        pass

    return evt.is_set()
