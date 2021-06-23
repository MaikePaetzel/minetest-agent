import miney
import atomic_actions as aa
import lua_actions as la
import bot_controller as bc

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
        most recent commands (aka the ones added last)
        will be executed first.
        """ 
        # TODO: generalize! replace hard scripted behaviour
        if request:
            self.bot.mt.time_of_day = 0.5
            chat = miney.Chat(self.bot.mt)
            chat.send_to_all('Request received')

            # TODO: synchronization
            # commands are be executed concurrently
            # each on its own thread in the game
            # but we want some of them to happen consecutively
            self.bot.add_action(self.mine_stop)
            self.bot.add_action(self.come_here)
            self.bot.add_action(self.mine)
            self.bot.start_execution()

    def init_atomic_actions(self):
        # TODO: add AAs from lua_actions.py programmatically into a list?
        # need to identify them clearly if we want to treat AAs
        # as as targets for Reinforcement Learning
        self.mine = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_mine)
        self.mine_stop = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_mine_stop)
        self.come_here = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_come_here)