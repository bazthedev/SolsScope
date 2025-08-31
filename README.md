<div align="center">
  <img src="https://raw.githubusercontent.com/bazthedev/SolsScope/refs/heads/main/icon.ico" alt="SolsScope Icon" width="128" height="128">

  # SolsScope

  **The most advanced Sols RNG Macro**

  Advanced automation featuring auto-craft, auto-purchase, aura/biome detection, and more. The next evolution of dolphSol for Eon 1+.

  [![Downloads](https://img.shields.io/github/downloads/bazthedev/SolsScope/total)](https://github.com/bazthedev/SolsScope/releases)
  [![Release](https://img.shields.io/github/v/release/bazthedev/SolsScope)](https://github.com/bazthedev/SolsScope/releases/latest)
  [![License](https://img.shields.io/github/license/bazthedev/SolsScope)](LICENSE)
  [![Stars](https://img.shields.io/github/stars/bazthedev/SolsScope)](https://github.com/bazthedev/SolsScope/stargazers)

</div>

---

## Features

### Core Features
- **Aura Detection** - Automatic detection and notification of rare auras
- **Biome Detection** - Real-time biome monitoring and alerts
- **Auto-Crafting** - Automated potion crafting with multiple recipe support
- **Auto-Purchase** - Intelligent item purchasing from merchants
- **Merchant Detection** - Screenshot and stock monitoring (requires Merchant Teleporter)

### Advanced Features
- **Anti-Kick Protection** - Prevents automatic disconnection
- **Custom Plugin System** - Extensible command framework
- **Multi-Webhook Support** - Forward notifications to multiple Discord channels
- **Automatic Updates** - Self-updating aura database
- **Periodic Screenshots** - Automated inventory and storage documentation

### Quality of Life
- **Configuration GUI** - User-friendly settings interface
- **Multi-Monitor Support** - Compatible with most 16:9 displays
- **Platform Detection** - Automatic MS Store/Player version detection
- **Disconnect Prevention** - Maintains stable connection
- **Auto Biome Items** - Automated Biome Randomizer and Strange Controller usage

---

## System Requirements

- **Operating System**: Windows 10/11
- **Display**: 1080p minimum (1440p recommended)
- **Python**: Version 3.12 or newer (versions 3.13 and above require slightly steps to setup)
- **Roblox**: Roblox Player is recommended (UWP version supported with limitations)

---

## Quick Start

1. **Download** the [latest release](https://github.com/bazthedev/SolsScope/releases/latest)
2. **Install Python** 3.12 or newer from [python.org](https://python.org)
3. **Install dependencies**:
   ```bash
   py -m pip install -r requirements.txt
   ```
4. **Run the application**:
   ```bash
   python main.py
   ```
5. **Configure webhook**: Create a Discord webhook and add the URL to the WEBHOOK_URL field
6. **Start automation** and enjoy!

---

## Support & Documentation

- **Video Guide**: [Setup Tutorial](https://www.youtube.com/watch?v=Y12uiAbqMDc)
- **Discord Support**: [Join our server](https://discord.gg/8khGXqG7nA)
- **Wiki**: [Detailed documentation](https://github.com/bazthedev/SolsScope/wiki)

---

## Troubleshooting

<details>
<summary><strong>Common Issues</strong></summary>

**Merchant Detection Issues**
- The macro uses OCR for item detection. Increase screen resolution for better accuracy.

**Dual Monitor Problems**
- Ensure Roblox runs on your primary display. Check via Windows Settings > System > Display.

**Platform Compatibility**
- Designed for Windows 10/11. Other platforms are not supported.

**Aura Download Freezing**
- Manually download `auras.json` and place it in `%localappdata%\Baz's Macro\`

**Macro Won't Stop**
- The macro safely terminates threads to prevent data loss. Wait for the current task to finish.

**Update Issues**
- If experiencing problems, set `skip_dl` to `true` in settings.

</details>

<div align="center">

  **© 2025 Scope Development. All rights reserved.**

</div>
