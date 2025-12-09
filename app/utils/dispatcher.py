active_connections = {}


async def dispatch_event_ws(user_id: str, event: str, data: dict):

    ws = active_connections.get(user_id)
    if ws:
        body = {"event": event, **data}
        await ws.send_json(body)
