
# HTTP Directory Explorer for The Sims Mods

  

> [!IMPORTANT]

>  **Credits & Acknowledgments**

> This tool is designed to work with the content provided by various **The Sims Content Creators** whose work is archived at [Must Be Destroyed (The Booty)](http://paysites.mustbedestroyed.org). We acknowledge the immense creativity of the modding community and the archival efforts of the website.

  

---

  

## 🌐 Project Overview

  

**HTTP Directory Explorer** is a robust Python-based CLI tool specifically designed for navigating and downloading content from AutoIndex-style directory listings. While it can be used for any compatible server, it is pre-configured for efficient retrieval of The Sims custom content from community archives.

  

## ✨ Features

  

-  **📂 Interactive Navigation**: Browse remote directories with a simple, numbered interface.

-  **📥 Smart Downloading**:

-  **Recursive Download**: Grab entire folder structures with a single command.

-  **Multi-selection**: Download specific lists of files (e.g., `1,3,5`).

-  **Batch Download**: Download all files in the current view.

-  **⏯️ Resume Support**: interupted downloads? No problem. The tool automatically resumes from where it left off.

-  **📊 Real-time Progress**: Visual feedback via `tqdm` progress bars for every file.

-  **💾 Session History**: Automatically saves your last visited location to resume your exploration later.

-  **🛡️ Conflict Handling**: Skips existing files if sizes match, saving bandwidth and time.

  

## 🛠️ Requirements

  

-  **Python 3.7+**

-  **Dependencies**:

```bash

pip install -r requirements.txt

```

*(Requires `tqdm` and `beautifulsoup4`)*

  

## 🚀 Quick Start

  

1.  **Clone the repository** (or download the files).

2.  **Install dependencies**.

3.  **Run the explorer**:

```bash

python main.py

```

*or use the [main.exe](https://github.com/1downy/TheSimsMods/releases/tag/1.0)* without installing anything


## ⚖️ Disclaimer

  

> [!WARNING]

> This software is intended for personal archival and educational purposes. The developers of this tool are not affiliated with Electronic Arts, The Sims, or any specific content creators. Use responsibly.
