from agent.Rob.bot_brain import DemoBrain


rob = DemoBrain()

rob.bot.lua_runner.run("""
local npc = npcf:get_luaentity("default_npc")
local move_obj = npcf.movement.getControl(npc)
move_obj.yaw = 1.8 + math.pi * 0.5
""")

# rob.PlaceBlock('dirt')
# rob.PlaceBlock('dirt')

# rob.PlaceBlock('dirt')
# rob.PlaceBlock('dirt')

# rob.DestroyBlockPrecise(0)
# rob.DestroyBlock(0)
