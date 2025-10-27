# hpy discord bot ⚙️

A multi-purpose educational Discord bot for **Math**, **Physics**, and **Chemistry**, built with Python and Discord.py.  
It evaluates equations, solves differential equations, converts units, and balances chemical reactions.

---

## 🚀 Features

- **Math**  
  - Evaluate or simplify expressions  
  - Compute derivatives, integrals, limits, and series  
  - Solve algebraic and differential equations (1st and 2nd order)

- **Physics**  
  - Access common constants (c, h, k_B, etc.)  
  - Convert units with autocomplete  
  - Apply Ohm’s law and kinematic formulas

- **Chemistry**  
  - Automatically balance chemical equations using linear algebra

- **Help Menu**  
  - `/help guide` shows examples and quick buttons to learn commands

---

## 🧰 Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/discord-science-bot.git
cd discord-science-bot

# Create a virtual environment
python -m venv venv
source venv/bin/activate     # on Linux / macOS
venv\Scripts\activate        # on Windows

# Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Usage

1. Create a Discord bot via the [Discord Developer Portal](https://discord.com/developers/applications).  
2. Copy your bot token and save it in a `.env` file or a secure config file.
3. Run the bot:

```bash
python main.py
```

4. Use slash commands like:
   - `/math calc expr:(2+3)^3`
   - `/phys convert value:10 src_unit:m/s dst_unit:km/h`
   - `/chem balance equation:"Fe + O2 = Fe2O3"`

---

## 🧩 Project Structure

```
discord-science-bot/
├─ main.py
├─ help.py
├─ chemistry.py
├─ physics.py
├─ math.py
├─ safe_sympy.py
├─ requirements.txt
└─ .gitignore
```

---

## 🧠 Requirements

- Python 3.10+
- `discord.py`
- `sympy`
- `pint`

Install everything with:
```bash
pip install discord.py sympy pint
```

---

## 💡 License

MIT License © 2025  
You are free to modify and distribute this project for educational or personal use.
