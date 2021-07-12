#        self.lua_code = """
# local npc = npcf:get_luaentity(\"""" + npc_id + """\")
# local move_obj = npcf.movement.getControl(npc)
#         """
#
#
#
#  starts the mining animation



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

#####################_lua_checks_############################
# a check has to return:
# 0 if the command it is observing is still being executed
# 1 if the command has reached a success state
# 2 if the command has failed to execute properly

lua_come_here_check = """
if move_obj._path == nil then
    return 2
end

local player = minetest.get_player_by_name(npc.owner)
local p = player:get_pos()
local n = vector.round(move_obj.pos)

local d = (p.y - n.y) * (p.y - n.y)

if d < 3 and p.z == n.z  then
    return 1
else
    return 0
end
"""
