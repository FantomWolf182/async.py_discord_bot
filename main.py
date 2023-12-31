import discord
from discord.ext import commands
import json
import os
from keep_alive import keep_alive
import time
import asyncio




# Define the intents
intents = discord.Intents.default()
intents.message_content = True  # Enable message content for the on_message event
intents.presences = True  # Enable presence updates
intents.members = True  # Enable member updates

# Load questions and answers from the JSON file
with open('ans.json', 'r') as file:
    answers_dict = json.load(file)

with open('username_and_userid.json', 'r') as file:
  userids = json.load(file)


# Create an instance of the bot with the specified intents
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print("Async.py is up and running!")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(e)

def create_embed(content, color):
  embed = discord.Embed(description=content, color=color)
  return embed

async def send_embed(channel, content, color, embeduserid=None):
  embed = create_embed(content, color)
  if embeduserid is not None:
      await channel.send(f"<@{embeduserid}>", embed=embed)
  else:
      await channel.send(embed=embed)



@bot.event
async def on_message(message):
  with open('username_and_userid.json', 'r') as file:
    userids = json.load(file)
  
    # Ignore messages from the bot itself to prevent potential loops
    if message.author == bot.user:
        return

    # Check if the user has the role "Naruto Botto"
    naruto_botto_role = discord.utils.get(message.guild.roles, name="Naruto Botto")
    if naruto_botto_role:
        if naruto_botto_role in message.author.roles:
            # Check if the message contains a question and answers in a flexible format
            if any(emoji in message.embeds[0].description for emoji in [":one:", ":two:", ":three:"]):
                # Extract the question and answers
                lines = message.embeds[0].description.split('\n')
                # Remove asterisks from the question
                question = lines[0].strip().replace('*', '')
                answers = [line.split(":", 1)[1].strip() for line in lines[1:] if ":" in line]

                # Extract the username from the embed title
                username = message.embeds[0].title.split("'s")[0]

                # Look for the answer in the ans.json file (case-insensitive)
                question_lower = question.lower()
                answer_key = next((value for key, value in answers_dict.items() if key.lower() == question_lower), None)

                if answer_key is not None:
                    # Send the question instead of printing
                    # await message.channel.send(f"Question: {question}")

                    # You can use the extracted variables (question, answers, answer_key) for further processing
                    response = f"The correct answer is: {answer_key}"

                    # Mention the user in the response
                    # await message.channel.send(f"## {username} ## , {response}")

                    # Send emoji based on the selected answer
                    emoji_dict = {1: ":one:", 2: ":two:", 3: ":three:"}
                    for i, ans in enumerate(answers):
                        if ans.lower().endswith(answer_key.lower()):
                            answer_number = i + 1
                            emoji_answer = emoji_dict.get(answer_number, "")
                            user_id = userids.get(username)
                            response = f" ### {emoji_answer} {answer_key}"
                            await send_embed(message.channel, response, discord.Color.green(), user_id)
                            await timer(message, 60, "mission")
                            break
                    else:
                      user_id = userids.get(username)
                      response = f" ### {answer_key}"
                      await send_embed(message.channel, response, discord.Color.orange(), user_id)
                      await timer(message, 60, "mission")
                else:
                    response = 'Answer not found in the ans.json file \n Question: {question}'
                    user_id = userids.get(username)
                    await send_embed(message.channel, response, discord.Color.red(), user_id)
                    await timer(message, 60, "mission")
            elif any(report_text in message.embeds[0].description for report_text in ["You saw", "free time."]):
                # Extract the report
                lines = message.embeds[0].description.split('\n')
                # Remove asterisks from the question
                report = lines[0].strip().replace('*', '')

                # Extract the username from the embed title
                username = message.embeds[0].title.split("'s")[0]

                # Send the report
                report = report.replace("You saw a group of ", "")
                report = report.replace(" while wandering around the village in your free time.", "")
                report = report.replace(" suspicious individuals", "")
                user_id = userids.get(username)
                response = f" ### {report}"
                await send_embed(message.channel, response, discord.Color.green(), user_id)
                await timer(message, 600, "report")
            else:
                response = 'Invalid format'
                #await message.channel.send(response)
        else:
            # If the user doesn't have the role "Naruto Botto"
            response = 'not_naruto_botto_role'
            # await message.channel.send(response)
    else:
        # If the role "Naruto Botto" doesn't exist on the server
        response = 'Make sure that the official Naruto Botto has the proper role'
        username = message.embeds[0].title.split("'s")[0]
        user_id = userids.get(username)
        await send_embed(message.channel, response, discord.Color.orange(), user_id)

    # Allow other event handlers to process the message
    await bot.process_commands(message)

async def timer(message, time, type):
  with open('username_and_userid.json', 'r') as file:
    userids = json.load(file)
  username = message.embeds[0].title.split("'s")[0]

  # Get the user ID from the JSON data
  user_id = userids.get(username)

  # Check if user ID is found
  if user_id:
  # Start a timer for 1 minute
    await asyncio.sleep(time)
    # Send a ping to the user after 1 minute
    response = f" ### Your {type} is ready!"
    await send_embed(message.channel, response, discord.Color.blue(), user_id)




@bot.tree.command(name="hello", description="Say hello to the bot!")
async def hello(interaction: discord.Interaction):
  response = f"Hey. Try some of my other commands next!"
  await send_embed(interaction.channel, response, discord.Color.og_blurple(), interaction.user.id)

@bot.tree.command(name="notifications_setup", description="Setup notifications")
async def notification_setup(interaction: discord.Interaction):
    # Retrieve username and user ID
    username = interaction.user.name
    user_id = str(interaction.user.id)

    # Create or load the JSON file
    try:
        with open('username_and_userid.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # Store the username and user ID in the JSON file
    data[username] = user_id

    # Save the updated JSON file
    with open('username_and_userid.json', 'w') as file:
        json.dump(data, file)

    response = f"Notification setup complete!"
    await send_embed(interaction.channel, response, discord.Color.green(), user_id)

@bot.tree.command(name="about", description="Information surrounding the bot")
async def about(interaction: discord.Interaction):
  response = str("# About **Async.py:** \n \n ## **Made by:** \n Quanfy, who is a really cool guy <:goodjob:1191142838684102777> \n \n Different Embed Color Meanings: \n \n **Green** - The answer is correct and the bot functioned correctly \n \n **Orange** - The answer is correct but the bot could not correctly extract the right answer number, \n \n **Red** - The answer is incorrect or the bot could not find the answer. \n \n **If you are not getting notifcations, make sure that you have setup notifications (using /notifications_setup)** \n \n ## **Have Fun!**")
  await send_embed(interaction.channel, response, discord.Color.og_blurple())






keep_alive()
try:
    bot.run(os.environ['bot_token'])
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system('kill 1')
    os.system("python restarter.py")

