# HPY Science Bot

HPY Science Bot is a multi-purpose educational Discord bot focused on Math, Physics, and Chemistry.
It provides quick, interactive tooling for symbolic math, unit conversions, simple physics utilities,
and chemical equation balancing.

Disclaimer: This bot is for educational use only and does not guarantee fully correct answers.
Always verify results with reliable sources, especially for coursework, exams, laboratory work, or professional use.

## Core capabilities

### Math
Math commands are intended for symbolic and algebraic computation. Typical use cases:
- Simplifying expressions
- Solving equations
- Differentiation and integration
- Limits and series expansions
- Solving ordinary differential equations (ODEs)

### Physics
Physics commands focus on practical utilities:
- Physical constants lookup
- Unit conversion with autocomplete
- Simple helpers such as Ohm’s law and basic kinematics workflows (if present in your physics cog)

### Chemistry
Chemistry commands focus on balancing chemical equations:
- Balances equations by conserving each element using a linear algebra approach
- Outputs the smallest whole-number coefficients when possible

## Help system

The bot provides an interactive help menu via:

- /help

This command displays an embed explaining the bot’s purpose and usage. It includes topic buttons
(Math, Physics, Chemistry). Clicking a topic button switches the embed to a detailed guide for that topic,
including command lists and usage examples.

The help pages also include the educational disclaimer.

## Command registration and removing old commands

Discord slash commands are registered on Discord’s side. When you rename or remove commands in code,
Discord may continue showing older commands until you re-sync.

This project supports two sync modes:

1) Development guild sync (recommended for testing)
   - Syncs commands to a single test server quickly.
   - Typically updates appear almost immediately in that server.

2) Optional global sync (use only when you need it)
   - Global commands can take longer to propagate/update.
   - Use global sync when you need to remove or update old global commands that still appear.

Environment variable:
- SYNC_GLOBAL_ON_START
  - If set to 1/true, the bot will sync global commands at startup.
  - Keep this off during normal development; turn it on temporarily when you need to update global commands.

## Presence (status text)

The bot’s presence text is configurable via:
- PRESENCE_TEXT

Example:
- PRESENCE_TEXT=try /help

This is applied when the bot becomes ready.

## Requirements

- Python 3.10 or newer
- discord.py
- sympy (for math)
- pint (for units)
- python-dotenv (for environment configuration)

Install dependencies:
- pip install -r requirements.txt

## Installation

1) Clone the repository
   - git clone <your-repo-url>
   - cd <your-repo-folder>

2) Create and activate a virtual environment
   - python -m venv venv
   - Windows:
     - venv\Scripts\activate
   - Linux/macOS:
     - source venv/bin/activate

3) Install requirements
   - pip install -r requirements.txt

## Configuration

Create a .env file in the project root:

TOKEN=YOUR_DISCORD_BOT_TOKEN
DEV_GUILD_ID=YOUR_TEST_GUILD_ID
SYNC_GLOBAL_ON_START=0
PRESENCE_TEXT=try /help

Notes:
- TOKEN is your bot token from the Discord Developer Portal.
- DEV_GUILD_ID is the server (guild) ID where you want fast command syncing during development.
- Keep SYNC_GLOBAL_ON_START disabled (0) unless you explicitly need to refresh global commands.

## Running the bot

- python main.py

Once the bot is online:
- Use /help to open the interactive guide.

## Project structure

discord-science-bot/
  main.py
  requirements.txt
  .env
  cogs/
    help.py
    math.py
    physics.py
    chemistry.py
  utils/
    (optional helpers)

## Troubleshooting

1) Old commands still show in Discord
- Ensure DEV_GUILD_ID is set correctly.
- Restart the bot so it re-syncs the dev guild commands.
- If old commands are global, temporarily set SYNC_GLOBAL_ON_START=1, restart once, then set it back to 0.

2) Commands do not appear in the guild
- Confirm the bot was invited with the applications.commands scope.
- Confirm the bot has permission to use slash commands in that server.
- Confirm your cogs load successfully (check logs).

3) Math parsing issues
- Wrap expressions containing spaces in quotes.
- Prefer x as the main variable for algebra/calc expressions.
- Use y only when working with ODEs if your math implementation reserves y for that purpose.

## License

MIT License.
