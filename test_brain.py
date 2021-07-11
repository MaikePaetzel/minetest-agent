from agent.Rob.bot_brain import DummyBrain


rob = DummyBrain()

rob.bot.lua_runner.run("""
local npc = npcf:get_luaentity("default_npc")
local move_obj = npcf.movement.getControl(npc)
npc.get_closest_tree(npc)
""")