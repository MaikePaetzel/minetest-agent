# Import section
import time
import configparser


class MineyNpcController :
    """
    MineyNpcController
    The idea is to seperate the movement controller from the other part to make it easier to read
    just hope it won't end into banana code
    """

    def __init__(self, mineynpc):
        self.mc = mineynpc
        # Probabliy iterate over all the npc's that exist and have a list of them


        config = configparser.ConfigParser()
        config.read('MineyNpcMod/newnpc.conf')
        print(config.sections())
        config = config['NPC']

        playername = self.mc.mt.player[0].name
        player = self.mc.mt.player[0]

        _id = config['ID']

        self.id = _id
        if config.getboolean('SPAWN_ON_PLAYER'):
            pos = player.position
            pos_vector = tuple([pos['x'], pos['y']+3, pos['z']])
        else:
            pos = [float(i) for i in config['SPAWN_POSITION'].split()]
            pos_vector = tuple([pos[0], pos[1]+3, pos[2]])

        yaw = float(config['YAW'])
        modname = config['MOD_NAME']
        ownername = config['OWNER_NAME']

        add_npc = f"""

        local ref = {{
            id = "{_id}",
            pos = vector.new{pos_vector},
            yaw = {yaw},
            name = "{modname}",
            owner = "{ownername}",
        }}
        npcf:add_npc(ref)

        """
        # time.sleep(3)

        # Testing if rob already exist 
        test_rob = """
        local e = npcf:get_luaentity( \"""" + _id + """\" )
            if e then
                return true
            else
                return false
            end
        """
        if  not self.mc.send_lua(test_rob) :
            print(self.mc.send_lua(add_npc))
            time.sleep(10)
        else :
            print("NPC already init")



    def build_lua(self,command):
        """
        The command will execute the command between :
            - The initializing part (access to the npc)
            - Executiong the command
            - closing the access 

        Name of variables : 
            - npc -> npc entity variables
            - move_obj -> npc's controller
        ---------------------------------------------------
        """

        cmd = """
            local npc = npcf:get_luaentity(\"""" + self.id + """\")
            local move_obj = npcf.movement.getControl(npc)
            """
        cmd = cmd + command
        print(cmd)
        return cmd

    def move_to(self,x,y,z):
        p = '{x='+ str(x) +', y='+ str(y) +', z='+str(z)+'}'
        cmd = """
            local player = minetest.get_player_by_name(npc.owner)
            move_obj:walk(move_obj,""" + str(p) + """,""" + str(self.speed) + """)
        """
        self.mc.send_lua(self.build_lua(cmd))
        

    def move_to_r(self,x,y,z):
        cmd = """
            local p = move_obj.pos
            local new_p = {x=p.x+ """+ str(x) +""",    y=p.y+"""+ str(y) +""",    z=p.z + """+ str(z) +"""} 
            move_obj:walk(move_obj,new_p,2)
        """
        self.mc.send_lua(self.build_lua(cmd))

    def get_position(self):
        cmd = """
            return move_obj.pos
        """
        print(self.mc.send_lua(self.build_lua(cmd)))


    def place(self,inv_id, x,y,z):
        # ignoring inv_id

        cmd = """
            return minetest.set_node({x=""" + str(x) + """, y=""" + str(y) + """, z=""" + str(z) + """}, {name="default:dry_dirt"})
        """

    def place_r(self,inv_id, x,y,z):
        cmd = """
            local p = move_obj.pos
            local new_p = {x=p.x+ """+ str(x) +""",    y=p.y+"""+ str(y) +""",    z=p.z + """+ str(z) +"""} 
            local block = {name="default:wood"}
            return minetest.add_node(new_p, block)
        """
        print(self.mc.send_lua(self.build_lua(cmd)))


    def break_node(self,inv_id, x,y,z):
        cmd = """
            minetest.dig_node({x=""" + str(x) + """, y=""" + str(y) + """, z=""" + str(z) + """}, {name="default:dirt"})
        """
        print(self.mc.send_lua(self.build_lua(cmd)))

    def break_node_r(self,inv_id, x,y,z):
        cmd = """
            local p = move_obj.pos
            local new_p = {x=p.x+ """+ str(x) +""",    y=p.y+"""+ str(y) +""",    z=p.z + """+ str(z) +"""} 
            return minetest.dig_node(new_p)
        """
        print(self.mc.send_lua(self.build_lua(cmd)))
        

    def join_owner(self):
        cmd = """
            local player = minetest.get_player_by_name(npc.owner)
            local p = player:get_pos()
            move_obj:walk(move_obj,p,""" + str(2) + """)
        """
        self.mc.send_lua(self.build_lua(cmd))

    def get_surrounding_nodes(self):
        cmd = """
            --local p = move_obj.pos
            local player = minetest.get_player_by_name(npc.owner)
            print(npc.owner)
            print(player.pos)
            local p = player:get_pos()

            print(p.x)
            print(p.y)

            print(p.z)

            p.y = p.y-3
            return minetest.get_node(p)
        """
        print(self.mc.send_lua(self.build_lua(cmd)))


    def look_to_owner(self):
        cmd = """
            local player = minetest.get_player_by_name(npc.owner)
            local p = player.pos
            move_obj:look_to(p)
        """
        self.mc.send_lua(self.build_lua(cmd))


    def mine(self):
        cmd = """
            move_obj:mine()
        """
        self.mc.send_lua(self.build_lua(cmd))
