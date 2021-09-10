import bot_brain as b
import atomic_actions as aa
import bot_controller as bc
import lua_actions as la
import time

class SimpleBrain(b.Brain):
    def __init__(self, controller=bc.BotController()):
        super().__init__(controller=controller)

    #################################################
    # Simple Behaviours
    #################################################

    def Stop(self):
        stop_action = aa.AtomicAction(self.bot.lua_runner, self.bot.id, la.lua_stop)

        self.bot.add_action(stop_action)
        self.bot.start_execution()

    #################################################

    def Move(self, direction, distance):
        d = 0
        if direction == "left": # 90° counter-clockwise
            d = -1
        elif direction == "right": # 90° clockwise
            d = 1
        elif direction == "backward": # 180° clockwise
            d = 2

        # update the brains orientation and get deltas
        new_orientation = (self.orientation.value + d) % 4
        self.orientation = self.Compass(new_orientation)
        d_x, d_z = self.orientation_2_deltas(new_orientation)

        # build the move action
        bot_pos = self.get_bot_position()
        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=round(bot_pos['x'] + d_x * distance),
            y=bot_pos['y'],
            z=round(bot_pos['z'] + d_z * distance))
        move = la.lua_move.format(target=lua_target_pos)

        move_action = aa.AtomicAction(
            self.bot.lua_runner,
            self.bot.id,
            move)
            
        self.bot.add_action(move_action)
        self.bot.start_execution()

    #################################################

    def Turn(self, direction):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot perform a turn')

        d = 0
        if direction == "left": # 90° counter-clockwise
            d = -1
        elif direction == "right": # 90° clockwise
            d = 1
        elif direction == "backward": # 180° clockwise
            d = 2
        
        # update the brains orientation and get deltas
        new_orientation = (self.orientation.value + d) % 4
        self.orientation = self.Compass(new_orientation)
        d_x, d_z = self.orientation_2_deltas(new_orientation)

        # update the bots ingame orientation
        bot_pos = self.get_bot_position()
        lua_target_pos = "{{x={x}, y={y}, z={z}}}".format(
            x=bot_pos['x'] + d_x,
            y=bot_pos['y'],
            z=bot_pos['z'] + d_z)
        
        turn = la.lua_turn.format(target=lua_target_pos)
        turn_action = aa.AtomicAction(self.bot.lua_runner, self.bot.id, turn)

        self.bot.add_action(turn_action)
        self.bot.start_execution()

    #################################################

    def ComeHere(self):
        come = aa.AtomicAction(
            self.bot.lua_runner,
            self.bot.id,
            la.lua_come_here,
            60.0,
            la.lua_come_here_check,
            0.5)

        self.bot.add_action(come)
        self.bot.start_execution()

    #################################################

    def PlaceBlock(self, type):
        dx, dz = self.orientation_2_deltas(self.orientation.value)
        
        SEA_LEVEL = 6.5
        # find the floor block in front of the bot
        bot_pos = self.get_bot_position()
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : SEA_LEVEL,
            'z' : bot_pos['z'] + dz
            }
        # find the highest position to place a new block
        check_node = self.bot.mt.node.get(target_pos)
        while check_node['name'] != 'air':
            target_pos['y'] += 1.0
            check_node = self.bot.mt.node.get(target_pos)
        
        # make it look like rob is mining
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.25)
        self.bot.mt.node.set(target_pos, str(type))
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))

    #################################################
    
    def DestroyBlock(self, height=0):
        dx, dz = self.orientation_2_deltas(self.orientation.value)

        # find floor block in front of bot
        SEA_LEVEL = 6.5
        bot_pos = self.get_bot_position()
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : SEA_LEVEL,
            'z' : bot_pos['z'] + dz
            }

        if height: # find block at specified height
            target_pos['y'] += height
        else: # find the highest block to destroy
            check_node = self.bot.mt.node.get(target_pos)
            while check_node['name'] != 'air':
                target_pos['y'] += 1.0
                check_node = self.bot.mt.node.get(target_pos)
            target_pos['y'] -= 1.0

        # make it look like rob is mining
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.25)
        self.bot.mt.node.set(target_pos, 'air')
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))