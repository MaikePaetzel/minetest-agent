import time
import datetime
import miney
import logging as log
from enum import Enum

class Result(Enum):
    RUNNING = 0
    SUCCESS = 1
    FAIL = 2
    TIMEOUT = 3

class AtomicAction:
    """
    This class holds lua code of atomic actions that a bot is able to execute.
    It can be run by calling class objects like a function.

    lua_runner   -  sends lua code off to be executed ingame
    npc_id       -  npc that is supposed to execute the command
    lua_command  -  behaviour to be executed
    max_time     -  max time for lua_command to finish ingame
                    must be > 0.0
    lua_check    -  lua code to check whether game state eventually changed as expected
                    if this is None the execution will return after max_time
    check_pause  -  pause between result checks
    """
    def __init__(self,
                lua_runner,
                npc_id,
                lua_command,
                max_time = 1.0,
                lua_check = False,
                check_pause = 0.5):

        self.lua_runner = lua_runner

        # CAREFUL: multiline string must not be indented
        # indentation will carry over into lua execution
        LUA_BASE = """
local npc = npcf:get_luaentity(\"""" + npc_id + """\")
local move_obj = npcf.movement.getControl(npc)
        """
        assert lua_command
        self.lua_command = LUA_BASE + lua_command

        if lua_check:
            self.lua_check = LUA_BASE + lua_check
            assert check_pause > 0.0
            self.check_pause = check_pause

        if max_time:
            assert max_time >= 0.0
            self.max_time = max_time

    def run_checks(self):
        """
        Sends this lua snippet to be executed ingame
        """
        print(self.lua_check)
        print(f"Commencing result checks at {datetime.datetime.now()}")
        result = None
        while not result:
            try:
                result = self.lua_runner.run(self.lua_check)
            except miney.LuaResultTimeout:
                log.exception(f"Result check timed out after {self.max_time}s at {datetime.datetime.now()}")
                return 3
            print(f"Check produced: {result}")
            if result != 0:
                return result
            time.sleep(self.check_pause)

    def run_command(self):
        """
        Sends this lua snippet to be executed ingame
        """
        print(self.lua_command)
        print(f"Attempting execution at {datetime.datetime.now()}")
        try:
             self.lua_runner.run(self.lua_command, timeout=self.max_time if self.max_time > 0 else None)
        except miney.LuaResultTimeout:
            log.exception(f"Execution timed out after {self.max_time}s at {datetime.datetime.now()}")
            return False
        print(f"Finished execution at {datetime.datetime.now()}")
        return True

    def __call__(self):
        """
        Makes objects of this class callable like a function.
        This means object() will be equivalent to object.__call__()
        """
        timeout = not self.run_command()
        if timeout:
            return Result.TIMEOUT

        try:
            if self.lua_check:
                result = self.run_checks()
                if result == 1:
                    return Result.SUCCESS
                else:
                    return Result.FAIL
        except:
            pass
        return Result.SUCCESS
