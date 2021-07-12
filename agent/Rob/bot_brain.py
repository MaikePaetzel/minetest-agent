import miney
import agent.Rob.atomic_actions as aa
import agent.Rob.lua_actions as la
import agent.Rob.bot_controller as bc

class DummyBrain:
    """
        Description :
        ----------
        This provisionary class builds scripted behaviours out of atomic actions.
        It is merely a test instance.
    """

    def __init__(self, controller=bc.BotController()):
        self.bot = controller

        # create callables with lua commands that the bot can execute
        self.init_atomic_actions()

    def process(self, request):
        """
        Behaviours are executed from stack meaning
        most recent commands (aka the last ones added)
        will be executed first.
        """
        if request:
            self.bot.mt.time_of_day = 0.5
            chat = miney.Chat(self.bot.mt)
            chat.send_to_all('Request received')
            self.bot.add_action(self.mine)
            # self.bot.add_action(self.come_here)
            self.bot.start_execution()

    def init_atomic_actions(self):
        # TODO: add AAs from lua_actions.py programmatically into a list?
        self.mine = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_mine, la.lua_generic_check)
        self.mine_stop = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_mine_stop)
        self.come_here = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_come_here, la.lua_come_here_check, 0.5)
