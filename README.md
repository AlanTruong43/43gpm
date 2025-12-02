# 🚀 43GPM Profile Dashboard

**Complete Batch Automation System for 43GPM (GPM Login) Antidetect Browser**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-Free-green.svg)](LICENSE)

A modern web-based dashboard for managing antidetect browser profiles and running batch automation tasks with multi-threading support.

![Dashboard](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)

---

## ✨ Key Features

### 📋 **Profile Management**
- View, search, and filter browser profiles
- Open/close profiles with one click
- Real-time status monitoring
- Error handling with detailed messages

### 🚀 **Batch Automation** (Core Feature)
- **Multi-profile selection** - Run automation on multiple profiles
- **Multi-threading** - Process 1-10 profiles simultaneously
- **Queue-based processing** - Automatic task management
- **Individual logging** - Separate logs for each profile
- **Auto open/close** - Profiles managed automatically
- **Retry mechanism** - Auto-retry on errors (0-5 attempts)
- **Auto-close on error** - Configurable error handling

### 📊 **Real-time Monitoring**
- **Live progress tracking** - Updates every 1 second
- **Live logs** - See automation steps as they happen
- **Status indicators** - Clear visual feedback
- **Metrics** - Total, Pending, Running, Completed, Error counts

### 🎨 **Modern UI/UX**
- Clean web interface
- Responsive design
- Real-time updates
- Color-coded status
- Expandable logs

---

## 🎯 Why This Dashboard?

### vs. Built-in GPM Automation:

| Feature | GPM Auto | This Dashboard |
|---------|----------|----------------|
| Multi-profile | ✅ | ✅ |
| Multi-threading | ✅ | ✅ Better (1-10 threads) |
| Individual logs | ❌ | ✅ **Detailed** |
| Real-time updates | ⚠️ Basic | ✅ **Live every 1s** |
| Custom projects | ❌ Limited | ✅ **Full Python** |
| Error handling | ✅ | ✅ **Better** |
| UI/UX | ⚠️ Basic | ✅ **Modern Web** |
| Open source | ❌ | ✅ |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- 43GPM (GPM Login) running on port 19995
- Git (optional)

### Quick Start

```bash
# Clone repository
git clone https://github.com/AlanTruong43/43gpm.git
cd 43gpm

# Install dependencies
pip install -r requirements.txt

# Start dashboard
streamlit run dashboard.py

# Or use the batch file (Windows)
START_DASHBOARD.bat
```

Dashboard will open at: **http://localhost:8501**

---

## 🎮 Usage

### 1️⃣ Profile Management

Navigate to **"Profiles"** tab:
- View all profiles with filters
- Open/close profiles
- See profile details
- Check browser status

### 2️⃣ Batch Automation

Navigate to **"Batch Automation"** tab:

**Configure:**
- Select automation project (e.g., twitter.py)
- Set number of threads (1-10)
- Enable/disable auto-close on error
- Set retry count (0-5)

**Select Profiles:**
- Multi-select profiles from list
- Profiles will run in order

**Start & Monitor:**
- Click "▶️ Start Automation"
- Watch real-time progress
- See live logs for each profile
- Monitor success/error counts

### 3️⃣ Status Monitoring

Navigate to **"Status"** tab:
- View running profiles
- See debug addresses
- Quick close buttons
- System information

---

## 🔧 Configuration

### Automation Settings

```python
# In dashboard UI:
Number of Threads: 1-10        # Parallel execution
Auto Close on Error: Yes/No    # Close profile on error
Retry on Error: 0-5            # Retry attempts
```

### Creating Custom Projects

Create a new file in `project/` folder:

```python
# project/instagram.py
import encoding_fix  # Fix Windows encoding

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def run(profile_data):
    """
    Main entry point - REQUIRED
    
    Args:
        profile_data: Dict with profile info
            - profile_id: Profile ID
            - profile_name: Profile name
            - remote_debugging_address: "127.0.0.1:port"
            - browser_location: Path to browser
            - driver_path: Path to driver
    """
    # Connect to opened browser
    chrome_options = Options()
    chrome_options.add_experimental_option(
        "debuggerAddress",
        profile_data['remote_debugging_address']
    )
    
    driver = webdriver.Chrome(options=chrome_options)
    
    # Your automation logic here
    driver.get("https://instagram.com")
    # ... automation steps ...
    
    # DON'T call driver.quit()
    # Dashboard handles closing
```

Dashboard will auto-detect new projects!

---

## 📊 Performance

### Speed
- **1 thread**: Sequential processing (~10-15s per profile)
- **5 threads**: 5 profiles in ~10-15s (5x faster)
- **10 threads**: 10 profiles in ~10-15s (10x faster)

### Resources
- RAM: ~100-200MB per profile
- CPU: Moderate usage
- Network: Depends on automation tasks

### Example
```
10 profiles with 5 threads:
  Traditional: ~2 minutes (sequential)
  Dashboard: ~20 seconds (parallel)
  Speedup: 6x faster! ⚡
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│   Streamlit Dashboard (UI)      │
│   - Web Interface               │
│   - Real-time Updates           │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│  Automation Runner Engine       │
│  - Multi-threading (1-10)       │
│  - Queue Management             │
│  - Individual Logging           │
│  - Error Handling & Retry       │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│   API Client (GPM Integration)  │
│   - Open/Close Profiles         │
│   - Get Profile Info            │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│   43GPM API (Port 19995)        │
│   - Profile Control             │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│   Chrome/Chromium + Selenium    │
│   = Automation Execution        │
└─────────────────────────────────┘
```

---

## 📁 Project Structure

```
43gpm/
├── dashboard.py              # Main dashboard
├── api_client.py             # 43GPM API client
├── automation_runner.py      # Batch automation engine
├── encoding_fix.py           # Windows encoding fix
├── check_open_profiles.py    # Profile management tool
│
├── project/                  # Automation projects
│   └── twitter.py           # Example project
│
├── api/                      # API documentation
│   ├── profile_list_api.txt
│   ├── open_profile_api.txt
│   └── ...
│
├── Documentation/            # Guides
│   ├── README.md
│   ├── BATCH_AUTOMATION_GUIDE.md
│   ├── QUICK_START_BATCH.txt
│   ├── PROJECT_OVERVIEW.md
│   └── ...
│
└── requirements.txt          # Dependencies
```

---

## 📚 Documentation

### Quick Start
- [QUICK_START_BATCH.txt](QUICK_START_BATCH.txt) - Fast getting started guide
- [HƯỚNG_DẪN.txt](HƯỚNG_DẪN.txt) - Vietnamese guide

### Detailed Guides
- [BATCH_AUTOMATION_GUIDE.md](BATCH_AUTOMATION_GUIDE.md) - Complete automation guide
- [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md) - Technical overview
- [REALTIME_UPDATES_GUIDE.txt](REALTIME_UPDATES_GUIDE.txt) - Real-time features
- [PROFILE_CLOSE_GUIDE.md](PROFILE_CLOSE_GUIDE.md) - Auto-close mechanism
- [DATA_CLEANUP_GUIDE.txt](DATA_CLEANUP_GUIDE.txt) - Data management

### Technical
- [ENCODING_FIX_README.txt](ENCODING_FIX_README.txt) - Windows encoding fix
- [GIT_GUIDE.txt](GIT_GUIDE.txt) - Git commands reference
- [CHANGELOG.md](CHANGELOG.md) - Version history

---

## 🎯 Use Cases

### Social Media Automation
- Twitter: Auto post, like, follow
- Instagram: Engagement automation
- Facebook: Content scheduling
- LinkedIn: Connection automation

### E-commerce
- Product monitoring
- Price tracking
- Auto checkout
- Inventory alerts

### Data Collection
- Web scraping
- Market research
- Competitor analysis
- Data extraction

### Testing
- Multi-account testing
- Browser compatibility
- Performance testing
- Load testing

---

## 🛠️ Tools & Utilities

### Check Open Profiles
```bash
python check_open_profiles.py
```
Lists all currently open profiles

### Close All Profiles
```bash
python check_open_profiles.py --close-all
```
Force close all open profiles

### Encoding Fix Test
```bash
python encoding_fix.py
```
Test Unicode support on Windows

---

## ⚙️ System Requirements

- **OS**: Windows 10/11 (Primary), Linux, macOS
- **Python**: 3.8 or higher
- **RAM**: 4GB+ (8GB+ recommended)
- **CPU**: 4+ cores recommended
- **Storage**: 1GB+ free space
- **Internet**: Stable connection
- **43GPM**: Installed and running

---

## 🐛 Troubleshooting

### Dashboard won't start?
```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Try different port
streamlit run dashboard.py --server.port 8502
```

### Can't connect to 43GPM?
- Ensure 43GPM is running
- Check port 19995 is not blocked
- Try: http://127.0.0.1:19995/api/v3/groups

### Profile won't open?
- Download browser core in 43GPM (Settings → Browser Core)
- Check profile exists in 43GPM
- Restart 43GPM

### Encoding errors?
- The project includes `encoding_fix.py` that auto-fixes Windows console encoding
- Already imported in all project files

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

---

## 📝 License

This project is free for personal use.

---

## 🙏 Acknowledgments

- Built to improve and extend 43GPM (GPM Login) automation capabilities
- Uses Streamlit for modern web interface
- Selenium for browser automation

---

## 📞 Support

For issues or questions:
1. Check [Documentation](PROJECT_OVERVIEW.md)
2. Review [Troubleshooting](#-troubleshooting)
3. Check GitHub Issues
4. Read the guides in the repo

---

## 🎉 Version

**Version 1.0.0** - Production Ready

### What's Included:
- ✅ Complete batch automation system
- ✅ Multi-threading support (1-10 threads)
- ✅ Real-time monitoring (1s updates)
- ✅ Individual profile logging
- ✅ Auto open/close profiles
- ✅ Error handling & retry
- ✅ Modern web dashboard
- ✅ Complete documentation
- ✅ Example projects
- ✅ Windows encoding fix
- ✅ Management tools

### Stats:
- 27+ files
- 5,200+ lines of code
- 10+ documentation files
- Production-ready

---

## 🚀 Get Started Now!

```bash
# Clone and run
git clone https://github.com/AlanTruong43/43gpm.git
cd 43gpm
pip install -r requirements.txt
streamlit run dashboard.py
```

**Then open:** http://localhost:8501

---

<div align="center">

**⭐ Star this repo if you find it useful!**

Made with ❤️ for the automation community

[Report Bug](https://github.com/AlanTruong43/43gpm/issues) · [Request Feature](https://github.com/AlanTruong43/43gpm/issues)

</div>
