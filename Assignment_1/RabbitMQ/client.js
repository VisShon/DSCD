const inquirer = require("inquirer")
const chalk = require("chalk")
const figlet = require("figlet")
const amqp = require("amqplib")

const user = require("./controllers/user.js")
const youtuber = require("./controllers/youtuber.js")

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

//--------------------------- Display Home -------------------------------------
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




//--------------------------- Prompts -------------------------------------

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
			message: `Welcome ${user.username}`,
			choices:[
				"Search",
				"Channels",
				"Notifications",
				"Subscriptions",
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
			message: `Welcome ${user.username}`,
			choices:[
				"Publish",
				"Videos",
				"Subscribers",
				"<"
			]
		}
	])

	return features.selection
}

// Services Prompt 
const servicePrompt = async () => {
	const selection = await inquirer.prompt([
		{
			type: "list",
			name: "service",
			message: "",
			choices: ["YouTube", "YouTube Studio"],
		},
	])

	console.log(chalk.redBright("-----------------------------------------------------"))
	console.log(chalk.redBright(`Welcome to ${selection.service}`))

	return selection.service
}




//--------------------------- Login -------------------------------------
const login = async (username,password,channel) => {

	// this fuction is used to login or create a new account(queue) for the user
	try{
		await channel.assertQueue(`${username+password}`, {
			exclusive: true
		})
		console.log("SUCESS USER",await channel.checkQueue(`${username+password}`))
		return true
	}
	catch{
		return false
	}
}



// Function to start the Terminal YouTube application
const startTerminalYouTube  = async () =>  {

	displayHomePage()


	const channel = await createConnection("amqp://vishnu:shon123@localhost:5672")
	channel.assertExchange("YOUTUBE", "topic", {
		durable: false //change to true in production
	})


	let auth
	try{
		auth = await loginPrompt()
		auth.success = await login(auth.username, auth.password, channel)
	}
	catch(e){
		console.warn(e)
	}



	if(auth.success){
		const service = await servicePrompt()

		if(service === "YouTube Studio"){
			const selection = await youtuberPrompt(auth)
			switch (selection) {
				case "Publish":
					await youtuber.publishVideo(auth,channel)
					break

				case "Videos":
					
					break
			
				case "Subscribers":
					
					break
				
				case "<":
					
					break

				default:
					break
			}

		}

		
		else if(service === "YouTube"){
			const selection = await userPrompt(auth)
			await channel.assertQueue(`${auth.username+auth.password}`,{
				exclusive:true
			})

			switch (selection) {
				case "Search":
					
					break

				case "Channels":
					await user.getChannels(channel)
					break
			
				case "Notifications":
					await channel.bindQueue(`${auth.username+auth.password}`, "YOUTUBE", "ss");
					await user.receiveNotifications(auth,channel)
					break
				
				case "Subscriptions":
					
					break

				case "<":
					
					break

				default:
					break
			}
			
		}

		else return
	}


	
	setTimeout(async () => {
		await channel.close()
		await connection.close()
	},5000)
	
	return
}

// Start the application
startTerminalYouTube()