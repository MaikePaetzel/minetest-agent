import simple_brain as sb
import bot_controller as bc
import lua_actions as la
import time
import math


# Word to number intent
def text2int(textnum, numwords={}):
    if not numwords:
        units = [
            "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
            "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
            "sixteen", "seventeen", "eighteen", "nineteen",
        ]

        tens = ["", "", "twenty", "thirty", "forty",
                "fifty", "sixty", "seventy", "eighty", "ninety"]

        scales = ["hundred", "thousand", "million", "billion", "trillion"]

        numwords["and"] = (1, 0)
        for idx, word in enumerate(units):
            numwords[word] = (1, idx)
        for idx, word in enumerate(tens):
            numwords[word] = (1, idx * 10)
        for idx, word in enumerate(scales):
            numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
            raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current

class AdvancedBrain(sb.SimpleBrain):
    def __init__(self, controller=bc.BotController()):
        super().__init__(controller=controller)

    #################################################
    # Complex Behaviours
    #################################################

    def place_multiple_blocks(self, type, count):
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        for _ in range(count):
            self.place_block(type=type)
            time.sleep(0.25)
        self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
        time.sleep(0.25)

    #################################################

    def build_wall(self, width=1, height=2, type='default:stonebrick'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        w = text2int(width)
        h = text2int(height)

        for i in range(w):
            self.place_multiple_blocks(type, h)
            if i < w-1:
                self.move(direction='right', distance=1)
                time.sleep(0.25)
                self.turn(direction='left')
            
    #################################################
    
    def make_door(self):
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

    def make_window(self):
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

    def build_stairs(self, height=2, type='stairs:slab_stone'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(2 * height): # working in half steps
            j = math.ceil(i / 2)
            if j > 0:
                self.PlaceMultipleBlocks('default:stonebrick', j)
            if i % 2 == 0:
                self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
                time.sleep(0.25)
                self.place_block(type=type)
                self.run_lua(la.lua_toggle_mining.format(npc_id=self.bot.id))
            self.move(direction='forward', distance=1)
            time.sleep(0.1)
        
    #################################################

    def place_roof_tiles(self, type, count):
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

    def build_roof(self, width=2, height=3, type='default:wood'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(width):
            self.place_roof_tiles(type, height)
            if i < width-1:
                self.move(direction='right', distance=1)
                time.sleep(0.25)
                self.turn(direction='left')

    #################################################

    def build_floor(self, width=2, type='default:cobble'):
        if self.run_lua(la.lua_bot_moving.format(npc_id=self.bot.id)):
            raise Exception('Bot is currently moving and cannot build.')

        for i in range(width):
            self.destroy_block(height=1)
            time.sleep(0.25)
            self.place_block(type)
            if i < width-1:
                self.move(direction='right', distance=1)
                time.sleep(0.25)
                self.turn(direction='left')