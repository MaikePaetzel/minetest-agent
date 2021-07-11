import queue
import sys
sys.path.append("/home/nrg/potsdam/embagent/minetest-agent/droidlet/")

import logging

from agents.core import BaseAgent
from droidlet.memory.sql_memory import AgentMemory


class Robo(BaseAgent):
    def __init__(self, action_input_queue: queue.Queue, world=None, opts=None):
        self.action_input_queue = action_input_queue
        self.world = world
        self.last_task_memid = None
        self.pos = (0, 0, 0)
        super(Robo, self).__init__(opts)

    def init_memory(self):
        self.memory = AgentMemory()

    def init_perception(self):
        self.perception_modules = {}
        self.perception_modules['heuristic'] = HeuristicPerception(self)

    def init_controller(self):
        pass

    def perceive(self):
        self.world.step() # update world state
        for perception_module in self.perception_modules.values():
            perception_module.perceive()

    def controller_step(self):
        # need to get incoming dialogue actions and work out what to do with them
        pass

    def task_step(self, sleep_time=5):
        while (
            self.memory.task_stack_peek() and self.memory.task_stack_peek().task.check_finished()
        ):
            self.memory.task_stack_pop()

        # do nothing if there's no task
        if self.memory.task_stack_peek() is None:
            return

        # If something to do, step the topmost task
        task_mem = self.memory.task_stack_peek()
        if task_mem.memid != self.last_task_memid:
            logging.info("Starting task {}".format(task_mem.task))
            self.last_task_memid = task_mem.memid
        task_mem.task.step(self)
        self.memory.task_stack_update_task(task_mem.memid, task_mem.task)

    def handle_exception(self, e):
        pass

    def get_incoming_chats(self):
        pass

    def send_chat(self, chat):
        pass


class MinetestWorld:
    def __init__(self, opts=None, spec=None):
        # interact via miney etc
        pass

    def step(self):
        pass


# heuristic_perception.py
class HeuristicPerception:
    def __init__(self, agent):
        self.agent = agent

    def perceive(self):
        # get the n x n x n grid of blocks
        pass