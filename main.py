length = 6

TOKEN = ""

import discord
from discord.ext import commands
import random
from captcha.image import ImageCaptcha
import string
import json
import os

bot = commands.Bot(command_prefix="=", case_insensitive=True, intents=discord.Intents.all())

config = None
verify_channel = None
verify_role = None
verify_guild = None

@bot.event
async def on_ready():

    global config
    global verify_channel
    global verify_role
    global verify_guild

    print(f"{bot.user} is online.")
    
    try:
        config = json.loads(open("config.json", "r").read())

    except:
        print("No config found! Run =setup in your server!")

    else:
        verify_guild = bot.get_guild(config["guild"])
        verify_role = verify_guild.get_role(config["role"])
        verify_channel = bot.get_channel(config["channel"])
        
        print("Loaded Config!")
        

@bot.event
async def on_member_join(member):

    global config
    global verify_channel
    global verify_role
    global verify_guild

    if member.guild.id == int(config["guild"]):

        ascii_lowercase = 'abcdefghjlmnpqrstuvwxyz'
        ascii_uppercase = 'ABCDEFGHJLMNPQRSTUVWXYZ'
        digits = '23456789'
        
        text = ''.join(random.choice(ascii_uppercase + digits + ascii_lowercase) for _ in range(length)).lower()
        file_name = ''.join(random.choice(ascii_uppercase + digits + ascii_lowercase) for _ in range(20))
        image = ImageCaptcha(width=280, height=90)
        captcha = image.generate(text)
        image.write(text, f"captchas\{file_name}.png")
        file = discord.File(f"captchas//{file_name}.png", filename=f"{file_name}.png")
        embed = discord.Embed(title="Verification Capchat", description="This server is using Captcha Verification to protect their server.\nPlease type out the letters you see in the captcha below.\n\n**Note:** All letters are **in lower case**, you have **only 5 chances**, and 5 minutes or **you will be expelled from the server.**\n\nPS: If you can't do it, no worries, you can try your luck as many times as possible **to find an easier capchat.**", icon_url="http://image.noelshack.com/fichiers/2022/25/3/1655892549-1.png", image=f"attachment://")
        embed.set_image(url=f"attachment://{file_name}.png")
        embed.set_thumbnail(url="http://image.noelshack.com/fichiers/2022/25/3/1655892549-1.png")
        
        del_msgs = []
        msg = await verify_channel.send(content=member.mention, embed=embed, file=file)
        del_msgs.append(msg)

        def wait_for_reply(message):
            return message.channel == verify_channel and message.author == member

        for x in range(5):
            
            try:
                rpy = await bot.wait_for("message", check=wait_for_reply, timeout=300)
            
            except:
                try: 
                    
                    await member.kick(reason="Verification Timeout.")
                    channel = bot.get_channel(966688939488477224)
                    
                    await channel.send(f"{member.mention} took too long to do the capchat.")
                
                except: 
                    pass
                
                break
            
            else:
                
                if rpy.content == text:
                    await member.add_roles(verify_role)

                    channel = bot.get_channel(966688939488477224)
                    await channel.send(f"{member.mention} successfully passed the capchat.")

                    for x in del_msgs:
                        await x.delete()
                    await rpy.delete()
                    
                    return
                
                else:
                    
                    if x != 4:
                        msg = await verify_channel.send(f"{member.mention} Invalid, please try again.")
                        del_msgs.append(msg)
                        del_msgs.append(rpy)

        try: 
            
            await member.kick(reason="Too many attempts.")
            channel = bot.get_channel(966688939488477224)
            await channel.send(f"{member.mention} missed too many times the capchat, he was expelled.")

        except: 
            
            pass
        
        for x in del_msgs:
            
            try:
                await x.delete()
            
            except:
                continue

        await rpy.delete()

@bot.event
async def on_channel_create(channel):
    
    global config
    global verify_channel
    global verify_role
    global verify_guild
    
    if channel.id == int(config["channel"]):
        
        try:
            overwrites = {verify_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
                add_reactions=False
            )}
            
            await channel.edit(overwrites=overwrites)
        
        except:
            pass


@bot.command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    
    if os.path.exists("config.json"):
        await ctx.send("config.json already exists!")
        return

    global config
    msg = await ctx.send("Setting up guild...")
    role = await ctx.guild.create_role(name="Verifing")
    
    for channel in ctx.guild.channels:
        try:
            overwrites = {role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
                add_reactions=False
            )}
            await channel.edit(overwrites=overwrites)

        except:
            pass

    overwrites = {

        ctx.guild.default_role: discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
        ),
        role: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
        )
    }

    channel = await ctx.guild.create_text_channel(name="verify-here", overwrites=overwrites, slowmode_delay=10)
    con_json = {"role": role.id, "channel": channel.id, "guild": ctx.guild.id}
    config = con_json
    conf = open("config.json", "a")
    conf.write(json.dumps(con_json))
    conf.close()
    await msg.edit(content="Finished Setup!")

@bot.command()
@commands.guild_only()
@commands.has_permissions(administrator=True)
async def perms_setup(ctx):

    if not os.path.exists("config.json"):
        await ctx.send("config.json doesn't exists!")
        return

    global config

    msg = await ctx.send("Rechecking perms...")

    for channel in ctx.guild.channels:

        try:
            overwrites = {verify_role: discord.PermissionOverwrite(
                read_messages=False,
                send_messages=False,
                add_reactions=False
            )}

            await channel.edit(overwrites=overwrites)

        except:
            pass

    overwrites = {

        ctx.guild.default_role: discord.PermissionOverwrite(
            read_messages=False,
            send_messages=False,
        ),

        verify_role: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=True,
        )
    }

    await msg.edit("Finished Setup!")

bot.run(TOKEN)
