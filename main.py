from discord.ext import commands, tasks
import os
import requests
import json
import random
import time
from replit import db
from keep_alive import keep_alive

client = commands.AutoShardedBot(command_prefix = "$")

def update_todo(todo):
  if "todolist" in db.keys():
    todolist = db["todolist"]
    todolist.append(todo)
    db["todolist"] = todolist
  else:
    db["todolist"] = [todo]


def delete_todo(index):
  todolist = db["todolist"]
  if len(todolist) > index:
    del todolist[index]
    db["todolist"] = todolist

def get_quote():
  response =  requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return quote


@tasks.loop(seconds=86400, reconnect=True)
async def manage_time():
	offset = 30900 
	current_time = (time.time()+offset)%86400

	if 28500 > current_time or current_time > 29000:
		difference_to_8 = 28800 - current_time
		if difference_to_8 < 0:
			difference_to_8 = (86_400 - current_time) + 28800
		manage_time.change_interval(seconds=difference_to_8)
	else:
		manage_time.change_interval(seconds=86400)
		
	channel = await client.fetch_channel(821882414099857418)
  # todolist = []
	if "todolist" in db.keys():
		todolist = db["todolist"]
		await channel.send("To-Do List: ")
		for i in range(len(todolist)):
			await channel.send(f"{i+1}) {todolist[i]}")
	else:
		await channel.send("List Empty!")


	
@client.command()
async def motivate(ctx):
	await ctx.send(get_quote())

@client.event 
async def on_ready():
  print('we have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
  if message.author == client.user: 
    return
	
  await client.process_commands(message)
  msg = message.content

  if msg.startswith('$motivate'):
    quote = get_quote()
    await message.channel.send(quote)

  if msg.startswith('$add'):
    todo = msg.split("$add ", 1)[1]
    update_todo(todo)
    await message.channel.send("To-do list updated!")

  if msg.startswith("$remove"):
    todolist = []
    if "todolist" in db.keys():
      index = int(msg.split("$remove ", 1)[1])
      delete_todo(index)
      todolist = db["todolist"]
    await message.channel.send(todolist)

  if msg.startswith("$list"):
    todolist = []
    if "todolist" in db.keys():
      todolist = db["todolist"]
      await message.channel.send("To-Do List: ")
      for i in range(len(todolist)):
        await message.channel.send(f"{i+1}) {todolist[i]}")
    else:
      await message.channel.send("List Empty!")

keep_alive()
manage_time.start()
client.run(os.getenv('TOKEN'))