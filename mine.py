import configparser  
from mcstatus import BedrockServer
import discord
from discord.ext import commands
import time
from datetime import datetime
from quickchart import QuickChart

config = configparser.ConfigParser() 
config.read("settings.ini")

bot = commands.Bot(command_prefix = config['main']['prefix'])

title_name = config['main']['title_name']
name = config['main']['server_name']
ip = config['main']['ip']
port = config['main']['port']
footer = config['main']['footer']

labels = ['00:00']
data = [0]

@bot.event
async def on_ready():
    print("Я запущен!")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="винки"))

@bot.event
async def on_reaction_add(reaction, user):
    if (str(reaction.emoji) == '🔄'):

        now = datetime.now()
        current_time = now.strftime("%H:%M")

        try:
            server = BedrockServer.lookup(f"{ip}:{port}")
            status = server.status()

            global data,labels
            if(len(data) > 3 or len(labels) > 3):
                for i in range(1,len(labels)):
                    data[i-1] = data[i]
                for i in range(1,len(labels)):
                    labels[i-1] = labels[i]

                data.extend([status.players_online])
                labels.extend([current_time])


            time = int(current_time.split(':')[1]) - int(labels[len(labels) - 1].split(':')[1])
            
            if(time >= 5):
                data.extend([status.players_online])
                labels.extend([current_time])
                
                qc = QuickChart()
                qc.width = 1000
                qc.height = 600
                qc.device_pixel_ratio = 2.0
                qc.config = {
                    "type": "line",
                    "data": {
                        "labels": labels,
                        "datasets": [{
                            "label": "Online",
                            "data": data
                        }]
                    }
                }

                image = qc.get_url()

                new_embed = discord.Embed(title=f"{title_name}", colour=0x00e600)
                new_embed.add_field(name="Server Name :", value=f"{name}", inline=False)
                new_embed.add_field(name="Direct Connect :", value=f"`{ip}:{port}`", inline=True)
                new_embed.add_field(name="Game :", value=f"Bebrock", inline=True)
                new_embed.add_field(name="Map :", value=f"{status.map}", inline=True)
                new_embed.add_field(name="Status :", value=f"✅ Online", inline=True)
                new_embed.add_field(name="Online Players :", value=f"{status.players_online} \ {status.players_max}", inline=True)
                new_embed.set_footer(text=f"Last Update: {current_time} | {footer}")
                new_embed.set_image(url=image)

                await msg.edit(embed = new_embed)
        except:

            print('oooops, error')

            new_embed = discord.Embed(title=f"{title_name}", colour=0xff0000)
            new_embed.add_field(name="Status :",value=f"❌ Offline", inline=True)
            
            new_embed.set_footer(text=f"Last Update: {current_time} | {footer}")

            await msg.edit(embed = new_embed)

        if(not user.bot):
            await reaction.remove(user)
        
        
@bot.command(name='list', description='узнать кол-во игроков на сервере', help='узнать кол-во игроков на сервере', aliases=['l','online'])
@commands.has_guild_permissions(administrator=True)
async def list(ctx):    

    embed = discord.Embed(title=f"{name}", colour=0x87CEEB, timestamp=datetime.utcnow())
    embed.add_field(name="online", value="no info", inline=False)
    embed.add_field(name="motd", value="no info", inline=True)
    embed.add_field(name="connect", value="no info", inline=True)
    embed.set_footer(text="from prorok with love!)")
    
    message = await ctx.send(embed=embed)

    global msg
    msg = await ctx.fetch_message(message.id)

    await message.add_reaction('🔄')  


bot.run(config['main']['token']) 
