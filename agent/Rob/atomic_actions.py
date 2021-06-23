import datetime

class AtomicAction:
    """
    This class holds lua code of atomic actions that a bot is able to execute.
    It can be executed by calling class objects like a function.
    """
    def __init__(self, lua_runner, npc_id, lua_command):
        # TODO: reimplement callbacks
        # self.cancel_condition = cancel_condition
        # self.success_condition = success_condition
        # self.on_cancel = None
        # self.on_success = None

        self.lua_runner = lua_runner
        # CAREFUL: multiline string must not be indented
        # indentation will carry over into lua execution
        self.lua_code = """
local npc = npcf:get_luaentity(\"""" + npc_id + """\")
local move_obj = npcf.movement.getControl(npc)
        """
        # TODO: assert lua_command not empty
        self.lua_code += lua_command

    # TODO: add *args, e.g. timeout
    def __call__(self):
        """
        Makes objects of this class callable like a function.
        This means

        object()

        will be equivalent to

        object.__call__()
        """
        print(self.lua_code)
        print(f"attempted execution at {datetime.datetime.now()}")

        return self.lua_runner.run(self.lua_code, timeout=10.0)
