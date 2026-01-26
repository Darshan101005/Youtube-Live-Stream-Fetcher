<div align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/2/20/YouTube_2024.svg" width="200" alt="YouTube Logo">
  <h1>YouTube Live HLS Fetcher</h1>
  <p>
    <b>A lightweight Flask API to extract and proxy live m3u8 streams from YouTube.</b>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Flask-2.0%2B-green?style=for-the-badge&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/yt--dlp-Latest-red?style=for-the-badge&logo=youtube" alt="yt-dlp">
  </p>
</div>

---

## ⚡ Overview

This tool allows you to bypass YouTube's restrictions and fetch direct HLS (`.m3u8`) stream URLs for any live video. It includes a built-in retry mechanism to handle connection failures and supports three modes of operation:

1. **Direct Redirect:** Redirects you straight to the raw m3u8 file.
2. **Server Proxy:** Routes traffic through your server (useful for geo-restriction bypass).
3. **External Proxy:** Allows you to supply a custom proxy for the fetch request.

## 🚀 Deployment (VPS / DigitalOcean)

Follow these steps to deploy the application on a Linux VPS.

### 1. Clone & Setup

```bash
git https://github.com/Darshan101005/Youtube-Live-Stream-Fetcher.git
cd Youtube-Live-Stream-Fetcher
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Forever (Background Process)

This command runs the application on Port 8000 in the background, even after you disconnect.

```bash
nohup python3 app.py > /dev/null 2>&1 &
```

### 3. Management Commands

* **Check Status:** `ps aux | grep python`
* **Stop Server:** `pkill -f app.py`

---

## 🔗 API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | Web Interface with ID generator and documentation. |
| `GET` | `/{ID}` | Redirects immediately to the stream URL. |
| `GET` | `/{ID}/proxy` | Proxies the stream through the server (Restream). |
| `GET` | `/{ID}/proxy/{PROXY_URL}` | Fetches the stream using an external HTTP proxy. |

### Supported Identifiers

* **Video ID:** `VNzHENanD0g`
* **Channel Handle:** `@polimernews`
* **Channel ID:** `UCttspZesZIDEwwpVIgoZtWQ`

---
## UI/UX

<img width="1919" height="864" alt="image" src="https://github.com/user-attachments/assets/bb256f97-5235-499d-9b2e-4c462394b4fd" />
<img width="1918" height="866" alt="image" src="https://github.com/user-attachments/assets/6646bc02-ebb1-4d65-a9bc-74b975b37c3a" />

## ⚙️ Configuration

The application runs on **Port 8000** by default. To change this, edit the bottom of `app.py`:

```python
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
```

## 🛠️ Retry Logic

The system automatically attempts to fetch the manifest **5 times** with a 2-second delay between attempts. If those fail, it waits **10 seconds** before a final attempt to ensure high availability for unstable streams.
