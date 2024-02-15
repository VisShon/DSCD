const inquirer = require("inquirer")
const chalk = require("chalk")
const figlet = require("figlet")
const amqp = require("amqplib")

const user = require("./utils/user.js")
const youtuber = require("./utils/youtuber.js")

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


const sendMessage = async(url,request,channel,data)=>{
	await channel.sendToQueue(
		url,
		Buffer.from(JSON.stringify(data)),
		{
			headers:{
				request
			}
		}
	)
	return true
}


// Function to start the Terminal YouTube application
const startTerminalYouTube  = async () =>  {

	let promptSelection = 0
	displayHomePage()


	const channel = await createConnection("amqp://vishnu:shon123@localhost:5672")
	channel.assertExchange("YOUTUBE", "topic", {
		durable: false //change to true in production
	})

	let auth
	let service
	let uid
	let yid

	prompt:while(true){

		service = await servicePrompt()
		
		if(service){
			
			if(service === "YouTube Studio"){
				await channel.assertQueue("YOUTUBER_REQUESTS", { durable: true })

				try{
					auth = await loginPrompt()
					await sendMessage("YOUTUBER_REQUESTS","auth",channel,{
						"username":auth.username,
						"password":auth.password,
					})
					
				}
				catch(e){
					console.warn(e)
				}
				const selection = await youtuberPrompt(auth)

				// switch (selection) {
				// 	case "Publish":
				// 		sendMessage("YOUTUBER_REQUESTS","publishVideo",channel,{
				// 			"youtuber":"c51ffdea-c35a-44d2-9ca5-d78dc191a436",
				// 			"link":"link",
				// 			"title":"video",
				// 			"description":"first video"
				// 		})
				// 		break
		
				// 	case "Videos":
						
				// 		break
				
				// 	case "Subscribers":
						
				// 		break
					
				// 	case "<":
				// 		continue prompt
	
				// 	case "exit":
				// 		continue prompt

				// 	default:
				// 		break
				// }
		
			}
		
			
			else if(service === "YouTube"){
				await channel.assertQueue("USER_REQUESTS", { durable: true })
				const selection = await userPrompt(auth)
		
				// switch (selection) {
				// 	case "Search":
						
				// 		break
		
				// 	case "Channels":
				// 		break
				
				// 	case "Notifications":
				// 		break
					
				// 	case "Subscriptions":
						
				// 		break
		
				// 	case "<":
				// 		continue prompt

				// 	case "exit":
				// 		continue prompt
		
				// 	default:
				// 		break
				// }
				
			}
		
			else return
		}

	}
	
	// setTimeout(async () => {
	// 	await channel.close()
	// 	await connection.close()
	// },5000)
	
}

// Start the application
startTerminalYouTube()