# 🎮 Aether Strife: Origins

A complete 2D Pre-MOBA game built with Python and Pygame. Inspired by the classic custom maps that birthed the MOBA genre (Aeon of Strife, Defense of the Ancients).

![Version](https://img.shields.io/badge/version-9.0-gold)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Pygame](https://img.shields.io/badge/pygame-2.5+-green)

## 🌟 Features

### Core Gameplay
- ✅ **Right-click movement / Left-click attack** (Authentic MOBA controls)
- ✅ **Attack-Move command** (A + Left-Click)
- ✅ **5 unique heroes** with distinct playstyles and passives
- ✅ **3 lanes** (Top, Mid, Bot) with proper minion pathing
- ✅ **Towers, Nexuses, and Jungle camps**
- ✅ **Fog of War** with ward-based vision control
- ✅ **Item shop** with 9 items (buy & sell)
- ✅ **Leveling system** (1-16) with XP tracking
- ✅ **Respawn timers** (8 seconds)

### Advanced Systems
- ✅ **Ability Upgrade System** - Choose upgrades at levels 6, 10, 13
- ✅ **Gold Bounties** - Killing spree enemies have bounties
- ✅ **Assist Tracking** - Get gold for helping kill enemies
- ✅ **CC Effects** - Stun, Slow, Root
- ✅ **Recall to Base** - Hold B for 3 seconds to teleport
- ✅ **Neutral Objectives** - Drake (speed buff) & Titan (siege buff)
- ✅ **Enhanced Enemy AI** - Farms jungle, uses all abilities, retreats intelligently

### Quality of Life
- ✅ **Match Timer** - Real-time game clock
- ✅ **Kill Feed** - Top-right notifications
- ✅ **GPM Tracking** - Gold Per Minute display
- ✅ **Minimap** - Live map overview
- ✅ **TAB Stats Panel** - Detailed match stats
- ✅ **Cursor Feedback** - Crosshair over enemies
- ✅ **Particle Effects** - Visual juice for abilities
- ✅ **Screen Shake** - Impact feedback on ultimates
- ✅ **Sound Effects** - Procedurally generated audio
- ✅ **Pause Menu** - ESC to pause
- ✅ **Settings Menu** - Volume, smart cast, range indicators
- ✅ **Game Modes** - Standard Match or 1v1 Last Hit Duel

## 🦸 Heroes

| Hero | Role | Passive | Playstyle |
|------|------|---------|-----------|
| **Bruiser** | Tank/CC | Iron Will: Every 3rd attack heals | Front-line fighter with stuns and shields |
| **Mage** | Burst | Spellweave: Abilities boost next attack | Long-range skillshots and AoE damage |
| **Assassin** | Burst/Mobile | Shadow Step: +20% speed in fog | Dash-based burst damage |
| **Support** | Healer/Utility | Tally: Earn gold on heals | Healing, speed boosts, crowd control |
| **Marksman** | DPS | Focus: Attacks grant stacking AD | Long-range sustained damage |

## 🎮 Controls

| Key | Action |
|-----|--------|
| **Right-Click** | Move to location |
| **Left-Click** | Attack target |
| **A + Left-Click** | Attack-Move |
| **Q / W / E / R** | Cast abilities |
| **B** | Open shop (at base) / Recall (elsewhere) |
| **V** | Place ward |
| **F** | Use health potion |
| **TAB** | View stats panel |
| **ESC** | Pause menu |
| **S** (in shop) | Sell item |

## 🚀 Installation

### Quick Start (Automated)
```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh

# Navigate to the project
cd aether_strife_origins

# Run the game
./run.sh
```

### Manual Installation
```bash
# Clone or download the project
cd aether_strife_origins

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate sound effects
python scripts/generate_sounds.py

# Run the game
python src/game.py
```

## 📁 Project Structure

```
aether_strife_origins/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── run.sh                    # Game launcher
├── setup.sh                  # Project setup script
├── src/
│   └── game.py              # Main game file (all features)
├── assets/
│   └── sounds/              # Sound effects (auto-generated)
│       ├── attack.wav
│       ├── ability.wav
│       ├── kill.wav
│       ├── purchase.wav
│       ├── levelup.wav
│       └── upgrade.wav
├── scripts/
│   └── generate_sounds.py   # Procedural sound generator
└── docs/
    └── (future documentation)
```

## 🎯 How to Play

### Objective
Destroy the enemy **Nexus** (large structure in their base) while protecting your own.

### Early Game
- Focus on **last-hitting** minions for gold (+50g per last hit)
- **Deny** your own minions when below 20% HP to deny enemy gold
- Buy items from the shop at your base (press B near base)

### Mid Game
- Fight over the **Drake** (spawns at 4:00) for movement speed buff
- Place **wards** to gain vision of the map
- Look for upgrade opportunities at levels 6, 10, and 13

### Late Game
- Contest the **Titan** (spawns at 10:00) for siege buff
- Group up for team fights
- Push lanes and destroy the enemy Nexus

### Tips
- Use the **minimap** (bottom-right) to track the game state
- Hold **TAB** to view detailed stats
- **Recall** (hold B) to return to base when low on HP
- Buy **Health Potions** for sustain in lane
- **Wards** are crucial for vision control

## 🔧 Configuration

Edit settings in-game via the Settings menu (accessible from pause or menu screens):
- **Master Volume**: 0-100%
- **Smart Cast**: Cast abilities instantly or with indicator
- **Range Indicators**: Show attack/ability ranges

## 🐛 Known Issues

- Enemy AI could be more sophisticated
- Some ability upgrades are hero-specific
- Sound generation requires numpy

## 🤝 Contributing

This is a complete single-player prototype. To extend it:
1. Add multiplayer via sockets or Photon
2. Add more heroes and abilities
3. Implement advanced AI with state machines
4. Add replay system
5. Create custom maps

## 📜 License

MIT License - Feel free to use, modify, and distribute.

## 🙏 Credits

Inspired by:
- **Aeon of Strife** (StarCraft custom map)
- **Defense of the Ancients** (Warcraft III custom map)
- **League of Legends** and **Dota 2**

Built with:
- Python 3.8+
- Pygame 2.5+
- NumPy (for sound generation)

---

**Enjoy the game! May your last-hits be perfect and your team fights victorious!** 🎮⚔️
