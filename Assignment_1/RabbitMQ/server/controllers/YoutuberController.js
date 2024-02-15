const db = require("../database.js")
const { v4: uuidv4 } = require('uuid')


// Function to publish the video to the youtubeServer
const publishVideo = async (youtuber,link,title,description) => {

	if(db.youtubers[youtuber]){
		const id = uuidv4()
		
		db.videos[id] = {
			title,
			description,
			creator:youtuber,
			views:0,
			link,
		}

		db.youtubers[youtuber]?.videos?.add(id)
		console.log(`${youtuber} VIDEO UPLOADED`)
		return "SUCCESS"
	}

	return "NOT_FOUND"
}

// Function to get views of the video from youtubeServer
const getViews = (video) => {
	if(db.videos[video])
		return db.videos[video]?.views
	return "NOT_FOUND"
}

// Function to get my videos from youtubeServer
const getYoutuberVideos = (youtuber) => {
	if(db.youtubers[youtuber]){
		const videoids = db.youtubers[youtuber]?.videos
		
		let videos = []

		videoids?.forEach(
			(id)=>videos.push(db.videos[id])
		)

		return videos
	}
	return "NOT_FOUND"
}

// Function to get all subscribers
const getSubscribers = (youtuber) => {
	if(db.youtubers[youtuber]){
		const subscriberids = db.youtubers[youtuber]?.subscribers

		let subscribers = []

		subscriberids?.forEach(
			(id)=>subscribers.push(db.users[id])
		)

		return subscribers
	}
	return "NOT_FOUND"
}


module.exports ={
	publishVideo,
	getViews,
	getYoutuberVideos,
	getSubscribers,
}
