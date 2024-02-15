const amqp = require("amqplib")
const {
	getNotifications,
	getSubscriptions,
	updateSubscription,
	getChannels,
	getChannelVideos,
	getVideos,
	getVideo
} = require("./controllers/UserControllers.js")

const {
	publishVideo,
	getViews,
	getYoutuberVideos,
	getSubscribers,
} = require("./controllers/YoutuberController.js")

const {
	login
} = require("./controllers/AuthController.js")


let connection

//--------------------------- Setup -------------------------------------
const createConnection = async (url) => {
	try{
		connection = await amqp.connect(url,{})
		return channel = await connection.createChannel()

	}catch(e){
		console.warn(e)
	}
}

/*
	auth
	{
		"username":"vishnu",
		"password":"shon123"
	}

	updateSubscriptions
	{
		"user":"c51ffdea-c35a-44d2-9ca5-d78dc191a436",
		"youtuber":"aac8f5f2-8164-4eee-bfec-8c98f76a08d5",
		"subscription":true
	}

	getSubscriptions
	{
		"user":"c51ffdea-c35a-44d2-9ca5-d78dc191a436"
	}

	getChannels
	{
		"user":"c51ffdea-c35a-44d2-9ca5-d78dc191a436"
	}

	publishVideo
	{
		"youtuber":"c51ffdea-c35a-44d2-9ca5-d78dc191a436",
		"link":"link",
		"title":"video",
		"description":"first video"
	}

	getChannelVideos
	{
		"youtuber":"c51ffdea-c35a-44d2-9ca5-d78dc191a436",
	}
*/

//--------------------------- User Queue -------------------------------------
const consumeUserRequests = async (channel) => {
	try{
		await channel.consume(
			"USER_REQUESTS",
			async (message) => {
				if (message) {
					switch (message?.properties?.headers?.request) {

						case "auth":{
							const req = JSON.parse(message?.content)
							const res =  await login(
											"USER_REQUESTS",
											req.username,
											req.password,
										)
							console.log(res)
							break
						}


						case "getNotifications":
							
						case "getSubscriptions":{
							const req = JSON.parse(message?.content)
							const res = await getSubscriptions(req.user)
							console.log(res)
							break
						}

						case "updateSubscription":{
							const req = JSON.parse(message?.content)
							const res = await updateSubscription(
												req.user,
												req.youtuber,
												req.subscription
											)
							console.log(res)
							break
						}

						case "getChannels":{
							const res = getChannels()
							console.log(res)
							break
						}

						case "getChannelVideos":{
							const req = JSON.parse(message?.content)
							const res = await getChannelVideos(req.youtuber)
							console.log(res)
							break
						}

						case "getVideos":{
							const req = JSON.parse(message?.content)
							const res =  getVideos(req.params)
							console.log(res)
							break
						}

						case "getVideo":{
							const req = JSON.parse(message?.content)
							const res =  getVideo(req.title)
							console.log(res)
							break
						}
					}
				}
			},
			{ noAck: true }
		)

	}catch(e){
		console.warn(e)
	}
}

//--------------------------- Youtuber Queue -------------------------------------
const consumeYouTuberRequests = async (channel) => {
	try{
		await channel.consume(
			"YOUTUBER_REQUESTS",
			async (message) => {
				if (message) {
					switch (message?.properties?.headers?.request) {

						case "auth":{
							const req = JSON.parse(message?.content)
							const res =  await login(
											"YOUTUBER_REQUESTS",
											req.username,
											req.password,
										)
							console.log(res)
							break
						}

						case "publishVideo":{
							const req = JSON.parse(message?.content)
							const res =  await publishVideo(
											req.youtuber,
											req.link,
											req.title,
											req.description
										)
							console.log(res)
							break
						}

						case "getViews":{
							const req = JSON.parse(message?.content)
							const res =  await getViews(req.video)
							console.log(res)
							break
						}

						case "getYoutuberVideos":{
							const req = JSON.parse(message?.content)
							const res =  getYoutuberVideos(req.youtuber)
							console.log(res)
							break
						}

						case "getSubscribers":{
							const req = JSON.parse(message?.content)
							const res =  getSubscribers(req.youtuber)
							console.log(res)
							break
						}
					}

				}
			},
			{ noAck: true }
		)

	}catch(e){
		console.warn(e)
	}
}



(async () => {

	const channel = await createConnection("amqp://vishnu:shon123@localhost:5672")

	await channel.assertQueue("USER_REQUESTS", { durable: true })
	await channel.assertQueue("YOUTUBER_REQUESTS", { durable: true })

	await consumeUserRequests(channel)
	await consumeYouTuberRequests(channel)

	// setTimeout(async () => {
	// 	await channel.close()
	// 	await connection.close()
	// },5000)
})()