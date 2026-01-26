from flask import Flask, render_template_string, request, Response, redirect, jsonify
import yt_dlp
import requests
import base64
import time
from urllib.parse import unquote, quote

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Live Fetcher</title>
    <link rel="icon" href="https://upload.wikimedia.org/wikipedia/commons/2/20/YouTube_2024.svg">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg: #f0f2f5; --card: #ffffff; --text: #1c1e21; --accent: #ff0000;
            --input: #f5f6f7; --border: #ddd; --shadow: rgba(0,0,0,0.1);
        }
        [data-theme="dark"] {
            --bg: #0f0f0f; --card: #1e1e1e; --text: #ffffff; --accent: #ff4444;
            --input: #2b2b2b; --border: #333; --shadow: rgba(0,0,0,0.5);
        }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; transition: 0.3s; display: flex; flex-direction: column; min-height: 100vh; }

        nav { width: 100%; padding: 25px; display: flex; justify-content: flex-end; box-sizing: border-box; }
        .theme-btn { 
            background: var(--card); border: 1px solid var(--border); color: var(--text); 
            width: 60px; height: 60px; border-radius: 50%; cursor: pointer; 
            box-shadow: 0 4px 15px var(--shadow); font-size: 24px; display: flex; 
            align-items: center; justify-content: center; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .theme-btn:hover { transform: rotate(45deg) scale(1.1); }
        .theme-btn:active { transform: scale(0.9); }

        .container { flex: 1; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 20px; }
        .card { background: var(--card); padding: 40px; border-radius: 24px; box-shadow: 0 20px 40px var(--shadow); width: 100%; max-width: 450px; text-align: center; position: relative; }

        .logo-main { width: 120px; margin-bottom: 10px; }
        h1 { font-size: 22px; margin-bottom: 30px; font-weight: 600; }

        .user-info { font-size: 11px; opacity: 0.7; margin-bottom: 25px; line-height: 1.6; letter-spacing: 0.5px; }

        .field { margin-bottom: 20px; text-align: left; }
        label { display: block; font-size: 12px; font-weight: 600; margin-bottom: 8px; opacity: 0.7; }

        input, .custom-select { 
            width: 100%; padding: 14px; border-radius: 12px; border: 1px solid var(--border); 
            background: var(--input); color: var(--text); font-size: 15px; outline: none; box-sizing: border-box;
        }

        .select-wrapper { position: relative; }
        select { 
            appearance: none; -webkit-appearance: none; width: 100%; padding: 14px; 
            border-radius: 12px; border: 1px solid var(--border); background: var(--input); 
            color: var(--text); cursor: pointer; outline: none; transition: 0.2s;
        }
        .select-wrapper::after {
            content: '\\f107'; font-family: "Font Awesome 6 Free"; font-weight: 900;
            position: absolute; right: 15px; top: 50%; transform: translateY(-50%); pointer-events: none;
        }

        .radio-group { display: flex; background: var(--input); padding: 5px; border-radius: 14px; margin-bottom: 25px; }
        .radio-group label { 
            flex: 1; text-align: center; padding: 10px; margin: 0; cursor: pointer; border-radius: 10px; 
            transition: 0.3s; font-size: 13px; font-weight: 600; opacity: 1;
        }
        .radio-group input { display: none; }
        .radio-group input:checked + label { background: var(--accent); color: white; }

        button.action-btn { 
            width: 100%; padding: 16px; border-radius: 12px; border: none; 
            background: var(--accent); color: white; font-weight: 600; cursor: pointer; 
            font-size: 16px; transition: 0.3s;
        }
        button.action-btn:hover { opacity: 0.9; transform: translateY(-2px); }

        #result-container { margin-top: 25px; display: none; animation: fadeIn 0.5s; }
        .result-box { 
            background: #000; color: #00ff00; padding: 15px; border-radius: 10px; 
            font-family: monospace; font-size: 12px; position: relative; overflow-wrap: break-word; text-align: left;
        }
        .copy-btn { position: absolute; top: 10px; right: 10px; color: white; cursor: pointer; background: #333; padding: 5px 8px; border-radius: 5px; }

        .docs-link { margin-top: 20px; display: block; color: var(--accent); text-decoration: none; font-size: 13px; font-weight: 600; }

        footer { padding: 30px; text-align: center; font-size: 13px; opacity: 0.7; }
        footer a { color: var(--accent); text-decoration: none; font-weight: 600; }

        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body data-theme="dark">
    <nav>
        <button class="theme-btn" onclick="toggleTheme()"><i class="fas fa-moon" id="t-icon"></i></button>
    </nav>

    <div class="container">
        <div class="card">
            <img src="https://upload.wikimedia.org/wikipedia/commons/2/20/YouTube_2024.svg" class="logo-main">
            <h1>YouTube Live Fetcher</h1>

            <div class="user-info">
                {% if geo.location %}<i class="fas fa-map-marker-alt"></i> {{ geo.location }} <br>{% endif %}
                {% if geo.isp %}<i class="fas fa-network-wired"></i> {{ geo.isp }} <br>{% endif %}
                <i class="fas fa-globe"></i> {{ geo.ip }}
            </div>

            <div class="radio-group">
                <input type="radio" name="goal" id="goal_stream" value="stream" checked onchange="handleGoal()">
                <label for="goal_stream">Stream Mode</label>
                <input type="radio" name="goal" id="goal_output" value="output" onchange="handleGoal()">
                <label for="goal_output">Output Link</label>
            </div>

            <div class="field">
                <label>IDENTIFIER</label>
                <input type="text" id="target" placeholder="@username, Video ID or Channel ID">
            </div>

            <div id="stream-options">
                <div class="field">
                    <label>STREAM MODE</label>
                    <div class="select-wrapper">
                        <select id="mode" onchange="toggleProxyField()">
                            <option value="direct">Direct Redirection</option>
                            <option value="restream">Restream (Server)</option>
                            <option value="proxy">External Proxy</option>
                        </select>
                    </div>
                </div>

                <div class="field" id="proxy_field" style="display:none;">
                    <label>PROXY URL</label>
                    <input type="text" id="proxy_url" placeholder="http://user:pass@ip:port">
                </div>
            </div>

            <button class="action-btn" id="main-btn" onclick="process()">Generate & Action</button>

            <div id="result-container">
                <label>MANIFEST URL</label>
                <div class="result-box">
                    <span id="url-text"></span>
                    <i class="fas fa-copy copy-btn" onclick="copyUrl()"></i>
                </div>
            </div>

            <a href="/docs" class="docs-link"><i class="fas fa-book"></i> Read Documentation</a>
        </div>
        <div id="status" style="margin-top:15px; font-size:13px; color:red; display:none;"></div>
    </div>

    <footer>
        Made with ❤️ by <a href="https://telegram.me/Darshan_101005" target="_blank">@Darshan_101005</a>
    </footer>

    <script>
        function toggleTheme() {
            const b = document.body;
            const icon = document.getElementById('t-icon');
            if(b.getAttribute('data-theme') === 'dark') {
                b.setAttribute('data-theme', 'light');
                icon.className = 'fas fa-sun';
                icon.parentElement.style.transform = 'rotate(180deg)';
            } else {
                b.setAttribute('data-theme', 'dark');
                icon.className = 'fas fa-moon';
                icon.parentElement.style.transform = 'rotate(0deg)';
            }
        }

        function handleGoal() {
            const isOutput = document.getElementById('goal_output').checked;
            document.getElementById('stream-options').style.display = isOutput ? 'none' : 'block';
            document.getElementById('result-container').style.display = 'none';
        }

        function toggleProxyField() {
            const mode = document.getElementById('mode').value;
            document.getElementById('proxy_field').style.display = (mode === 'proxy') ? 'block' : 'none';
        }

        function process() {
            const target = document.getElementById('target').value.trim();
            const isOutput = document.getElementById('goal_output').checked;
            const status = document.getElementById('status');

            if(!target) { alert("Please enter an identifier"); return; }
            status.style.display = 'none';

            if(!isOutput) {
                const mode = document.getElementById('mode').value;
                const proxy = document.getElementById('proxy_url').value.trim();
                let path = "/" + target;
                if(mode === 'restream') path += "/proxy";
                if(mode === 'proxy') path += "/proxy/" + encodeURIComponent(proxy);
                window.location.href = path;
            } else {
                document.getElementById('main-btn').innerText = "Fetching...";
                fetch(`/api/get_url?id=${encodeURIComponent(target)}`)
                .then(r => r.json())
                .then(data => {
                    document.getElementById('main-btn').innerText = "Generate & Action";
                    if(data.success) {
                        document.getElementById('url-text').innerText = data.url;
                        document.getElementById('result-container').style.display = 'block';
                    } else {
                        status.innerText = data.error;
                        status.style.display = 'block';
                    }
                });
            }
        }

        function copyUrl() {
            const text = document.getElementById('url-text').innerText;
            navigator.clipboard.writeText(text);
            alert("URL Copied!");
        }
    </script>
</body>
</html>
"""

DOCS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Documentation | YT Fetcher</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; line-height: 1.6; padding: 40px; max-width: 800px; margin: auto; background: #0f0f0f; color: #eee; }
        h1 { color: #ff4444; border-bottom: 2px solid #333; padding-bottom: 10px; }
        code { background: #222; color: #00ff00; padding: 2px 6px; border-radius: 4px; }
        .endpoint { background: #1e1e1e; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #ff4444; }
        a { color: #ff4444; }
    </style>
</head>
<body>
    <h1>System Documentation</h1>
    <p>This script allows you to obtain direct HLS (.m3u8) manifests for Live streams.</p>

    <h2>1. Supported Identifiers</h2>
    <ul>
        <li><strong>Watch ID:</strong> The 11-digit ID in URL (e.g., <code>VNzHENanD0g</code>)</li>
        <li><strong>Handle:</strong> Channel @username (e.g., <code>@polimernews</code>)</li>
        <li><strong>Channel ID:</strong> Full YouTube ID starting with UC (e.g., <code>UCttspZesZIDEwwpVIgoZtWQ</code>)</li>
    </ul>

    <h2>2. API Endpoints</h2>

    <div class="endpoint">
        <strong>Direct Multi-Quality Redirect</strong><br>
        <code>GET /&lt;identifier&gt;</code><br>
        Example: <code>/VNzHENanD0g</code>
    </div>

    <div class="endpoint">
        <strong>Server-Side Proxy (Restream)</strong><br>
        <code>GET /&lt;identifier&gt;/proxy</code><br>
        Forces all video data to flow through this server.
    </div>

    <div class="endpoint">
        <strong>External Proxy Route</strong><br>
        <code>GET /&lt;identifier&gt;/proxy/&lt;encoded_proxy_url&gt;</code><br>
        Uses a custom HTTP proxy to fetch segments.
    </div>

    <div class="endpoint">
        <strong>Standard M3U8 Alias</strong><br>
        <code>GET /&lt;identifier&gt;/index.m3u8</code><br>
        <code>GET /&lt;identifier&gt;/proxy/index.m3u8</code><br>
        <code>GET /&lt;identifier&gt;/proxy/&lt;proxy_url&gt;/index.m3u8</code>
    </div>

    <p><a href="/">← Back to Home</a></p>
</body>
</html>
"""

def get_geo_info():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
    res = {"ip": ip, "location": None, "isp": None}
    if not ip or ip in ['127.0.0.1', '::1']: return res
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}", timeout=3).json()
        if data.get("status") == "success":
            loc_parts = [data.get("city"), data.get("regionName"), data.get("country")]
            res["location"] = ", ".join([p for p in loc_parts if p])
            res["isp"] = data.get("isp")
    except: pass
    return res

def b64e(s): return base64.urlsafe_b64encode(s.encode()).decode() if s else ""
def b64d(s): return base64.urlsafe_b64decode(s.encode()).decode() if s else ""

def get_yt_link(target, proxy_url=None):
    if target.startswith('@'): url = f"https://www.youtube.com/{target}/live"
    elif target.startswith('UC'): url = f"https://www.youtube.com/channel/{target}/live"
    else: url = f"https://www.youtube.com/watch?v={target}"

    opts = {'quiet': True, 'no_warnings': True, 'nocheckcertificate': True, 'format': 'best'}
    if proxy_url: opts['proxy'] = proxy_url

    for i in range(5):
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                res = info.get('manifest_url') or info.get('url')
                if res: return res
        except:
            pass
        time.sleep(2)

    time.sleep(10)

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('manifest_url') or info.get('url')
    except:
        return None

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE, geo=get_geo_info())

@app.route('/docs')
def docs():
    return render_template_string(DOCS_TEMPLATE)

@app.route('/api/get_url')
def api_get_url():
    target = request.args.get('id')
    url = get_yt_link(target)
    if url: return jsonify({"success": True, "url": url})
    return jsonify({"success": False, "error": "Hs manifest not found"})

@app.route('/<identifier>')
@app.route('/<identifier>/index.m3u8')
def direct_route(identifier):
    url = get_yt_link(identifier)
    if not url: return "Hs manifest not found", 404
    return redirect(url)

@app.route('/<identifier>/proxy')
@app.route('/<identifier>/proxy/index.m3u8')
@app.route('/<identifier>/proxy/<path:ext_proxy>')
@app.route('/<identifier>/proxy/<path:ext_proxy>/index.m3u8')
def proxy_route(identifier, ext_proxy=None):
    p_url = None
    if ext_proxy:
        p_url = unquote(ext_proxy)
        if "https:/" in p_url and "https://" not in p_url: p_url = p_url.replace("https:/", "https://")
        elif "http:/" in p_url and "http://" not in p_url: p_url = p_url.replace("http:/", "http://")
    url = get_yt_link(identifier, proxy_url=p_url)
    if not url: return "Hs manifest not found", 404
    proxies = {"http": p_url, "https": p_url} if p_url else None
    try:
        r = requests.get(url, headers=HEADERS, proxies=proxies, timeout=15)
        if r.status_code != 200: return f"Upstream Error: {r.status_code}", 502
        output = []
        for line in r.text.splitlines():
            if line.startswith("http"):
                p_param = f"&p={b64e(p_url)}" if p_url else ""
                output.append(f"{request.host_url}ts?u={b64e(line)}{p_param}")
            else: output.append(line)
        return Response("\n".join(output), content_type='application/vnd.apple.mpegurl')
    except Exception as e: return f"Fetch Failed: {str(e)}", 500

@app.route('/ts')
def ts_proxy():
    try:
        target = b64d(request.args.get('u'))
        p_str = request.args.get('p')
        proxies = {"http": b64d(p_str), "https": b64d(p_str)} if p_str else None
        r = requests.get(target, headers=HEADERS, stream=True, timeout=25, proxies=proxies)
        def stream():
            for chunk in r.iter_content(chunk_size=1024 * 128): yield chunk
        return Response(stream(), content_type=r.headers.get('Content-Type'))
    except: return "Stream Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)
