const db = require("../database.js")
const { v4: uuidv4 } = require('uuid')


const login = (type,username,password) => {

	if(!username)
		return "INVALID_USERNAME"

	if(!password)
		return "INVALID_PASSWORD"


	switch (type) {
		case "USER_REQUESTS":
			let uid

			let userExist = Object.values(db.users)?.findIndex(
				(item)=>item?.password===password&&item?.username===username)

			uid = Object.keys(db.users)[userExist]

			if(uid)
				return uid

			console.log("ADDING NEW USER")
			// uid = uuidv4()
			uid="c51ffdea-c35a-44d2-9ca5-d78dc191a436"
			db.users[uid] = {
				username:username,
				password:password,
				notification: new Set(),
				subscriptions: new Set(),
			}

			console.log("SUCCESS")
			return uid

		case "YOUTUBER_REQUESTS":
			let yid
			
			let youtuberExist = Object.values(db.youtubers)?.findIndex(
				(item)=>item?.password===password&&item?.username===username)
			yid = Object.keys(db.youtubers)[youtuberExist]

			if(yid)
				return yid

			console.log("ADDING NEW YOUTUBER")
			// yid = uuidv4()
			yid="aac8f5f2-8164-4eee-bfec-8c98f76a08d5"
			db.youtubers[yid] = {
				username:username,
				password:password,
				subscribers: 0,
				videos: new Set(),
			}
			console.log("SUCCESS")
			return yid
	}

	return "INVALID_REQUEST"

}


module.exports = {
    login,
}