from dataclasses import dataclass
from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher

import queue


class BotInstruction:
    pass


@dataclass
class PlaceBlock(BotInstruction):
    reference_object_place_block: str
    repeat_count_place_block: str
    block_type_place_block: str


@dataclass
class Move(BotInstruction):
    reference_object_move: str
    relative_direction_move: str
    repeat_count_move: str


@dataclass
class Turn(BotInstruction):
    reference_object_turn: str
    relative_direction_turn: str
    repeat_count_turn: str


@dataclass
class ComeHere(BotInstruction):
    where_to: str


@dataclass
class DestroyBlock(BotInstruction):
    tower_height_destroy_block: str


@dataclass
class Stop(BotInstruction):
    pass


class ActionSendBotBrain(Action):
    output_queue: queue.Queue

    def __init__(self, output_queue):
        super().__init__()
        self.output_queue = output_queue

    def name(self) -> Text:
        return "action_send_bot_brain"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:


        print(f"Got intent from tracker: {tracker.get_intent_of_latest_message()}")

        if tracker.get_intent_of_latest_message() == "ask_place_block":

            bot_action = PlaceBlock(
                tracker.get_slot("reference_object_place_block"),
                tracker.get_slot("repeat_count_place_block"),
                tracker.get_slot("block_type_place_block")
            )
            self.output_queue.put_nowait(bot_action)


        if tracker.get_intent_of_latest_message() == "ask_destroy_block":

            bot_action = DestroyBlock(
                tracker.get_slot("tower_height_destroy_block")
            )
            self.output_queue.put_nowait(bot_action)


            return [SlotSet("tower_height_destroy_block", None)]

        if tracker.get_intent_of_latest_message() == "ask_come_here":
            request = ComeHere(
                "player_position"
            )
            dispatcher.utter_message(text="Okay, I'll come to where you are.")


            # self.rob.process(request)
            self.output_queue.put_nowait(request)

            # set the slot for rasa to be able to track it
            return [SlotSet("player_position", "player_position")]

        if tracker.get_intent_of_latest_message() == "ask_move":

            request = Move(
                tracker.get_slot("reference_object_move"),
                tracker.get_slot("relative_direction_move"),
                tracker.get_slot("repeat_count_move"),
            )

            if tracker.get_slot("reference_object_move"):
                self.output_queue.put_nowait(request)
                return []

            self.output_queue.put_nowait(request)

            # if action fullfilled or started
            return [SlotSet("relative_direction_move", None), SlotSet("repeat_count_move", None)]
            # self.rob.process(request)

        if tracker.get_intent_of_latest_message() == "ask_turn":

            request = Turn(
                tracker.get_slot("reference_object_turn"),
                tracker.get_slot("relative_direction_turn"),
                tracker.get_slot("repeat_count_turn"),
            )

            if tracker.get_slot("reference_object_turn"):
                self.output_queue.put_nowait(request)
                return [SlotSet("reference_object_turn", None)]

            self.output_queue.put_nowait(request)
            dispatcher.utter_message(text="Ok I am turning")

            # if action fullfilled or started
            return [SlotSet("relative_direction_turn", None), SlotSet("repeat_count_turn", None)]


        if tracker.get_intent_of_latest_message() == "ask_bot_stop_action":
            dispatcher.utter_message(text="I am stopping")
            self.output_queue.put_nowait(Stop())

        return []

