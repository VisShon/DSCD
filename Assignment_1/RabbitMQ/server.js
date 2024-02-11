const amqp = require("amqplib")
let connection

// Methods:

// -consume_user_requests()

// Starts consuming Login and Subscription/Unsubscription Requests from Users.
// Prints “<username> logged in” whenever a user logs in
// Prints “<username> <subscibed/ubsubscribed> to <youtuberName>”  whenever a user updates their subscriptions.

// -consume_youtuber_requests()

// Starts consuming video upload requests from YouTubers.
// Prints “<YouTuberName> uploaded <videoName>” whenever a YouTuber uploads a new video.

// -notify_users()

// Sends notifications to all users whenever a YouTuber they subscribe to uploads a new video.

//--------------------------- Setup -------------------------------------
const createConnection = async (url) => {
	try{
		connection = await amqp.connect(url,{})
		return channel = await connection.createChannel()

	}catch(e){
		console.warn(e)
	}
}

//--------------------------- Publish Video -------------------------------------
const publishVideo = async (channel,key,video) => {

}


(async () => {

	const channel = await createConnection("amqp://vishnu:shon123@localhost:5672")
	await channel.assertExchange("YOUTUBE", "topic", {
		durable: false //change to true in production
	})
	
	

	setTimeout(async () => {
		await channel.close()
		await connection.close()
	},5000)
})()


// Function to publish the video to the youtubeServer
// Function to get views of the video from youtubeServer
// Function to get my videos from youtubeServer
// Function to get all subscribers
// Function to get all notifications
// Function to get all subscribed channels
// Function to get all channels
// Function to subscribe a channel
// Function to search videos
// Function to get all videos of a channel
// Function to get video