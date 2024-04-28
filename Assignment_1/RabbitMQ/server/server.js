// #region ------------------- Setup -----------------------------------

const amqp = require("amqplib")
const {
	getSubscriptions,
	updateSubscription,
	getChannels,
	getVideos,
	getVideo
} = require("./controllers/UserControllers.js")

const {
	publishVideo,
	getYoutuberVideos,
	getSubscribers,
} = require("./controllers/YoutuberController.js")

const {
	login
} = require("./controllers/AuthController.js")



let connection

const createConnection = async (url) => {
	try{
		connection = await amqp.connect(url,{})
		return channel = await connection.createChannel()

	}catch(e){
		console.warn(e)
	}
}

// #endregion

// #region ------------------- Helper Function -------------------------

// response logic
const response = async (channel,replyTo, correlationId, data) => {
	try{
		await channel.sendToQueue(replyTo,
			Buffer.from(JSON.stringify(data)),
			{
				correlationId
			}
		)
		return true
	}catch(e){
		console.log("Error")
		console.warn(e)
	}
}

// User Queue
const consumeUserRequests = async (channel) => {
	try{
		channel.prefetch(1)
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

							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
							break
						}
							
						case "getSubscriptions":{
							const req = JSON.parse(message?.content)
							const res = await getSubscriptions(req.user)

							console.log(res)

							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)

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

							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)

							console.log(res)
							break
						}

						case "getChannels":{
							const res = await getChannels()
							console.log(res)
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
							break
						}

						case "getVideos":{
							const req = JSON.parse(message?.content)
							const res =  getVideos(req.params)
							console.log(res)
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
							break
						}

						case "getVideo":{
							const req = JSON.parse(message?.content)
							const res =  getVideo(req.index)
							console.log(res)
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
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

// Youtuber Queue
const consumeYouTuberRequests = async (channel) => {
	try{
		channel.prefetch(1)
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
							
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
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
							
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
							break
						}

						case "getYoutuberVideos":{
							const req = JSON.parse(message?.content)
							const res =  getYoutuberVideos(req.youtuber)
							
							console.log(res)
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
							break
						}

						case "getSubscribers":{
							const req = JSON.parse(message?.content)
							const res =  getSubscribers(req.youtuber)
							
							console.log(res)
							await response(
								channel,
								message.properties?.replyTo,
								message.properties?.correlationId,
								res
							)
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

// #endregion


(async () => {

	const channel = await createConnection("amqp://vishnu:shon123@34.131.141.142:5672")

	await channel.assertQueue("USER_REQUESTS", { durable: true })
	await channel.assertQueue("YOUTUBER_REQUESTS", { durable: true })

	await consumeUserRequests(channel)
	await consumeYouTuberRequests(channel)

})()
