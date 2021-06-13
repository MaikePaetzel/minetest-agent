import miney
from Rob.RobBrain import RobBrain
import time
import configparser



class BotController :
    """
    This class registers a bot object with the game
    and takes care of controlling it via atomic actions.
    MineyNpc - initializing minetest
    @param? ip : server address, local by default
    @param? port : server port, default 29999
    @param? username : default "RobController"
    @param? password : default "123456789"

    """

    CONFIG_PATH = 'Rob/newnpc.conf'

    def __init__(self, IP="127.0.0.1",port="29999", username="RobController", password="123456789"):
        self.mt = miney.Minetest()
        self.lua_runner = miney.Lua(self.mt)
        self.brain = None
        # TODO: iterate over all the npc's that exist and have a list of them

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)
        print(config.sections())
        config = config['NPC']

        playername = self.mt.player[0].name
        player = self.mt.player[0]

        _id = config['ID']

        self.id = _id
        if config.getboolean('SPAWN_ON_PLAYER'):
            pos = player.position
            pos_vector = tuple([pos['x'], pos['y']+1, pos['z']])
        else:
            pos = [float(i) for i in config['SPAWN_POSITION'].split()]
            pos_vector = tuple([pos[0], pos[1]+1, pos[2]])

        yaw = float(config['YAW'])
        modname = config['MOD_NAME']
        ownername = config['OWNER_NAME']

        add_npc = """
        local ref = {{
            id = "{_id}",
            pos = vector.new{pos_vector},
            yaw = {yaw},
            name = "{modname}",
            owner = "{ownername}",
        }}
        npcf:add_npc(ref)
        """

        # testing if rob already exists
        test_rob = """
        local e = npcf:get_luaentity( \"""" + _id + """\" )
            if e then
                return true
            else
                return false
            end
        """
        if  not self.send_lua(test_rob) :
            print(self.send_lua(add_npc))
            time.sleep(10)
        else :
            print("bot is initialized")

    def send_lua(self,cmd):
        return self.lua_runner.run(cmd)

    def init_rob_brain(self):
        self.brain = RobBrain()





