const db = require("../database.js")

// Function to subscribe a channel
const updateSubscription = async (user,youtuber,subscribe) => {
	if(!youtuber)
		return "INVALID_REQUEST"

	const youtuberid = Object.keys(db.youtubers)[youtuber]

	if(db.youtubers[youtuberid]){
		switch (subscribe) {
			case true:{
				await db.users[user]?.subscriptions?.add(youtuberid)
				await db.youtubers[youtuberid]?.subscribers?.add(user)
				console.log(`${user} SUBSCRIBED TO ${youtuberid}`)
				break
			}
			case false:{
				await db.users[user]?.subscriptions?.delete(youtuberid)
				await db.youtubers[youtuberid]?.subscribers?.delete(user)
				console.log(`${user} UNSUBSCRIBED TO ${youtuberid}`)
				break
			}
		}
		return "SUCCESS"
	}

	return "NOT_FOUND"
}

// Function to get all subscribed channels
const getSubscriptions = async (user) => {
	if(!user)
		return "INVALID_REQUEST"

	if(db.users[user]){
		let res = []

		await db.users[user]?.subscriptions?.forEach(id => {
			res.push({id,name:db.youtubers[id].username})
		})

		return res
	}

	return "NOT_FOUND"
}

// Function to get all channels
const getChannels = () => {
	
	let res = Object.keys(db.youtubers).map(yid => ({
		yid,
		username: db.youtubers[yid].username
	}))

	return res
}

// Function to search videos
const getVideos = (param) => {
	return  Object.values(db.videos)
			.filter(
				(item)=>item?.title?.includes(param)
			)
}


// Function to get video
const getVideo = (title) => {
	if(!title) 
		return "INVALID_REQUEST"

	if(db.videos[title])
		return db.videos[title]

	return "NOT_FOUND"
}


module.exports ={
	getSubscriptions,
	updateSubscription,
	getChannels,
	getVideos,
	getVideo,
}