from dataclasses import dataclass
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import sys
REPO_PATH = '/your/repo/path/minetest-agent/agent/rob'
sys.path.append(REPO_PATH)
import bot_brain as b


class BotBrain:
    # dummy class
    def send_action(self, action):
        print(f"bot brain received action {action}")


class BotInstruction:
    pass


@dataclass
class MoveBlock(BotInstruction):
    which_block: str
    where_to: str


@dataclass
class ComeHere(BotInstruction):
    where_to: str



@dataclass
class Stop(BotInstruction):
    pass



class ActionSendBotBrain(Action):
    def __init__(self):
        super().__init__()
        self.bot_brain = BotBrain()
        # TODO: replace Dummy
        # self.rob = b.DummyBrain()

    def name(self) -> Text:
        return "action_send_bot_brain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        
        if tracker.get_intent_of_latest_message() == "ask_move_block":
                
            bot_action = MoveBlock(
                tracker.get_slot("which_block"),
                tracker.get_slot("position")
            )

            if tracker.get_slot("which_block") and tracker.get_slot("position"):
                dispatcher.utter_message(text="I will move the block")
            self.bot_brain.send_action(bot_action)
        
        if tracker.get_intent_of_latest_message() == "ask_come_here":
            request = ComeHere(
                "player_position"
            )
            dispatcher.utter_message(text="Okay, I'll come to where you are.")
            self.bot_brain.send_action(bot_action)

            # make call to the brain
            # self.rob.process(request)

            #set slot for the tracker
            return [SlotSet("player_position", "player_position")]
            

        if tracker.get_intent_of_latest_message() == "ask_bot_stop_action":
            dispatcher.utter_message(text="I am stopping")
            self.bot_brain.send_action(Stop())

        return []


