from snow.events import event, TagPacket, allow_once, has_attribute


@event.on(TagPacket("/version"))
@allow_once
async def handle_snow_version_check(p):
    await p.send_tag(
        "S_VERSION",
        "FY15-20150206 (4954)r",
        "73971eecbd8923f695303b2cd04e5f70",
        "Tue Feb  3 14:11:56 PST 2015",
        "/var/lib/jenkins/jobs/BuildPlatform/workspace/metaserver_source/dimg",
    )


@event.on(TagPacket("/place_context"))
@allow_once
async def handle_server_context(p, world, parameters):
    p.attributes["place_context"] = True
    parameters_parsed = parameters.split("&")
    for parameter in parameters_parsed:
        curr_param = parameter.split("=")
        if curr_param[0] == "tipMode":
            p.tip_mode = bool(curr_param[1])
        elif curr_param[0] == "muted":
            p.muted = bool(curr_param[1])
        else:
            p.media_url = curr_param[1]
