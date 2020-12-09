# shadowBot.py - a wizen#1312 creation.
import os

prefix = '!'

import discord
from dotenv import load_dotenv
from discord.message import Message
load_dotenv()
# database handler
import mysql.connector

DB_PASSWORD = os.getenv('DB_PASSWORD')

mydb = mysql.connector.connect(
  host="localhost",
  user="keybot",
  password=DB_PASSWORD,
  database="exuKeyDB"
)
sql=mydb.cursor()

print('MySQL Database [exuKeyDB] connected!')



TOKEN = os.getenv('DISCORD_TOKEN')

bot = discord.Client()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_message(message):
    if message.author==bot.user: #ignore own messages
        return 
    if message.content.startswith(prefix)==False: 
        return
    if isinstance(message.channel, discord.channel.DMChannel):
        return
    argString=message.content.strip(prefix)
    args=argString.split(' ')
    
    
    if args[0]=='addKey': # add a key to the database
        if len(args)==1:
            await message.channel.send("Sorry, can't add a key with no key!")
            return
        if len(args)>2:
            await message.channel.send("Sorry, keys cannot contain spaces!")
            return
        keyToAdd=args[1]
        donor=message.author.name
        
        
        await message.delete()
        sql.execute('INSERT INTO mysteryKeys (name,gameKey) VALUES ("' + donor + '","' + keyToAdd + '");')
        mydb.commit()
        await message.channel.send('Thank you for your generosity, ' + donor + '! The key has been recorded!')

    if args[0]=='getKey': 
        if len(args)>1:
            await message.channel.send("getKey does not accept arguments!")
            return
                
        sql.execute('SELECT gameKey,name,id FROM mysteryKeys WHERE id = (SELECT MIN(id) FROM mysteryKeys)AND name != "' + message.author.name + '";')
        keyResult = sql.fetchall()
        
        if len(keyResult)==0:
            await message.channel.send("Cannot fetch any keys! Can I interest you in donating one?")
            return
        
        channel = await message.author.create_dm()
        await channel.send("Your key is " + keyResult[0][0] + " - Donated by " + keyResult[0][1] +"!")       
        await message.channel.send("Key dispensed.")
        sql.execute('DELETE FROM mysteryKeys WHERE id ="' + str(keyResult[0][2]) + '";')
        mydb.commit()
        await message.delete()
        
    if args[0]=='help': # help function
        await message.channel.send("Don't Panic! I understand the following commands. !help (this message), !addKey <key>, and !getKey. Capitalization matters! Key requests are still not tracked. Donors are tracked for gratitude purposes.")
        
        
bot.run(TOKEN)