const inquirer = require("inquirer")


// Function to publish the video to the youtubeServer
const publishVideo = async (auth,channel) => {
	// Video details Prompt 
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

	//real video implementation
	try{
		await channel.publish("YOUTUBE", `${auth?.username+auth?.password}`, Buffer.from(JSON.stringify({
			"title":details?.title,
			"description":details?.description,
			//video
		})),{
			contentType:"application/json"
		})
	}catch(e){
		console.warn(e)
	}
}

// // Function to get views of the video from youtubeServer
// const getViews = (user,title,channel) => {
	
// }

// // Function to get my videos from youtubeServer
// const getVideos = (user,channel) => {
	
// }

// // Function to get all subscribers
// const getSubscribers = (user,channel) => {
	
// }

module.exports ={
	publishVideo,
	// getViews,
	// getVideos,
	// getSubscribers,
}
