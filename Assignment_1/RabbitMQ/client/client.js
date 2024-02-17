// #region --------------------------- Setup --------------------------------------------

const inquirer = require("inquirer")
const chalk = require("chalk")
const figlet = require("figlet")
const amqp = require("amqplib")
const { v4: uuidv4 } = require('uuid')
const { spawn } = require('child_process');
const axios = require('axios')
const fs = require('fs')

let connection = null
const correlationId = uuidv4()
let replyQueue = ''

const createConnection = async (url) => {
	try{
		connection = await amqp.connect(url,{})
		return channel = await connection.createChannel()

	}catch(e){
		console.warn(e)
	}
}
// #endregion

// #region --------------------------- Display Home -------------------------------------
const displayHomePage = () => {

	console.log(chalk.white(figlet.textSync("Terminal Youtube", {
		horizontalLayout: "default",
		verticalLayout: "default"
	})))


	console.log(chalk.redBright(`
    ++++++++++++++++++++++++++++++++++++++++++++
   ++++++++++++++++++++++++++++++++++++++++++++++
  ++++++++++++++++++++++++++++++++++++++++++++++++
  ++++++++++++++++++++${chalk.white('XI')}+++++++++++++++++++++++++++
  ++++++++++++++++++++${chalk.white('M###BI')}++++++++++++++++++++++++
  ++++++++++++++++++++${chalk.white('M#######BI')}++++++++++++++++++++
  ++++++++++++++++++++${chalk.white('M###########V')}+++++++++++++++++
  ++++++++++++++++++++${chalk.white('M########BI')}+++++++++++++++++++
  ++++++++++++++++++++${chalk.white('M###BI')}++++++++++++++++++++++++
  ++++++++++++++++++++${chalk.white('XI')}+++++++++++++++++++++++++++
  ++++++++++++++++++++++++++++++++++++++++++++++++=
   =++++++++++++++++++++++++++++++++++++++++++++++
    ++++++++++++++++++++++++++++++++++++++++++++++
      =+++++++++++++++++++++++++++++++++++++++++`))
	

	console.log("")


	console.log(chalk.redBright("-----------------------------------------------------"))


	console.log(chalk.gray("Use arrow keys to navigate, and press Enter to select."))

}
// #endregion 

// #region  -------------------------- Prompts ------------------------------------------

// Login Prompt 
const loginPrompt = async () => {
	return await inquirer.prompt([
		{
			type: "input",
			name: "username",
			message: "Enter username:",
		},
		{
			type: "password",
			name: "password",
			message: "Enter password:",
		},
	])
}

// User Prompt
const userPrompt = async (user) => {
	const features =  await inquirer.prompt([
		{
			type: "list",
			name: "selection",
			message: `Welcome ${user}`,
			choices:[
				"Search",
				"Channels",
				"Notifications",
				"Subscriptions",
				"exit",
				"<",
			]
		}
	])

	return features.selection
}

// Youtuber Prompt
const youtuberPrompt = async (user) => {
	const features = await inquirer.prompt([
		{
			type: "list",
			name: "selection",
			message: `Welcome ${user}`,
			choices:[
				"Publish",
				"Videos",
				"Subscribers",
				"exit",
				"<",
			]
		}
	])

	return features.selection
}

// Video publish Prompt
const videoPrompt = async (user) => {
	return await inquirer.prompt([
		{
			type: "input",
			name: "title",
			message: "Enter Title:",
		},
		{
			type: "input",
			name: "description",
			message: "Enter Description:",
		},
		{
			type: "input",
			name: "link",
			message: "Enter Link:",
		},
	])
}

// Services Prompt 
const servicePrompt = async () => {
	const selection = await inquirer.prompt([
		{
			type: "list",
			name: "service",
			message: "",
			choices: ["YouTube Studio","YouTube"],
		},
	])

	console.log(chalk.redBright("-----------------------------------------------------"))
	console.log(chalk.redBright(`Welcome to ${selection.service}`))

	return selection.service
}

// Subscribe Prompt 
const subscribePrompt = async () => {
	const selection = await inquirer.prompt([
		{
			type: "confirm",
			name: "confirm",
			message: "Do You Want to Subscribe to a Channel?",
		},
	])

	if(selection.confirm){
		console.log(chalk.redBright("-----------------------------------------------------"))
		const selection = await inquirer.prompt([
			{
				type: "input",
				name: "index",
				message: "Enter Channel Index:",
			}
		])

		return selection.index
	}

	else return ''
}

// UnSubscribe Prompt 
const unSubscribePrompt = async () => {
	const selection = await inquirer.prompt([
		{
			type: "confirm",
			name: "confirm",
			message: "Do You Want to Unsubscribe to a Channel?",
		},
	])

	if(selection.confirm){
		console.log(chalk.redBright("-----------------------------------------------------"))
		const selection = await inquirer.prompt([
			{
				type: "input",
				name: "index",
				message: "Enter Channel Index:",
			}
		])

		return selection.index
	}

	else return ''
}

// Playback Prompt 
const videoPlaybackPrompt = async () => {

	const selection = await inquirer.prompt([
		{
			type: "confirm",
			name: "confirm",
			message: "Do You Want to Watch a Video?",
		},
	])

	if(selection.confirm){
		console.log(chalk.redBright("-----------------------------------------------------"))
		const selection = await inquirer.prompt([
			{
				type: "input",
				name: "index",
				message: "Enter Video Index:",
			}
		])

		return selection.index
	}

	else return ''
}

// #endregion 

// #region  -------------------------- Helper Functions ---------------------------------

const sendMessage = async(url,request,channel,replyQueue,data)=>{
	try{
		return await channel.sendToQueue(
			url,
			Buffer.from(JSON.stringify(data)),
			{
				headers:{
					request
				},
				correlationId,
				replyTo:replyQueue.queue,
			}
		)
	}
	catch(e){
		console.warn(e)
	}
}

const response = async(channel,replyQueue)=>{
	let res

	try{
		await channel.prefetch(1)
		const req = await channel.consume(replyQueue.queue, 
			async (message) => {
			if (message.properties.correlationId === correlationId)
				res = JSON.parse(message?.content)
		}, {
			noAck: true
		})

		await channel.cancel(req.consumerTag)
	}
	catch(e){
		console.warn(e)
	}

	return res
}

const pollNotifications = async(channel,uid)=>{

	await channel.assertQueue(uid, { durable: true })
	const req = await channel.consume(uid, 
		async (message) =>{
			console.log("\n"+message?.content?.toString())
		},
	{
		noAck: true
	})

	return req
}

const login = async(service,channel) => {

	try{
		await channel.assertQueue(service, { durable: true })
		replyQueue = await channel.assertQueue('', {
            exclusive: true
        })
	}
	catch(e){
		console.warn(e)
	}

	const prompt = await loginPrompt()
	await sendMessage(service,"auth",channel,replyQueue,{
		"username":prompt.username,
		"password":prompt.password,
	})


	const res = await response(channel,replyQueue)
	return res
}

const printTable = (data, propertyToSkip) =>{
    const modifiedData = data?.map(obj => {
        const { [propertyToSkip]: omit, ...rest } = obj
        return rest
    })

    console.table(modifiedData)
}

const downloadVideo = async(url, outputPath) =>{
    try {
        const response = await axios({
            url: url,
            method: 'GET',
            responseType: 'stream'
        })

        const writer = fs.createWriteStream(outputPath)
        response.data.pipe(writer)

        return new Promise((resolve, reject) => {
            writer.on('finish', resolve)
            writer.on('error', reject)
        })
    } catch (error) {
        throw new Error('Failed to download video: ' + error.message)
    }
}

// #endregion 

// #region --------------------------- Runner --------------------------------------------

const startTerminalYouTube  = async () =>  {

	const channel = await createConnection("amqp://guest:guest@34.135.86.77:5672")
	displayHomePage()

	let service
	let uid
	let yid

	auth:while(true){

		service = await servicePrompt()		
		if(service){

			if(service === "YouTube Studio"){
				
				yid  = await login("YOUTUBER_REQUESTS", channel)

				youtuber:while(yid){
					const selection = await youtuberPrompt(yid)
					switch (selection) {

						case "Publish":{

							const video =  await videoPrompt()
							await sendMessage("YOUTUBER_REQUESTS","publishVideo",channel,replyQueue,{
								"youtuber":yid,
								"link":video.link,
								"title":video.title,
								"description":video.description,
							})

							const res = await response(channel,replyQueue)
							console.log(res)

							console.log(chalk.redBright("-----------------------------------------------------"))
							continue youtuber
						}
			
						case "Videos":{

							await sendMessage("YOUTUBER_REQUESTS","getYoutuberVideos",channel,replyQueue,{
								"youtuber":yid,
							})

							const res = await response(channel,replyQueue)
							printTable(res,"link")

							console.log(chalk.redBright("-----------------------------------------------------"))
							continue youtuber
						}
					
						case "Subscribers":{

							await sendMessage("YOUTUBER_REQUESTS","getSubscribers",channel,replyQueue,{
								"youtuber":yid,
							})

							const res = await response(channel,replyQueue)
							console.log(res, "Subscribers")

							console.log(chalk.redBright("-----------------------------------------------------"))
							continue youtuber
						}
						
						case "<":{
							break youtuber
						}
		
						case "exit":{
							await channel.close()
							await connection.close()
							process.exit(0)
						}
					}	
				}
			}
		
			else if(service === "YouTube"){

				uid = await login("USER_REQUESTS",channel)

				if(uid){
					user:while(uid){
						const selection = await userPrompt(uid)
						switch (selection) {
							case "Search":{
								const searchParam = await inquirer.prompt([
									{
										type: "input",
										name: "title",
										message: "Search Title:"
									}
								])

								await sendMessage("USER_REQUESTS","getVideos",channel,replyQueue,{
									"params":searchParam.title
								})

								const res = await response(channel,replyQueue)
								printTable(res,"link")

								const playbackReq = await videoPlaybackPrompt()

								if(playbackReq){
									const link = (res[playbackReq])?.link
									console.log(res)
									if(link){
										await downloadVideo(link,`./assets/videos/${playbackReq}.mp4`)
										const childProcess = spawn(`mplayer ./assets/videos/${playbackReq}.mp4`, {
											shell: true,
											detached: true,
											stdio: 'ignore'
										})
										childProcess.unref()
									}
								}

								console.log(chalk.redBright("-----------------------------------------------------"))
								continue user
							}
								
							case "Notifications":{
								const req = await pollNotifications(channel,uid)
								const selection = await inquirer.prompt([
									{
										type: "confirm",
										name: "confirm",
										message: "Do You Want to Go Back?",
									},
								])
							
								if(selection.confirm){
									await channel.cancel(req.consumerTag)
									continue user
								}
								
							}
				
							case "Channels":{
								await sendMessage("USER_REQUESTS","getChannels",channel,replyQueue,{})

								const res = await response(channel,replyQueue)
								console.table(res)

								console.log(chalk.redBright("-----------------------------------------------------"))

								const subscriptionReq = await subscribePrompt()
								
								if(subscriptionReq){
									await sendMessage("USER_REQUESTS","updateSubscription",channel,replyQueue,{
										"user":uid,
										"youtuber":subscriptionReq,
										"subscription":true
									})
									const res = await response(channel,replyQueue)

									console.log(res)
									console.log(chalk.redBright("-----------------------------------------------------"))
								}

								continue user
							}
					
							
							case "Subscriptions":{
								await sendMessage("USER_REQUESTS","getSubscriptions",channel,replyQueue,{
									"user":uid,
								})

								const res = await response(channel,replyQueue)
								printTable(res,"subscribers")

								console.log(chalk.redBright("-----------------------------------------------------"))

								const unSubscriptionReq = await unSubscribePrompt()
								
								if(unSubscriptionReq){
									await sendMessage("USER_REQUESTS","updateSubscription",channel,replyQueue,{
										"user":uid,
										"youtuber":unSubscriptionReq,
										"subscription":false
									})
									const res = await response(channel,replyQueue)
									
									console.log(res)
									console.log(chalk.redBright("-----------------------------------------------------"))
								}
								
								continue user
							}
								
				
							case "<":{
								continue auth
							}
		
							case "exit":{
								await channel.close()
								await connection.close()
								process.exit(0)
							}
						}
					}
				}
			}

		}
	}
}

startTerminalYouTube()

// #endregion