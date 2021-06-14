from Rob import AtomicAction

class DummyBrain:
    """
        Description :
        ----------
        This provisionary class builds scripted behaviours out of atomic actions.
        It is merely a test instance.
    """

    def __init__(self, controller):
        self.bot = controller
        
        #TODO: add a scripted test behaviour
        self.bot.add_action()
        self.bot.start_execution()

    #TODO: brain with retico interface
        