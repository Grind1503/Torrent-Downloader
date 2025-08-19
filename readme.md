# Torrent Search & Downloader (with LLM-powered Query Expansion)

## 📌 Overview
This project is a **torrent search and download automation tool** powered by:
- **LLM (Large Language Model)** for turning natural language queries into optimized torrent search keywords.
- **1337x torrent search scraping** to fetch results.
- **qBittorrent WebUI API** for automatically adding torrents to your download client.
- **Full-stack app** with:
  - **Backend** (Flask + MCP server) for orchestrating LLM + torrent search + downloads.
  - **Frontend** (React + Vite + Material UI) for a clean UI to enter queries and monitor results.

### 🔑 Key Features
- Accepts **natural language queries** (e.g., “Download all Harry Potter movies”).
- LLM (via Perplexity API) expands queries into **torrent-ready keywords** and categorizes them (Movies, Games, TV, Music, etc.).
- Scrapes results from **1337x** (using `cloudscraper` to bypass Cloudflare).
- Auto-fetches **magnet links** and sends them to **qBittorrent** for download.
- Simple **web interface** for users to enter queries and track torrent status.

---

## 🗂 Project Structure
```
TORRENT_SEARCH/
│── backend/
│   ├── llmclient.py       # LLM client for query expansion (Perplexity API)
│   ├── middle.py          # Flask middleware between frontend ↔ backend tools
│   ├── server.py          # MCP server for torrent search + qBittorrent download
│   └── .env               # Environment variables (API keys, etc.)
│
│── frontend/
│   ├── src/
│   │   ├── App.jsx        # Main React UI logic
│   │   ├── App.css        # Styling
│   │   └── main.jsx       # Entry point
│   ├── public/
│   ├── package.json       # Frontend dependencies
│   └── vite.config.js     # Vite configuration
│
│── requirements.txt       # Python dependencies
│── README.md              # Project documentation
```

---

## ⚙️ Installation & Setup

### 1. Clone Repository
```bash
git clone https://github.com/Grind1503/Torrent-Downloader.git
cd torrent-search
```

### 2. Backend Setup
#### Create Virtual Environment (Use Python version 3.11)
```bash
cd backend
python -m venv venv
source venv/bin/activate   # On Linux/Mac
venv\Scripts\activate      # On Windows
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Configure Environment
Create a `.env` file in `backend/` with:
```env
PERPLEXITY_API_KEY=your_perplexity_api_key_here
```

#### Run Servers
- Start MCP server (torrent search + download):
```bash
python server.py
```
- Start Flask middleware (LLM + MCP bridge):
```bash
python middle.py
```

By default:
- MCP server runs on `http://localhost:8050`
- Flask middleware runs on `http://localhost:8000`

---

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend will start on `http://localhost:5173`

---

### 4. qBittorrent Setup
- Install [qBittorrent](https://www.qbittorrent.org/).
- Enable **WebUI** in preferences (default: `http://localhost:8080`).
- Configure credentials in `server.py`:
- Make sure the application runs in the background.
```python
QB_URL = "http://localhost:8080"
QB_USER = "admin"
QB_PASS = "adminadmin"
```

---

## 🚀 Usage
1. Open the frontend (`http://localhost:5173`).
2. Enter a query like:
   - `"Download all Marvel movies"`
   - `"Latest Ubuntu ISO"`
   - `"Call of Duty Modern Warfare"`
3. LLM expands it into torrent-ready search terms.
4. MCP server searches 1337x, fetches magnet links, and sends them to qBittorrent.
5. UI shows status of downloads (success/failure).

---

## 🔮 Future Improvements
- Add support for multiple torrent sources beyond 1337x.
- User authentication for private use.
- Advanced filters (seeders, size, quality).
- Automatic notifications when downloads start/finish.

---

## ⚠️ Disclaimer
This project is for **educational purposes only**. Downloading copyrighted material without permission is illegal. The authors are not responsible for any misuse of this tool.
