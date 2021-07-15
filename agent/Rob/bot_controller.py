import miney
import time
from enum import Enum
from concurrent import futures
import configparser
import agent.Rob.atomic_actions as aa

class State(Enum):
    NOEXIST = 0
    IDLE = 1
    RUNNING = 2

class BotController:
    """
    This class registers a bot object with the game
    and takes care of controlling it via atomic actions.
    MineyNpc - initializing minetest
    @param? ip : server address, local by default
    @param? port : server port, default 29999
    @param? username : default "Minehart"
    @param? password : default ""
    """    

    def __init__(self, server="127.0.0.1", playername="Minehart", password="", port=29999):
        self.state = State.NOEXIST
        self.action_q = []
        self.mt = miney.Minetest(server, playername, password, port)
        self.lua_runner = miney.Lua(self.mt)

        # CONFIG_PATH = '/your/repo/path/minetest-agent/agent/rob/newnpc.conf'

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        config = config['NPC']

        player = self.mt.player[0]
        bot_id = config['ID']
        
        self.id = bot_id
        if config.getboolean('SPAWN_ON_PLAYER'):
            pos = player.position
            pos_vector = tuple([pos['x'], pos['y']+1, pos['z']])
        else:
            pos = [float(i) for i in config['SPAWN_POSITION'].split()]
            pos_vector = tuple([pos[0], pos[1]+1, pos[2]])

        yaw = float(config['YAW'])
        modname = config['MOD_NAME']
        ownername = config['OWNER_NAME']

        add_rob = f"""
        local ref = {{
            id = "{bot_id}",
            pos = vector.new{pos_vector},
            yaw = {yaw},
            name = "{modname}",
            owner = "{ownername}",
        }}
        npcf:add_npc(ref)
        """

        # testing if rob already exists
        test_rob = """
        local e = npcf:get_luaentity(\"""" + bot_id + """\")
            if e then
                return true
            else
                return false
            end
        """

        for i in range(3):
            if self.lua_runner.run(test_rob):
                self.state = State.IDLE
                print("Rob is initialized")
                break
            print(str(i+1) + ". try to initialize Rob")
            self.lua_runner.run(add_rob)
            # TODO: sleep for max time or just await ingame result
            time.sleep(10)
        
        if not self.lua_runner.run(test_rob):
            # TODO: raise exceptions
            print("Initializing Rob FAILED")
        
    def start_execution(self):
        assert self.state != State.NOEXIST
        COMMAND_DELAY = 1.0
        self.state = State.RUNNING

        while len(self.action_q) > 0:
            self.action = self.action_q[-1]
            print("Result of Action: ", self.action())
            time.sleep(COMMAND_DELAY)
            # pop only after the action is done
            self.action_q.pop()
        
        self.state = State.IDLE

    def add_action(self, action):
        self.action_q.append(action)

    def stop_execution(self):
        # TODO: interrupt current ingame action
        self.action_q.clear()
        self.state = State.IDLE

    def skip_current_action(self):
        # TODO: interrupt current ingame action and continue with next
        pass
