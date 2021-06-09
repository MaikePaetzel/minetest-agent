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
       self.object:setpos(p)
      end
      -- Always looking the owner
      move_obj:look_to(p)
    end
})
