#  **YouTube Video Downloader (Telegram Bot + Terminal)**

This project is a **multi-mode YouTube video downloader** that supports:
- Download via **Telegram Bot**
- Download via **Terminal (CLI)**
- Resume downloads (if interrupted or cancelled by mistake)
- Support for **YouTube Shorts** & normal videos
- Organised downloads into `downloads/` folder
- **Thumbnail Downloader** (default & custom timestamp)

---

##  **Features**
- **Telegram Bot Mode (1):**  
  Run the bot and send YouTube links to download videos directly.  
  Commands supported:  
  - `/start` → Show help  
  - `/download <YouTube_Link>` → Download video  
  - `/thumbnail <YouTube_Link>` → Get default thumbnail  
  - `/thumbnail <YouTube_Link> <timestamp>` → Get custom thumbnail (HH:MM:SS or seconds)

- **Terminal Downloader Mode (2):**  
  Paste YouTube video/shorts links in the terminal to download.  
  - Choose **video quality**  
  - Optionally choose to **download thumbnail**  

- **YouTube Shorts Support:**  
  Special handling for YouTube Shorts videos.

- **Efficient Large File Handling:**  
  Works with large files (GBs in size) with resume support.

- **Thumbnail Support:**  
  - Default thumbnails are saved automatically in `thumb_downloads/`  
  - Custom thumbnails can be generated at a specific timestamp.  

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

