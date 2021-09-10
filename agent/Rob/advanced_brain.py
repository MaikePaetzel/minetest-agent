import simple_brain as sb
import bot_controller as bc
import lua_actions as la
import time
import math

class AdvancedBrain(sb.SimpleBrain):
    def __init__(self, controller=bc.BotController()):
        super().__init__(controller=controller)

    #################################################
    # Complex Behaviours
    #################################################

    def PlaceMultipleBlocks(self, type, count):
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        for _ in range(count):
            self.PlaceBlock(type=type)
            time.sleep(0.25)
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.25)

    #################################################

    def BuildWall(self, width=1, height=2, type='default:stonebrick'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(width):
            self.PlaceMultipleBlocks(type, height)
            if i < width-1:
                self.Move(direction='right', distance=1)
                time.sleep(0.25)
                self.Turn(direction='left')
            
    #################################################
    
    def MakeDoor(self):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        dx, dz = self.orientation_2_deltas(self.orientation.value)

        # find the floor block in front of the bot
        bot_pos = self.get_bot_position()
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : bot_pos['y'] - 1.0, # bot head
            'z' : bot_pos['z'] + dz
            }

        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.25)
        self.bot.mt.node.set(target_pos, 'air')
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.25)
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        target_pos['y'] += 1.0
        time.sleep(0.25)
        self.bot.mt.node.set(target_pos, 'air')
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        
    #################################################

    def MakeWindow(self):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        dx, dz = self.orientation_2_deltas(self.orientation.value)

        # find the floor block in front of the bot
        bot_pos = self.get_bot_position()
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : bot_pos['y'], # bot face
            'z' : bot_pos['z'] + dz
            }

        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.5)
        self.bot.mt.node.set(target_pos, 'air')
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        
    #################################################

    def BuildStairs(self, height=2, type='stairs:slab_stone'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(2*height): # working in half steps
            j = math.ceil(i / 2)
            if j > 0:
                self.PlaceMultipleBlocks('default:stonebrick', j)
            if i % 2 == 0:
                self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
                time.sleep(0.25)
                self.PlaceBlock(type=type)
                self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
            self.Move(direction='forward', distance=1)
            time.sleep(0.1)
        
    #################################################

    def PlaceRoofTiles(self, type, count):
        dx, dz = self.orientation_2_deltas(self.orientation.value)
        
        # find the floor block in front of the bot
        bot_pos = self.get_bot_position()
        target_pos = {
            'x' : bot_pos['x'] + dx,
            'y' : bot_pos['y'] + 2.0, # above the bots head
            'z' : bot_pos['z'] + dz
            }
        # find the highest position to place a new block
        for _ in range(count):
            self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
            time.sleep(0.1)
            self.bot.mt.node.set(target_pos, str(type))
            target_pos['x'] -= dx
            target_pos['y'] += 1.0
            target_pos['z'] -= dz
            self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
            time.sleep(0.1)

    def BuildRoof(self, width=2, height=3, type='default:wood'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(width):
            self.PlaceRoofTiles(type, height)
            if i < width-1:
                self.Move(direction='right', distance=1)
                time.sleep(0.25)
                self.Turn(direction='left')

    #################################################

    def BuildFloor(self, width=2, type='default:cobble'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(width):
            self.DestroyBlock(height=1)
            time.sleep(0.25)
            self.PlaceBlock(type)
            if i < width-1:
                self.Move(direction='right', distance=1)
                time.sleep(0.25)
                self.Turn(direction='left')