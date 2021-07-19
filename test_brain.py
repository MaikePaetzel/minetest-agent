from agent.Rob.bot_brain import DemoBrain


rob = DemoBrain()

# rob.bot.lua_runner.run("""
# local npc = npcf:get_luaentity("default_npc")
# local move_obj = npcf.movement.getControl(npc)
# npc.get_closest_tree(npc)
# """)

# rob.PlaceBlock('dirt')
# rob.DestroyBlockPrecise(0)
rob.DestroyBlock(0)
