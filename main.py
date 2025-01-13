import interactions
import random
import asyncio
import json
import logging

from interactions import Client, SlashContext, slash_command

toke_file = open("secret/bot_token.env")
BOT_TOKEN = toke_file.read()

# File path for storing user data
DATA_FILE = 'character_id.json'

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord_errors.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

# Helper function to load user data
def load_data():
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        print("No existing data found or JSON decode error.")
        return {}

# Helper function to save user data
def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

bot = Client(token=BOT_TOKEN)

@bot.event
async def on_ready():
    global user_data_RPG
    print(f'Logged in as {bot.user}')
    user_data_RPG = load_data()
    print(f'User data loaded: {user_data_RPG}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, interactions.errors.CommandNotFound):
        await ctx.send("This command does not exist. Please use /help to see the list of available commands.")
    elif isinstance(error, interactions.errors.MissingRequiredArgument):
        await ctx.send("You are missing required arguments for this command.")
    elif isinstance(error, interactions.errors.BadArgument):
        await ctx.send("One of your arguments is invalid.")
    elif isinstance(error, interactions.errors.CommandInvokeError):
        await ctx.send("There was an error while executing the command. Please try again later.")
        logger.error(f"Error in command '{ctx.command}': {error}")
    else:
        await ctx.send("An unexpected error occurred. Please try again later.")
        logger.error(f"Unexpected error: {error}")

places = {
    "kingdoms": {
        "The Central Dominance": {
            "Dominous": {
                "town square": {
                    "description": "You stand at in the middle of town square.",
                    "items": ["none"],
                    "npcs": ["Agrand"],
                    "cords": [0, 0]
                },
            }
        }
    }
}

biomes = {
    "grassy plains": {
        "enemies": {
            "Swamp lurch": {
                "enemy_health": 30,
                "enemy_attack": 13,
                "enemy_dexterity": 5,
                "xp": 50
            },
        },
        "description": "You stroll through the lucious grassy plains.",
        "look_description": "You are in the grassy fields of the Central Dominance.",
        "freq": 1,
        "area": [-50, 100, -50, 50],
    }
}

dialouges = {
    "Agrand": {
        "Quest": {
            "description":
                "Yes mate, go kill some swamp lurches."
                "\nThose bastards have been chewing on my grain for weeks!",
            "clear": "Thank you for killing those bastards!",
            "enemy": "Swamp lurch",
            "amount": 3,
            "xp_reward": 50
        },
        "Help": "You need help you say? Try typing /help to get a list of commands!"
    }
}

@slash_command(name="initialize", description="Initialize the bot for a user")
async def initialize(ctx: SlashContext):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()
        if user_id not in user_data_RPG:
            user_data_RPG[user_id] = {
                'x': 0, 'y': 0,
                "max_hp": 100,
                "player_health": 100,
                "player_attack": 20,
                "player_dexterity": 10,
                "player_energy": 10,
                "max_energy": 10,
                "current_quest": None,
                "progress": 0,
                "xp": 0,
                "threshold": 50
            }
            save_data(user_data_RPG)
            await ctx.send("Bot initialized")
        else:
            await ctx.send("You are already initialized!")
    except Exception as e:
        await ctx.send("An error occurred during initialization. Please try again later.")
        logger.error(f"Error in initialize command: {e}")

@slash_command(name="ping", description="Ping the bot")
async def ping(ctx: SlashContext):
    await ctx.send("pong")

async def lvl_up(ctx):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        await ctx.send("You leveled up!")
        await ctx.send("Please choose an option!")

        view = interactions.ui.View()

        strength_button = interactions.ui.Button(label="Strength", style=interactions.ButtonStyle.blurple)
        health_button = interactions.ui.Button(label="Health", style=interactions.ButtonStyle.red)
        dexterity_button = interactions.ui.Button(label="Dexterity", style=interactions.ButtonStyle.green)

        async def button_callback(interaction, attribute):
            if interaction.user == ctx.author:
                if attribute == "Strength":
                    await ctx.send("You have chosen Strength")
                    user_data_RPG[user_id]["player_attack"] += 5
                elif attribute == "Health":
                    await ctx.send("You have chosen Health")
                    user_data_RPG[user_id]["max_hp"] += 10
                elif attribute == "Dexterity":
                    await ctx.send("You have chosen Dexterity")
                    user_data_RPG[user_id]["player_dexterity"] += 5

                user_data_RPG[user_id]["xp"] = 0
                user_data_RPG[user_id]["threshold"] += 50
                save_data(user_data_RPG)

                for item in view.children:
                    item.disabled = True
                await interaction.response.edit_message(view=view)
            else:
                await interaction.response.send_message("You cannot click this button!", ephemeral=True)

        strength_button.callback = lambda interaction: button_callback(interaction, "Strength")
        health_button.callback = lambda interaction: button_callback(interaction, "Health")
        dexterity_button.callback = lambda interaction: button_callback(interaction, "Dexterity")

        view.add_item(strength_button)
        view.add_item(health_button)
        view.add_item(dexterity_button)

        await ctx.send("Choose an attribute to improve:", view=view)
    except Exception as e:
        await ctx.send("An error occurred while leveling up. Please try again later.")
        logger.error(f"Error in lvl_up function: {e}")

async def get_biome(ctx):
    try:
        user_id = str(ctx.author.id)
        user_data = load_data()

        x = user_data[user_id]["x"]
        y = user_data[user_id]["y"]

        for biome_name, biome_data in biomes.items():
            biome_area = biome_data["area"]
            if biome_area[0] <= x <= biome_area[1] and biome_area[2] <= y <= biome_area[3]:
                return biome_data

        return None
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

async def get_rand_encounter(ctx):
    try:
        biome = await get_biome(ctx)

        if biome:
            enemy_name = random.choice(list(biome["enemies"].keys()))
            enemy_stats = biome["enemies"][enemy_name]

            freq = random.randint(1, biome["freq"])

            if freq == 1:
                return enemy_name, enemy_stats, freq
            else:
                return None
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

async def get_place(ctx):
    try:
        user_id = str(ctx.author.id)
        user_data = load_data()

        x = user_data[user_id]['x']
        y = user_data[user_id]['y']

        for kingdom_name, kingdom_data in places.items():
            for city_name, city_data in kingdom_data.items():
                for region_name, region_data in city_data.items():
                    for region_key, region_info in region_data.items():
                        if "cords" not in region_info:
                            continue

                        cords = region_info["cords"]

                        if cords == [x, y]:
                            return region_info

        return None
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

async def accept_quest(ctx, user_id, enemy, amount, xp_reward):
    try:
        user_data_RPG = load_data()
        user_data_RPG[user_id]["current_quest"] = {"enemy": enemy, "amount": amount, "progress": 0,
                                                   "xp_reward": xp_reward}
        save_data(user_data_RPG)
        await ctx.send(f"You have accepted the quest to kill {amount} {enemy}")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

async def decline_quest(ctx):
    await ctx.send("You have declined the quest.")

async def quest(ctx, enemy, amount, quest_info):
    try:
        user_id = str(ctx.author.id)

        user_data_RPG = load_data()

        if user_data_RPG[user_id]["current_quest"]:
            await ctx.send("You are already doing a quest!")
        else:
            view = interactions.ui.View()

            accept_button = interactions.ui.Button(label="Yes", style=interactions.ButtonStyle.green)
            decline_button = interactions.ui.Button(label="No", style=interactions.ButtonStyle.red)

            async def accept_button_callback(interaction):
                if interaction.user == ctx.author:
                    await accept_quest(ctx, user_id, enemy, amount, quest_info["xp_reward"])
                else:
                    await interaction.response.send_message("You cannot click this button!", ephemeral=True)

            async def decline_button_callback(interaction):
                if interaction.user == ctx.author:
                    await decline_quest(ctx)
                else:
                    await interaction.response.send_message("You cannot click this button!", ephemeral=True)

            accept_button.callback = accept_button_callback
            decline_button.callback = decline_button_callback

            view.add_item(accept_button)
            view.add_item(decline_button)

            await ctx.send(quest_info["description"], ephemeral=True)
            await ctx.send(f"Do you want to accept the quest to kill {amount} {enemy}?", view=view)
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

async def complete_quest(ctx, user_id, xp_reward):
    try:
        user_data_RPG = load_data()
        xp = user_data_RPG[user_id]["xp"]
        threshold = user_data_RPG[user_id]["threshold"]

        xp += xp_reward

        user_data_RPG[user_id]["xp"] = xp

        if xp >= threshold:
            await lvl_up(ctx)

        user_data_RPG[user_id]["current_quest"] = None
        save_data(user_data_RPG)

        await ctx.send(f"You have completed your quest and earned {xp_reward} XP!")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

async def fight(ctx, enemy_health, enemy_attack, enemy_dexterity, enemy_name, enemy_xp):
    try:
        user_id = str(ctx.author.id)

        user_data_RPG = load_data()

        player_health = user_data_RPG[user_id]['player_health']
        player_attack = user_data_RPG[user_id]['player_attack']
        player_dexterity = user_data_RPG[user_id]['player_dexterity']

        while player_health > 0 and enemy_health > 0:
            round_message = []

            player_roll = random.randint(1, player_dexterity + enemy_dexterity)
            if player_roll <= player_attack:
                enemy_health -= player_attack
                round_message.append(f"You hit the {enemy_name} for {player_attack} damage.")
            else:
                round_message.append("You missed.")

            enemy_roll = random.randint(1, player_dexterity + enemy_dexterity)
            if enemy_roll <= enemy_dexterity:
                player_health -= enemy_attack
                round_message.append(f"The {enemy_name} hits you for {enemy_attack} damage.")
            else:
                round_message.append(f"The {enemy_name} missed.")

            round_message.append(f"Your health: {player_health}")
            round_message.append(f"{enemy_name}'s health: {enemy_health}")

            await ctx.send("\n".join(round_message))

            user_data_RPG[user_id]['player_health'] = player_health
            save_data(user_data_RPG)

            if player_health <= 0 or enemy_health <= 0:
                break

            await asyncio.sleep(0.5)
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

    if player_health <= 0:
        await ctx.send("You have been defeated!")
        user_data_RPG[user_id]['player_health'] = 0
    elif enemy_health <= 0:
        await asyncio.sleep(0.5)
        await ctx.send(f"The {enemy_name} has been defeated!")
        xp = user_data_RPG[user_id]["xp"]
        threshold = user_data_RPG[user_id]["threshold"]

        xp += enemy_xp

        user_data_RPG[user_id]["xp"] = xp

        if xp >= threshold:
            await lvl_up(ctx)

        current_quest = user_data_RPG[user_id].get("current_quest", None)
        if current_quest:
            enemy = current_quest["enemy"]
            amount = current_quest["amount"]
            progress = current_quest["progress"]

            if enemy_name == enemy and progress < amount:
                progress += 1
                current_quest["progress"] = progress
                user_data_RPG[user_id]["current_quest"] = current_quest

                if progress == amount:
                    await complete_quest(ctx, user_id, current_quest["xp_reward"])
                else:
                    await ctx.send(f"{progress} / {amount}")

    user_data_RPG[user_id]['player_health'] = player_health
    save_data(user_data_RPG)

@slash_command(name="move", description="Move in a direction")
async def move(ctx: SlashContext, direction: str, amount: int):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if user_id not in user_data_RPG:
            await ctx.send("You need to initialize first with /initialize.")
            return

        x = user_data_RPG[user_id]['x']
        player_energy = user_data_RPG[user_id]['player_energy']
        y = user_data_RPG[user_id]['y']

        valid_directions = ["w", "west", "n", "north", "e", "east", "s", "south"]
        direction = direction.lower()
        if direction not in valid_directions:
            await ctx.send("Please choose a valid direction (w/west, n/north, e/east, s/south).")
            return

        try:
            amount = int(amount)
        except ValueError:
            await ctx.send("Please provide a valid integer for the amount.")
            return

        if player_energy > 0:
            for i in range(amount):
                if player_energy <= 0:
                    await ctx.send("You are out of energy, try resting!")
                    break

                if direction in ["w", "west"]:
                    x -= 1
                elif direction in ["e", "east"]:
                    x += 1
                elif direction in ["n", "north"]:
                    y += 1
                elif direction in ["s", "south"]:
                    y -= 1

                player_energy -= 1
                await ctx.send(f"Your coordinates are now {x}, {y}. Remaining energy: {player_energy}")
                await asyncio.sleep(0.5)

                place = await get_place(ctx)
                if place:
                    await ctx.send(place["description"])
                else:
                    biome = await get_biome(ctx)
                    if biome:
                        await ctx.send(biome["description"])
                        encounter = await get_rand_encounter(ctx)
                        if encounter:
                            enemy_name, enemy_stats, freq = encounter
                            await ctx.send(f"You encounter a {enemy_name}")
                            await fight(ctx, enemy_stats["enemy_health"], enemy_stats["enemy_attack"],
                                        enemy_stats["enemy_dexterity"], enemy_name, enemy_stats["xp"])

                user_data_RPG[user_id]['x'] = x
                user_data_RPG[user_id]['y'] = y
                user_data_RPG[user_id]['player_energy'] = player_energy
                save_data(user_data_RPG)
        else:
            await ctx.send("You are out of energy, try resting!")
    except Exception as e:
        await ctx.send("An error occurred while moving. Please try again later.")
        logger.error(f"Error in move command: {e}")

@slash_command(name="rest", description="Rest to recharge your energy")
async def rest(ctx: SlashContext, amount: int):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        player_energy = user_data_RPG[user_id]['player_energy']
        max_energy = user_data_RPG[user_id]["max_energy"]

        player_health = user_data_RPG[user_id]['player_health']
        max_hp = user_data_RPG[user_id]["max_hp"]

        try:
            amount = int(amount)
        except ValueError:
            await ctx.send(f"Please give an integer that is between 0 and {max_energy}")
            return

        if amount <= 0:
            await ctx.send(f"You need to rest for a positive number of seconds.")
            return

        if player_energy == max_energy and player_health == max_hp:
            await ctx.send(f"Your energy and health are already full.")
            return

        await ctx.send(f"You sit down to rest for {amount} seconds.")

        message = await ctx.send(f"{amount} seconds remaining")
        await asyncio.sleep(1)

        for i in range(amount):
            remaining_time = amount - (i + 1)
            await message.edit(content=f"{remaining_time} seconds remaining.")

            if player_energy < max_energy:
                player_energy = min(player_energy + 1, max_energy)
            if player_health < max_hp:
                player_health = min(player_health + 10, max_hp)

            user_data_RPG[user_id]['player_energy'] = player_energy
            user_data_RPG[user_id]['player_health'] = player_health
            save_data(user_data_RPG)

            if player_energy == max_energy and player_health == max_hp:
                await ctx.send(f"Your energy and health are now full.")
                break

            await asyncio.sleep(1)

        await ctx.send(f"Rest is complete! You now have {player_energy} energy and {player_health} HP.")
    except Exception as e:
        await ctx.send("An error occurred while resting. Please try again later.")
        logger.error(f"Error in rest command: {e}")


@bot.slash_command(name="look", description="Describe your surroundings")
async def look(ctx: SlashContext):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if user_id not in user_data_RPG:
            await ctx.send("You need to initialize first with /initialize.")
            return

        x = user_data_RPG[user_id]['x']
        y = user_data_RPG[user_id]['y']

        place = await get_place(ctx)

        if place:
            await ctx.send(f"\n{place['description']}")

            items = place.get('items', ['none'])
            if "none" not in items:
                await ctx.send(f"Items: {', '.join(items)}")
            else:
                await ctx.send("There are no items here.")

            npcs = place.get('npcs', ['none'])
            if "none" not in npcs:
                for npc in npcs:
                    await ctx.send(f"{npc} is here")
            else:
                await ctx.send("There are no NPCs here.")
        else:
            biome = await get_biome(ctx)
            if biome:
                await ctx.send(biome["look_description"])
                items = biome.get('items', ['none'])
                if "none" not in items:
                    await ctx.send(f"Items: {', '.join(items)}")
                else:
                    await ctx.send("There are no items here.")

                npcs = biome.get('npcs', ['none'])
                if "none" not in npcs:
                    for npc in npcs:
                        await ctx.send(f"{npc} is here")
                else:
                    await ctx.send("There are no NPCs here.")
            else:
                await ctx.send("You are in an unknown area, and there is no information available.")

        other_players = [user for user in user_data_RPG if
                         user != user_id and user_data_RPG[user]['x'] == x and user_data_RPG[user]['y'] == y]
        if other_players:
            await ctx.send(f"Players here: {', '.join(other_players)}")
        else:
            await ctx.send("There are no other players here.")
    except Exception as e:
        await ctx.send("An error occurred while looking around. Please try again later.")
        logger.error(f"Error in look command: {e}")

@bot.slash_command(name="talk", description="Talk to an NPC")
async def talk(ctx: SlashContext, npc: str):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if npc in dialouges:
            npc_dialogue = dialouges[npc]
            view = discord.ui.View()

            for option in npc_dialogue.keys():
                button = discord.ui.Button(label=option, style=discord.ButtonStyle.blurple)

                async def button_callback(interaction, option=option):
                    if interaction.user == ctx.author:
                        if option == "Quest":
                            current_quest = user_data_RPG[user_id].get("current_quest", None)
                            if current_quest and current_quest["progress"] == current_quest["amount"]:
                                await interaction.response.send_message(npc_dialogue[option]["clear"], ephemeral=True)
                            else:
                                quest_info = npc_dialogue[option]
                                await quest(ctx, quest_info["enemy"], quest_info["amount"], quest_info)
                        else:
                            await interaction.response.send_message(npc_dialogue[option], ephemeral=True)
                    else:
                        await interaction.response.send_message("You cannot click this button!", ephemeral=True)

                button.callback = button_callback
                view.add_item(button)

            await ctx.send(f"Talking to {npc}. Please choose an option:", view=view)
        else:
            await ctx.send("That isn't a valid NPC.")
    except Exception as e:
        await ctx.send("An error occurred while talking. Please try again later.")
        logger.error(f"Error in talk command: {e}")

@bot.slash_command(name="help", description="Provides a list of all the commands")
async def help(ctx: SlashContext):
    await ctx.send("\nHere is a list of all the commands:"
                   "\n- help - provides a list of all the commands."
                   "\n- initialize - initializes the bot."
                   "\n- ping - returns pong."
                   "\n- move <direction> <amount> - lets you move through the map."
                   "\n- rest <amount> - lets you recharge your energy."
                   "\n- look - describes your surroundings including npcs and items."
                   "\n- talk <npc> - lets you talk to npcs")

@bot.slash_command(name="stats", description="Display user stats")
async def stats(ctx: SlashContext):
    try:
        user_id = str(ctx.author.id)
        user_data_RPG = load_data()

        if user_id not in user_data_RPG:
            await ctx.send("You need to initialize first with /initialize.")
            return

        current_quest = user_data_RPG[user_id].get("current_quest", None)
        if current_quest:
            enemy = current_quest["enemy"]
            amount = current_quest["amount"]
            progress = current_quest["progress"]
            await ctx.send(f"\nPosition: {user_data_RPG[user_id]['x']}, {user_data_RPG[user_id]['y']}"
                           f"\nHealth: {user_data_RPG[user_id]['player_health']} / {user_data_RPG[user_id]['max_hp']}"
                           f"\nAttack: {user_data_RPG[user_id]['player_attack']}"
                           f"\nDexterity: {user_data_RPG[user_id]['player_dexterity']}"
                           f"\nEnergy: {user_data_RPG[user_id]['player_energy']} / {user_data_RPG[user_id]['max_energy']}"
                           f"\nQuest: {enemy} {progress} / {amount}")
        else:
            await ctx.send(f"\nPosition: {user_data_RPG[user_id]['x']}, {user_data_RPG[user_id]['y']}"
                           f"\nHealth: {user_data_RPG[user_id]['player_health']} / {user_data_RPG[user_id]['max_hp']}"
                           f"\nAttack: {user_data_RPG[user_id]['player_attack']}"
                           f"\nDexterity: {user_data_RPG[user_id]['player_dexterity']}"
                           f"\nEnergy: {user_data_RPG[user_id]['player_energy']} / {user_data_RPG[user_id]['max_energy']}"
                           f"\nQuest: You don't have any quests.")
    except Exception as e:
        await ctx.send("An error occurred while displaying stats. Please try again later.")
        logger.error(f"Error in stats command: {e}")

@bot.event
async def on_disconnect():
    save_data(user_data_RPG)

# Run the bot
bot.start()