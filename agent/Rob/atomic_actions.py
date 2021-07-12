import time
import datetime
from enum import Enum
from threading import Condition, Thread
from concurrent import futures

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
    lua_result_check -  lua code to check whether lua_command has been executed ingame
                    if this is None the execution will always return after max_time
    check_every  -  timeout between result checks
    max_time     -  max time for lua_command to finish ingame
                    must be > 0.0
    """
    def __init__(self, lua_runner,
                npc_id,
                lua_command,
                lua_result_check=None,
                check_every=0.1,
                max_time=100.0):
                # TODO: add callbacks
                # on_cancel=None
                # on_success=None

        self.lua_runner = lua_runner
        # CAREFUL: multiline string must not be indented
        # indentation will carry over into lua execution
        lua_base = """
local npc = npcf:get_luaentity(\"""" + npc_id + """\")
local move_obj = npcf.movement.getControl(npc)
        """
        assert lua_command
        self.lua_command = lua_base + lua_command

        if lua_result_check:
            assert max_time > 0.0
            self.lua_result_check = lua_base + lua_result_check
        else:
            self.lua_result_check = None

        assert check_every > 0.0
        self.check_every = check_every

        assert max_time >= 0.0
        self.max_time = max_time

        # TODO: add callbacks
        # self.on_cancel = on_cancel
        # self.on_success = on_success

    def command_thread(self, condition):
        """
        Sends this lua snippet to be executed ingame
        then waits for the observer_thread to signal
        whether the execution has reached a final state.
        """
        condition.acquire()
        print(self.lua_command)
        print(f"Attempting execution at {datetime.datetime.now()}")
        self.lua_runner.run(self.lua_command)

        done = condition.wait(timeout=self.max_time if self.max_time > 0.0 else None)
        if not done:
            print(f"Execution timed out after {self.max_time} at {datetime.datetime.now()}")
        else:
            print(f"Finished execution at {datetime.datetime.now()}")
        condition.release()
        return done

    def observer_thread(self, condition):
        """
        Method to execute the result checks concurrently.
        Notifies the command_thread to awake upon completion.

        """
        result = None
        while True:
            result = self.lua_runner.run(self.lua_result_check, timeout=self.check_every)

            if not result or result == Result.RUNNING:
                print(f"Still running command at {datetime.datetime.now()}", end="\r")

            elif result == Result.SUCCESS:
                condition.acquire()
                print(f"Execution successful at {datetime.datetime.now()}", end="\r")
                condition.notify()
                condition.release()
                return result

            elif result == Result.FAIL:
                condition.acquire()
                print(f"Execution failed at {datetime.datetime.now()}", end="\r")
                condition.notify()
                condition.release()
                return result

            time.sleep(self.check_every)

    def __call__(self):
        """
        Makes objects of this class callable like a function.
        This means object() will be equivalent to object.__call__()
        """
        command_result = Result.RUNNING
        observer_result = None

        condition = Condition()
        # using a with statement to ensure threads are cleaned up promptly
        with futures.ThreadPoolExecutor(max_workers=2) as executor:
            observer_future = None
            command_future = executor.submit(self.command_thread, (condition))
            # TODO: if self.lua_result_check:
            observer_future = executor.submit(self.observer_thread, (condition))

            command_result = command_future.result() # false for TIMEOUT
            if self.lua_result_check:
                observer_result = observer_future.result() # 1 for SUCCESS or 2 for FAIL
        
        if not lua_result_check:
            return Result.SUCCESS

        if self.max_time and not command_result:
            return Result.TIMEOUT

        return observer_result
