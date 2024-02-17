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

		for(user of db.youtubers[youtuber]?.subscribers) {
			console.log("hello")
			try{
				await channel.assertQueue(user, { durable: true })
				await channel.sendToQueue(
					user,
					Buffer.from(`${youtuber} uploaded new video:${title}`),
				)
			}
			catch(e){
				console.warn(e)
			}
		}

		return "SUCCESS"
	}

	return "NOT_FOUND"
}

// Function to get my videos from youtubeServer
const getYoutuberVideos = (youtuber) => {
	if(db.youtubers[youtuber]){
		const videoids = db.youtubers[youtuber]?.videos
		
		let videos = []

		if(videoids){
			videoids?.forEach(
				(id)=>videos.push(db.videos[id])
			)
		}

		return videos
	}
	return "NOT_FOUND"
}

// Function to get all subscribers
const getSubscribers = (youtuber) => {
	if(db.youtubers[youtuber]){
		const subscriberids = db.youtubers[youtuber]?.subscribers
		return subscriberids.size
	}
	return "NOT_FOUND"
}


module.exports ={
	publishVideo,
	getYoutuberVideos,
	getSubscribers,
}
