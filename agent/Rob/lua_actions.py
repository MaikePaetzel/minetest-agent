#####################_simple_commands_############################
# executable actions for the bot object
# starts the mining animation
lua_mine = """
move_obj:mine()
return true
"""

# stops the mining animation
lua_mine_stop = """
move_obj:mine_stop()
return true
"""

# flips the mining animation on/off
lua_toggle_mining = """
if move_obj:is_mining() then
    move_obj:mine_stop()
else
    move_obj:mine()
end
return true
"""

# turns towards a position
# will need to be formatted
lua_turn = """
move_obj:look_to({target})
return true
"""
# places a block at the highest 
lua_place_block = """
local p = move_obj.pos
local new_p = {target}
minetest.set_node(new_p, {{name="default:{block}"}})
return true
"""

#####################_auxiliary_functions_############################
# can be sent directly to the game
# to get values we need to complete other commands

# returns the current coordinates of bot object
# will need to be formatted
lua_get_position = """
local npc = npcf:get_luaentity("{npc_id}")
local move_obj = npcf.movement.getControl(npc)
local p = move_obj.pos
return p
"""

# returns the current coordinates of bot object
# will need to be formatted
lua_get_yaw = """
local npc = npcf:get_luaentity("{npc_id}")
local move_obj = npcf.movement.getControl(npc)
local sun_x = (move_obj.pos.x + 1)
local y = move_obj.pos.y
local z = move_obj.pos.z
local sun = {{x=sun_x, y=y, z=z}}
local yaw = npcf:get_face_direction(move_obj.pos, sun)
return yaw
"""

# returns the current node at pos
# will need to be formatted
lua_get_node = """
return minetest.get_node_or_nil({pos})
"""

#####################_commands_with_check_############################
# executable actions for the bot object
# makes rob walk to the owner character
lua_come_here = """
local speed = 2 -- walking speed

local player = minetest.get_player_by_name(npc.owner)
local p = player:get_pos()
move_obj:walk(p, speed)

return true
"""

lua_come_here_check = """
local distance = 2 -- how close to get to player

if move_obj._path == nil then
    return 2
end

local player = minetest.get_player_by_name(npc.owner)
local p = player:get_pos()
local n = vector.round(move_obj.pos) 

-- take euclidean distance
local d = ((p.x-n.x) ^ 2 + (p.z-n.z) ^ 2) ^ 0.5

if d < distance then
    return 1
else
    return 0
end
"""

# moves laterally towards a new position
# will need to be formatted
lua_move = """
local speed = 2 -- walking speed

local new_p = {target}
move_obj:walk(new_p, speed)

return true
"""

# will need to be formatted
lua_move_check = """
local distance = 0.25-- how close to get to new position

if move_obj._path == nil then
    return 2
end

local p = {target}
local n = vector.round(move_obj.pos)

-- take euclidean distance
local d = ((p.x-n.x) ^ 2 + (p.z-n.z) ^ 2) ^ 0.5

if d < distance then
    return 1
else
    return 0
end
"""