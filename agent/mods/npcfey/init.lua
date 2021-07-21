-- NPCF mod + miney to controll npc with python

NPCF_DATADIR = minetest.get_worldpath().."/npc_data/"


-- Find the closest person as the ower
-- for key, value in minetest.get_authentication_handler():iterate() do
--   print(key)
--   print(value)
-- end



-- Registering the NPC
local ref = npcf:register_npc("npcfey:npc" ,{
    description = "Im Rob",
    textures = {"npcf_info_skin.png"},
    mesh = "npcf_tst.x",
    orientation = 1,
    var = {
        selected = "",
        nodelist = {},
        nodedata = {},
        last_pos = {},
    },
    walk_param = {
      find_path = true
    },
    stepheight = 1.1,
    inventory_image = "npcf_info_inv.png",
    on_activate = function(self)
      self.object:setvelocity({x=0, y=0, z=0})
      self.object:setacceleration({x=0, y=-10, z=0})
      self.properties = {textures = textures}
      self.object:set_properties(self.properties)
      self.npc_id = "rob"
      self.mo_printed = false
    end,
    on_rightclick = function(self, clicker)
          local name = clicker:get_player_name()
          if name == self.owner then
              npcf:show_formspec(name, self.npc_id, nil)
          end
      print(self)
    end,
    on_step = function(self,dtim)
      -- Get some initial variable
      local move_obj = npcf.movement.getControl(self)
        move_obj.pos = self.object:get_pos()
            local max_dist = 15
      local pos_rob = move_obj.pos
      local player = minetest.get_player_by_name(self.owner)
      local p = player:get_pos()
      -- print(p)
      p.y = p.y+1
      -- Not considering the high in the distance
      local distance = vector.distance(pos_rob, {x=p.x, y=pos_rob.y, z=p.z})
      -- print(distance)
      if distance > max_dist then
       print(self)
--        self.object:setpos(p)
      end
      -- Always looking the owner
--       move_obj:look_to(p)
    end,


    get_closest_tree = function(self)
      print(self)
      print('Finding a tree')
      local move_obj = npcf.movement.getControl(self)
      print(move_obj)
      local origin_point = move_obj.pos -- Actually the frist point here
      print(self.object:getpos())
      print("Begin point:")
      print(origin_point.x)
      print(origin_point.y) -- Won't change
      print(origin_point.z)


      local current_point = {x=0,y=origin_point.y,z=0}

      local radius = 5
      local further_min = -1
      local further_max = 1
      local tree_dist = {}
      for i=further_min,further_max do
        -- local node = minetest.get_node(pos)
        for j=further_min,further_max do
          print('Changing ')
          current_point.x = origin_point.x + i*radius*2
          current_point.z = origin_point.z + j*radius*2

          for chunk_x=current_point.x-radius,current_point.x+radius do
           for chunk_z=current_point.z-radius,current_point.z+radius do
            local node = minetest.get_node({x=chunk_x, y=current_point.y, z=chunk_z})
            print(node.name .. " at position " .. chunk_x, current_point.y,chunk_z )
            if node.name == "wool:red" then
              move_obj:walk({x=chunk_x, y=current_point.y, z=chunk_z}, 2)
              return
            end
           end
          end
          -- begin_point
        end
      end,

      get_orientation = function(self)
        return self.orientaion
      end,

      set_orientation = function(self, n_orien)
        -- TODO check if the orientation is right
        self.orientaion = n_orien


      end
    end
})