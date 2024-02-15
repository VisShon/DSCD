const db = require("../database.js")

// Function to get previous notifications
const getNotifications = (user) => {
    // if(user)
	//     return db.users[user].notifications
}

// Function to subscribe a channel
const updateSubscription = async (user,youtuber,subscribe) => {
	if(!youtuber)
		return "INVALID_REQUEST"

	if(db.youtubers[youtuber]){
		switch (subscribe) {
			case true:{
				await db.users[user]?.subscriptions?.add(youtuber)
				let subscribers = db.youtubers[youtuber]?.subscribers
				db.youtubers[youtuber].subscribers = 1+subscribers
				console.log(`${user} SUBSCRIBED TO ${youtuber}`)
				break
			}
			case false:{
				await db.users[user]?.subscriptions?.remove(youtuber)
				let subscribers = db.youtubers[youtuber]?.subscribers
				db.youtubers[youtuber].subscribers = 1-subscribers
				console.log(`${user} UNSUBSCRIBED TO ${youtuber}`)
				break
			}
		}
		return "SUCCESS"
	}

	return "NOT_FOUND"
}

// Function to get all subscribed channels
const getSubscriptions = (user) => {
	if(!user)
		return "INVALID_REQUEST"

	if(db.users[user])
		return db.users[user]?.subscriptions

	return "NOT_FOUND"
}

// Function to get all channels
const getChannels = () => {
	return Object.values(db.youtubers)
}

// Function to search videos
const getVideos = (param) => {
	return  Object.values(db.videos)
			.filter(
				(item)=>item?.title?.includes(param)
			)
}

// Function to get all videos of a channel
const getChannelVideos = async (youtuber) => {
	if(!youtuber)
		return "INVALID_REQUEST"

	if(db.youtubers[youtuber]){
		const videoids = db.youtubers[youtuber]?.videos
		
		let videos = []

		await videoids?.forEach(
			(id)=>videos.push(db.videos[id])
		)

		return videos
	}

	return "NOT_FOUND"
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
	getNotifications,
	getSubscriptions,
	updateSubscription,
	getChannels,
	getChannelVideos,
	getVideos,
	getVideo,
}