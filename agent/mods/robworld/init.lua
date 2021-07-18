
minetest.register_chatcommand("rw", {
    params = params,
	description = "Rob world command",
	func = function(name, param)

        local param_a = {}
        local len = 0
        for token in string.gmatch(param, "[^%s]+") do
            param_a[len] = token    
            len = len + 1
        end
        if len > 0 then
            if param_a[0] == "init" then
                minetest.chat_send_all('Init')
                
                local can_continue = true
                for i= 1, 6 do
                    local function ToInteger(number)
                        if pcall(function() math.floor(tonumber(number)) end) then
                            return math.floor(tonumber(number))
                        else 
                            return 'a'
                        end
                    end
                    -- print(param_a[i] .." " .. i .. " " .. type(param_a[i]))
                    if type(ToInteger(param_a[i])) ~= type(1) then
                        can_continue = false
                    else
                        param_a[i] = math.floor(tonumber(param_a[i]))
                    end

                end
                if can_continue then

                    local pos_f = {x=0,z=0,y=0}
                    local pos_t = {x=0,z=0,y=0}

                    -- Ordering the position
                    if param_a[1] < param_a[4] then
                        pos_f['x'] = param_a[1]
                        pos_t['x'] = param_a[4]
                    else
                        pos_t['x'] = param_a[1]
                        pos_f['x'] = param_a[4]
                    end

                    if param_a[2] < param_a[5] then
                        pos_f['y'] = param_a[2]
                        pos_t['y'] = param_a[5]
                    else
                        pos_t['y'] = param_a[2]
                        pos_f['y'] = param_a[5]
                    end

                    if param_a[3] < param_a[6] then
                        pos_f['z'] = param_a[3]
                        pos_t['z'] = param_a[6]
                    else
                        pos_t['z'] = param_a[3]
                        pos_f['z'] = param_a[6]
                    end

                    -- Debug output
                    print('From pos')
                    print(pos_f['x'])
                    print(pos_f['y'])
                    print(pos_f['z'])
                    print('To pos')
                    print(pos_t['x'])
                    print(pos_t['y'])
                    print(pos_t['z'])

                    -- print(minetest.registered_nodes['default:dirt'])

                    for x = pos_f['x'],pos_t['x'] do
                        for y = pos_f['y'],pos_t['y'] do
                            for z = pos_f['z'],pos_t['z'] do
                                local new_pos = {x=x,y=y,z=z}
                                minetest.remove_node(new_pos)
                                if x == pos_f['x'] or x == pos_t['x'] or z == pos_f['z'] or z == pos_t['z'] then  
                                    minetest.set_node(new_pos, minetest.registered_nodes['default:obsidian_glass'])
                                end

                                if y == pos_f['y'] then 
                                    minetest.set_node(new_pos, minetest.registered_nodes['default:dirt_with_grass'])
                                end

                                if y == pos_t['y'] then 
                                    minetest.set_node(new_pos, minetest.registered_nodes['default:obsidian_glass'])
                                end


                            end
                        end
                    end
                    

                    -- Prepare the terrain to teleport player here
                    for x = pos_f['x'],pos_t['x'] do
                        for y = pos_t['y']+1,pos_t['y']+5 do
                            for z = pos_f['z'],pos_t['z'] do
                                local new_pos = {x=x,y=y,z=z}
                                minetest.remove_node(new_pos)
                            end
                        end
                    end


                    -- Teleport the player and rob
                    local player = minetest.get_player_by_name(name)
                    player:set_pos({x=pos_f['x']+2,y=pos_t['y']+2,z=pos_f['z']+2})

                    local var = "hello"
                    local npc = npcf:get_luaentity('default_npc')
                    print(npc)
                    local move_obj = npcf.movement.getControl(npc)
                    npc.object:setpos({x=pos_f['x']+4,y=pos_f['y']+2,z=pos_f['z']+4})


                else 
                    minetest.chat_send_all("Wrong init parameter waiting for <x> <y> <z> <x'> <y'> <z'> ")
                end
                

                
            elseif  param_a[0] == "initr" then
            else
                minetest.chat_send_all('Wrong parameters')
            end
        else
            minetest.chat_send_all('Type "rw help" to get the help')
        end
    end
})
