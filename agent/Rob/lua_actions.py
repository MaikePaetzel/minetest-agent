#####################_simple_commands_############################
# executable actions for the bot object
# stops the bot from doing anything
lua_stop = """
move_obj:mine_stop()
move_obj:stop()
return true
"""

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

# turns towards a position
# will need to be formatted
lua_turn = """
move_obj:look_to({target})
return true
"""

# places a block at the given position
# will need to be formatted
lua_place_block = """
local new_p = {target}
minetest.set_node(new_p, {{name="default:{block}"}})
return true
"""

# break block at the given position
# will need to be formatted
lua_break_block = """
local new_p = {target}
minetest.remove_node(new_p)
return true
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

if not move_obj._path or not move_obj._path[1] then
    return 2
end

local player = minetest.get_player_by_name(npc.owner)
local p = player:get_pos()
local n = vector.round(move_obj.pos)

if vector.distance(p, n) < distance then
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
local distance = 0.4 -- how close to get to new position

if not move_obj._path or not move_obj._path[1] then
    return 2
end

local p = {target}
local n = vector.round(move_obj.pos)

if vector.distance(p, n) < distance then
    return 1
else
    return 0
end
"""

#####################_auxiliary_functions_############################
# can be sent directly to the game
# to get values we need to complete other commands

# sets the sun to always be in the sky
lua_lock_daytime = """
local timer = 0
minetest.register_globalstep(function(dtime)
	timer = timer + dtime;
	if timer >= 5 then
		minetest.set_timeofday(0.7)
		timer = 0
	end
end)
"""

# initializes the bot to look north
# will need to be formatted
lua_init_compass = """
local npc = npcf:get_luaentity("{npc_id}")
local move_obj = npcf.movement.getControl(npc)
local north = npc.object:getpos()
north.x = north.x+1
move_obj:look_to(north)
"""

# flips the mining animation on/off
# will need to be formatted
lua_toggle_mining = """
local npc = npcf:get_luaentity("{npc_id}")
local move_obj = npcf.movement.getControl(npc)
if move_obj.is_mining then
    move_obj:mine_stop()
else
    move_obj:mine()
end
"""

# returns the current coordinates of bot object
# will need to be formatted
lua_get_position = """
local npc = npcf:get_luaentity("{npc_id}")
return npc.object:getpos()
"""

# returns the current coordinates of bot object
# will need to be formatted
lua_get_yaw = """
local npc = npcf:get_luaentity("{npc_id}")
return npc.object:getyaw()
"""

# returns true if the bot is currently moving
# will need to be formatted
lua_bot_moving = """
local npc = npcf:get_luaentity("{npc_id}")
local move_obj = npcf.movement.getControl(npc)
if not move_obj._path or not move_obj._path[1] then
    return false
end
return true
"""
