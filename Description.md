# DiscordRPG

DiscordRPG is a Python-based role-playing game bot for Discord that lets users interact and play within a text-based RPG environment directly in their Discord server.

## Functionalities:
- **Initialize the Bot:** `!initialize`
- **Ping the Bot:** `!ping`
- **Move Your Character:** `!move <direction> <amount>`
- **Rest to Recharge Energy:** `!rest <amount>`
- **Look Around:** `!look`
- **Talk to NPCs:** `!talk <npc>`
- **Set Your Character's Name:** `!name <name>`
- **Leave/Enter Buildings:** `!leave <place> / !enter <place>`
- **Check Your Stats:** `!stats`
- **Get Help:** `!help`

## Creating New Biomes, NPCs, and Places
### Biomes: 
Biomes are defined in the biomes dictionary. Each biome has attributes like enemies, description, look description, frequency, and area. Adding a new biome involves defining these attributes for the new biome.
### NPCs: 
NPCs are managed in the dialouges dictionary. Each NPC has dialogues and potential quests. Adding a new NPC involves creating a new entry in this dictionary with their dialogues and quest attributes.
### Places: 
Places are structured in the places dictionary. Each place has attributes like description, items, NPCs, coordinates, and optionally, enter and leave coordinates. Adding a new place involves defining these attributes for the new place.
Creating new biomes, NPCs, and places is straightforward by updating the respective dictionaries in the main.py file.

You can add this description to your repository's README.md file or in the repository description on GitHub.

