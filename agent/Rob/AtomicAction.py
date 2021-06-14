import time
import datetime

class Action:
    """
    This class holds lua code of atomic actions that a bot is able to execute.

    action : lua code to execute
    on_cancel: callback for user initiated cancellation
    on_fail: callback in case of an inexecutable action
    on_success: callback in case of a succesfully executed action

    """
    def __init__(self, action, cancel_condition, success_condition):
        self.action = action
        
        self.cancel_condition = cancel_condition
        self.success_condition = success_condition

        self.on_cancel = None
        self.on_success = None

        self.now = round(time.time() * 1000)



class AtomicAction(Action):
    """
    This class holds lua code of atomic actions that a bot is able to execute.

    action : lua code to execute
    on_cancel: callback for user initiated cancellation
    on_fail: callback in case of an inexecutable action
    on_success: callback in case of a succesfully executed action

    """
    def __init__(self, lua_runner, npc_id):
        self.lua_runner = lua_runner
        self.base_cmd = """
        local npc = npcf:get_luaentity(\"""" + npc_id + """\")
        local move_obj = npcf.movement.getControl(npc)
        """


    def build_lua(self, command):
        """
        A command consists of:
            - initialization (access to the npc)
            - executing the command
            - closing the access

        Name of variables : 
            - npc -> npc entity variables
            - move_obj -> npc's controller
        ---------------------------------------------------
        """
        print('Lua command executed at {datetime.datetime.now()}')
        
        cmd = self.base_cmd + command
        print (cmd)
        return self.lua_runner(cmd)


    def move_to(self, x, y, z):
        
        def action():

            p = '{x='+ str(x) +', y='+ str(y) +', z='+str(z)+'}'
            cmd = """
            local player = minetest.get_player_by_name(npc.owner)
            move_obj:walk(""" + str(p) + """,2)
            """
            return self.build_lua(cmd)

        def cancel_condition():
            
            cmd = """
            if move_obj._path == nil then
                return true
            else
                return false
            end
            """
            return self.build_lua(cmd)


        def on_cancel():
            print('The action has been canceled')
        
        def success_condition():
            p = '{x='+ str(x) +', y='+ str(y) +', z='+str(z)+'}'
            cmd = """
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


        def on_success(parent_action):
            print('The goal has been reached')

        a = Action(action, cancel_condition, success_condition)
        a.on_cancel = on_cancel
        a.on_success = on_success

        return a
