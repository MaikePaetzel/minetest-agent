from Rob.Action import Action
import datetime

class AtomicAction :
    def __init__(self, lua_runner, npc_id):
        self.lua_runner = lua_runner
        self.npc_id = npc_id


    def build_lua(self, command):
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
        print(f'Lua command executed at {datetime.datetime.now()}')
        cmd = """
    local npc = npcf:get_luaentity(\"""" + self.npc_id + """\")
    local move_obj = npcf.movement.getControl(npc)
        """
        cmd = cmd + command
        print (cmd)
        return self.lua_runner(cmd)



    def move_to(self, x,y,z):
        
        def codeInnerFunction(parent_action):

            p = '{x='+ str(x) +', y='+ str(y) +', z='+str(z)+'}'
            cmd = """
    local player = minetest.get_player_by_name(npc.owner)
    move_obj:walk(""" + str(p) + """,2)
            """
            return self.build_lua(cmd)

        def cancelInnerFunction(parent_action):
            
            cmd = """

    if move_obj._path == nil then
        return true
    else
        return false
    end
            """
            ret = self.build_lua(cmd)
            return ret


        def on_cancelInnerFunction(parent_action):
            print('The walk have been canceld')
        
        def goalInnerFunction(parent_action):
            p = '{x='+ str(x) +', y='+ str(y) +', z='+str(z)+'}'
            cmd = f"""
    p = vector.round({p})
    n = vector.round(move_obj.pos) 

    d = (p.y - n.y) * (p.y - n.y)

    if p.x == n.x and d < 3 and p.z == n.z  then
        return true
    else
        return false
    end
            """
            ret= self.build_lua(cmd)
            return ret


        def on_goalInnerFunction(parent_action):
            print('The goal have beean reached')

        a = Action(codeInnerFunction, cancelInnerFunction, goalInnerFunction)
        a.set_on_cancel(on_cancelInnerFunction)
        a.set_on_goal(on_goalInnerFunction)

        return a

    

# def move_to_r(self,x,y,z):
#     cmd = """
#         local p = move_obj.pos
#         local new_p = {x=p.x+ """+ str(x) +""",    y=p.y+"""+ str(y) +""",    z=p.z + """+ str(z) +"""} 
#         move_obj:walk(move_obj,new_p,2)
#     """
#     self.mc.send_lua(self.build_lua(cmd))

# def get_position(self):
#     cmd = """
#         return move_obj.pos
#     """
#     print(self.mc.send_lua(self.build_lua(cmd)))


# def place(self,inv_id, x,y,z):
#     # ignoring inv_id

#     cmd = """
#         return minetest.set_node({x=""" + str(x) + """, y=""" + str(y) + """, z=""" + str(z) + """}, {name="default:dry_dirt"})
#     """

# def place_r(self,inv_id, x,y,z):
#     cmd = """
#         local p = move_obj.pos
#         local new_p = {x=p.x+ """+ str(x) +""",    y=p.y+"""+ str(y) +""",    z=p.z + """+ str(z) +"""} 
#         local block = {name="default:wood"}
#         return minetest.add_node(new_p, block)
#     """
#     print(self.mc.send_lua(self.build_lua(cmd)))


# def break_node(self,inv_id, x,y,z):
#     cmd = """
#         minetest.dig_node({x=""" + str(x) + """, y=""" + str(y) + """, z=""" + str(z) + """}, {name="default:dirt"})
#     """
#     print(self.mc.send_lua(self.build_lua(cmd)))

# def break_node_r(self,inv_id, x,y,z):
#     cmd = """
#         local p = move_obj.pos
#         local new_p = {x=p.x+ """+ str(x) +""",    y=p.y+"""+ str(y) +""",    z=p.z + """+ str(z) +"""} 
#         return minetest.dig_node(new_p)
#     """
#     print(self.mc.send_lua(self.build_lua(cmd)))
    

# def join_owner(self):
#     cmd = """
#         local player = minetest.get_player_by_name(npc.owner)
#         local p = player:get_pos()
#         move_obj:walk(move_obj,p,""" + str(2) + """)
#     """
#     self.mc.send_lua(self.build_lua(cmd))

# def get_surrounding_nodes(self):
#     cmd = """
#         --local p = move_obj.pos
#         local player = minetest.get_player_by_name(npc.owner)
#         print(npc.owner)
#         print(player.pos)
#         local p = player:get_pos()

#         print(p.x)
#         print(p.y)

#         print(p.z)

#         p.y = p.y-3
#         return minetest.get_node(p)
#     """
#     print(self.mc.send_lua(self.build_lua(cmd)))


# def look_to_owner(self):
#     cmd = """
#         local player = minetest.get_player_by_name(npc.owner)
#         local p = player.pos
#         move_obj:look_to(p)
#     """
#     self.mc.send_lua(self.build_lua(cmd))


# def mine(self):
#     cmd = """
#         move_obj:mine()
#     """
#     self.mc.send_lua(self.build_lua(cmd))
