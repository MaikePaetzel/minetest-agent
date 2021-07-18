from dataclasses import dataclass
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher

# import sys
# REPO_PATH = '/your/repo/path/minetest-agent/agent/rob'
# sys.path.append(REPO_PATH)
# import bot_brain as b



class BotBrain:
    # dummy class as a stand-in for the brain implementation
    def send_action(self, action):
        print(f"bot brain received action {action}")


class BotInstruction:
    pass


@dataclass
class PlaceBlock(BotInstruction):
#    reference_object_place_block: str
#    n_blocks: str
    type: str


@dataclass
class Move(BotInstruction):
#    ref_object: str
    direction: str
    distance: str

@dataclass
class Turn(BotInstruction):
#    reference_object_turn: str
    direction: str
#    degrees: str


@dataclass
class ComeHere(BotInstruction):
    pass

@dataclass
class DestroyBlock(BotInstruction):
    height: str


@dataclass
class Stop(BotInstruction):
    pass


class ActionSendBotBrain(Action):
    def __init__(self):
        super().__init__()
        self.rob = b.DemoBrain()

    def name(self) -> Text:
        return "action_send_bot_brain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        
        # if tracker.get_intent_of_latest_message() == "ask_move_block":
        
        #     request = MoveBlock(
        #         tracker.get_slot("which_block"),
        #         tracker.get_slot("position")
        #     )
            
        #     if tracker.get_slot("which_block") and tracker.get_slot("position"):
        #         dispatcher.utter_message(text="I will move the block")
        #     self.rob.process(request)

        if tracker.get_intent_of_latest_message() == "ask_place_block":
        
            request = PlaceBlock(
                # tracker.get_slot("repeat_count_place_block"),
                tracker.get_slot("block_type_place_block")
            )
            self.rob.process(request)


        if tracker.get_intent_of_latest_message() == "ask_destroy_block":
        
            request = DestroyBlock(
                tracker.get_slot("tower_height_destroy_block")
            )
            self.rob.process(request)
        
        
            return [SlotSet("tower_height_destroy_block", None)]
        
        if tracker.get_intent_of_latest_message() == "ask_come_here":
            request = ComeHere()
            dispatcher.utter_message(text="Okay, I'll come to where you are.")

            self.rob.process(request)

            # set the slot for rasa to be able to track it
            return [SlotSet("player_position", "player_position")]
            
        if tracker.get_intent_of_latest_message() == "ask_move":
            
            request = Move(
                tracker.get_slot("relative_direction_move"),
                tracker.get_slot("repeat_count_move"),
            )

            self.rob.process(request)
            
            # if action fullfilled or started
            return [SlotSet("relative_direction_move", None), SlotSet("repeat_count_move", None)]
            # self.rob.process(request)

        if tracker.get_intent_of_latest_message() == "ask_turn":
            
            request = Turn(
                tracker.get_slot("relative_direction_turn"),
                #tracker.get_slot("repeat_count_turn"),
            )

            self.rob.process(request)
            
            # if action fullfilled or started
            return [SlotSet("relative_direction_turn", None), SlotSet("repeat_count_turn", None)]
            # self.rob.process(request)


        if tracker.get_intent_of_latest_message() == "ask_bot_stop_action":
            dispatcher.utter_message(text="I am stopping")
            self.rob.process(Stop())

        return []

