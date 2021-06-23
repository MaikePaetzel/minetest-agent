# starts the mining animation
lua_mine = """
move_obj:mine()
"""

# stops the mining animation
lua_mine_stop = """
move_obj:mine_stop()
"""
# makes rob walk to the owner character
lua_come_here = """
local player = minetest.get_player_by_name(npc.owner)
local p = player:get_pos()
move_obj:walk(p, 2)
"""
