# DiscordRPG

![rpgbotlogo](https://github.com/user-attachments/assets/ccbcb242-eaa3-4efd-af4f-b98603e89338)

DiscordRPG is a Python-based role-playing game bot for Discord that lets users interact and play within a text-based RPG environment directly in their Discord server.

## Installation Guide


1. **Clone the Repository**
```sh
git clone https://github.com/DrDehydratedWater/DiscordRPG.git
cd DiscordRPG
```
2. **Create a Virtual Environment** (optional but recommended)
```sh
python -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate
```
3. **Install Dependencies**

```sh
pip install -r requirements.txt
```
4. **Set Up Bot Token**

    Create a file `secret/bot_token.env`.
  
    Add your Discord bot token to the file:
    
   `YOUR_BOT_TOKEN`
  
5. **Run the Bot**

```sh
python main.py
```
## Usage
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
