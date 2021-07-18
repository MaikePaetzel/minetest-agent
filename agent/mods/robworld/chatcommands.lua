minetest.register_chatcommand("rw", {
    params = params,
	description = "Rob world command",
	func = function(name, param)
        minetest.chat_send_all('hello world')
    end
}
