// Function to get all notifications
const receiveNotifications = async (auth,channel) => {
	try{
		await channel.consume(`${auth?.username+auth?.password}`, function(msg) {
			console.log(" [x] %s:'%s'", msg.fields.routingKey, msg.content.toString())
		}, {
			noAck: true
		})
	}catch(e){
		console.warn(e)
	}
}

// Function to subscribe a channel
const updateSubscription = async (user,youtuber,subscribe,channel) => {
	// Subscription Prompt 
	const details = await inquirer.prompt([
		{
			type: "input",
			name: "title",
			message: "Enter title:",
		},
		{
			type: "input",
			name: "description",
			message: "Enter description:",
		},
	])
	
}

// // Function to get all subscribed channels
// const getSubscribed = (user,channel) => {
	
// }

// Function to get all channels
const getChannels = (channel) => {
	
}

// // Function to search videos
// const getVideos = (title,channel) => {
	
// }

// // Function to get all videos of a channel
// const getChannelVideos = (youtuber,channel) => {
	
// }

// // Function to get video
// const getVideo = (title,channel) => {
	
// }

module.exports ={
	receiveNotifications,
	// getSubscribed,
	updateSubscription,
	getChannels,
	// getChannelVideos,
	// getVideos,
	// getVideo,
}
