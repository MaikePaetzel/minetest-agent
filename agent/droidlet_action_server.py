import json
import queue

from aiohttp import web
from dialog_manager.rasa_dm.actions.actions import ActionSendBotBrain
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher


def get_action_endpoint(output_queue: queue.Queue):
    # implement the rasa actions interface, so that it is easier
    # to inject the shared queue between brain and action server
    action = ActionSendBotBrain(output_queue)

    async def health(_):
        body = {"status": "ok"}
        return web.json_response(body)

    async def handle_action(request: web.Request):
        dispatcher = CollectingDispatcher()
        rasa_json = await request.json()
        print(f"Got json from rasa {rasa_json}")
        tracker = Tracker.from_dict(rasa_json["tracker"])
        output_events = action.run(dispatcher, tracker, domain={})
        response = {"events": output_events, "responses": dispatcher.messages}
        print(f"Returning output from handle_action {json.dumps(response)}")
        return web.json_response(response)

    async def actions(_):
        body = [{"name": "action_send_bot_brain"}]
        return web.json_response(body)

    app = web.Application()
    app.add_routes(
        [
            web.post("/webhook", handle_action),
            web.get("/health", health),
            web.get("/actions", actions),
        ]
    )

    return app
