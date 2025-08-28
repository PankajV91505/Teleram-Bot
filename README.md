#  **YouTube Video Downloader (Telegram Bot + Terminal)**

This project is a **multi-mode YouTube video downloader** that supports:
- Download via **Telegram Bot**
- Download via **Terminal (CLI)**
- Resume downloads (if interrupted or cancelled by mistake)
- Support for **YouTube Shorts** & normal videos
- Organised downloads into `downloads/` folder

---

##  **Features**
- **Telegram Bot Mode (1):**  
  Run the bot and send YouTube links to download videos directly.

- **Terminal Downloader Mode (2):**  
  Paste YouTube video/shorts links in the terminal to download.

- **YouTube Shorts Support:**  
  Special handling for YouTube Shorts videos.

- **Efficient Large File Handling:**  
  Works with large files (GBs in size) with resume support.

---

##  **Installation**

1. Clone this repo:
   ```bash
   git clone https://github.com/your-username/telegram-youtube-downloader.git
   cd telegram-youtube-downloader
    ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

