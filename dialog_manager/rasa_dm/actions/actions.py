from dataclasses import dataclass
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
from word2number import w2n


import sys
# REPO_PATH = '/your/repo/path/minetest-agent/agent/rob'

sys.path.append(REPO_PATH)
import bot_brain as b



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
    output_queue: queue.Queue

    def __init__(self, output_queue):
        super().__init__()
        self.rob = b.DemoBrain()

    def name(self) -> Text:
        return "action_send_bot_brain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        if tracker.get_intent_of_latest_message() == "ask_place_block":

            # reference_object_place_block = tracker.get_slot("reference_object_place_block")
            # repeat_count_place_block = tracker.get_slot("repeat_count_place_block")
            # block_type_place_block =  tracker.get_slot("block_type_place_block")
            block_type_place_block =  tracker.get_slot("block_type_place_block")


            request = PlaceBlock(
                # reference_object_place_block,
                # repeat_count_place_block,
                block_type_place_block
            )
            # when action is started
            if self.rob.process(request):
                # dispatcher.utter_message(text=f"I will place {repeat_count_place_block} blocks of {block_type_place_block}")
                dispatcher.utter_message(text=f"I will place a {block_type_place_block} block")
            else:
                dispatcher.utter_message(text=f"I think you want me to place a block but some parameters are wrong")

            return [SlotSet("reference_object_place_block", None), SlotSet("repeat_count_place_block", None), SlotSet("block_type_place_block", None)]



        if tracker.get_intent_of_latest_message() == "ask_destroy_block":

            tower_height_destroy_block = tracker.get_slot("tower_height_destroy_block")

            request = DestroyBlock(
                tower_height_destroy_block
            )


            if self.rob.process(request):
                dispatcher.utter_message(text=f"I will destroy the block at tower height {tower_height_destroy_block}")
            else:
                dispatcher.utter_message(text=f"I think you want me to destroy a block but some parameters are wrong.")


            return [SlotSet("tower_height_destroy_block", None)]



        if tracker.get_intent_of_latest_message() == "ask_move":

            reference_object_move = tracker.get_slot("reference_object_move")
            relative_direction_move = tracker.get_slot("relative_direction_move")
            repeat_count_move = tracker.get_slot("repeat_count_move")

            # repeat_count_move = w2n.word_to_num(repeat_count_move) or repeat_count_move

            if repeat_count_move:
                repeat_count_move = w2n.word_to_num(repeat_count_move)


            request = Move(
                # reference_object_move,
                relative_direction_move,
                repeat_count_move
            )


            if self.rob.process(request):
                dispatcher.utter_message(text=f"I'll move {repeat_count_move} counts to the {relative_direction_move}")
            else:
                dispatcher.utter_message(text=f"I think you want me to move but some parameters are wrong.")
            return [SlotSet("relative_direction_move", None), SlotSet("repeat_count_move", None), SlotSet("reference_object_move", None)]


        if tracker.get_intent_of_latest_message() == "ask_turn":

            reference_object_turn = tracker.get_slot("reference_object_turn")
            relative_direction_turn = tracker.get_slot("relative_direction_turn")
            repeat_count_turn = tracker.get_slot("repeat_count_turn")

            request = Turn(
                # reference_object_turn,
                relative_direction_turn
                # repeat_count_turn
            )



            if self.rob.process(request):
                # dispatcher.utter_message(text=f"I'll turn {repeat_count_turn} to the {relative_direction_turn}")
                dispatcher.utter_message(text=f"I'll turn to the {relative_direction_turn}")
            else:
                dispatcher.utter_message(text=f"I think you want me to turn but some parameters seem to be wrong.")

            return [SlotSet("relative_direction_turn", None), SlotSet("repeat_count_turn", None)]



        if tracker.get_intent_of_latest_message() == "ask_bot_stop_action":
            if self.rob.process(Stop()):
                dispatcher.utter_message(text="I am stopping")
            else:
                dispatcher.utter_message(text="I think you want me to stop but something is wrong. This is what the scientists warned us about.")

        if tracker.get_intent_of_latest_message() == "ask_come_here":
            request = ComeHere()

            if self.rob.process(request):
                dispatcher.utter_message(text="Okay, I'll come to where you are.")
            else:
                dispatcher.utter_message(text="I think you want me to come to where you are. But something is wrong.")


        return []
