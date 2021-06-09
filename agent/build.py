
import shutil
from datetime import datetime
import os
from Rob import NPC
from Rob.Movement import AtomicAction
import time

### Copy mod file and place them in the right folder and run python file

# Creating temporary file & backup
os.mkdir('tmp') 
shutil.copytree('MineyNpcMod', 'tmp/MineyNpc')
shutil.copytree('npcf+miney', 'tmp/npcf+miney')
shutil.copytree('Rob', 'tmp/Rob')

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S
dt_string = now.strftime("%d-%m-%Y_%H:%M:%S")
shutil.make_archive("backup/bckp" + dt_string , "zip", "tmp")
shutil.rmtree('tmp')


# Moving mod to minetest mod section
shutil.rmtree('/home/owrel/.minetest/mods/npcf+miney')
shutil.copytree('npcf+miney', '/home/owrel/.minetest/mods/npcf+miney')

time.sleep(3)
npc = NPC.NpcController()
npc.create_npc()
npc.init_rob_brain()

AA = AtomicAction(npc.send_lua, 'default_npc')

move_f = AA.move_to(-205,10,-245)

npc.brain.addAction(move_f)


time.sleep(10)

move_f = AA.move_to(-210,10,-245)
npc.brain.addAction(move_f)