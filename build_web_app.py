import urllib.request
import os
import re

def download_lib(url):
    print(f"Downloading {url}...")
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')

def main():
    # CDN links for standard QR generation and scanning libraries
    qrcode_js_url = "https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"
    jsqr_js_url = "https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.min.js"
    
    try:
        qrcode_js = download_lib(qrcode_js_url)
        
        # Replace the buggy UTF-8 character loop in qrcode.js with standard TextEncoder
        a_pattern = r'function a\(a\)\{this\.mode=c\.MODE_8BIT_BYTE,[\s\S]*?unshift\(239\)\)\}'
        new_a = 'function a(a){this.mode=c.MODE_8BIT_BYTE,this.data=a;var bytes=new TextEncoder().encode(a);this.parsedData=[];if(bytes.length!==a.length){this.parsedData.push(239,187,191)}for(var i=0;i<bytes.length;i++){this.parsedData.push(bytes[i])}}'
        qrcode_js = re.sub(a_pattern, new_a, qrcode_js)

        # Replace capacity calculator s(a) to also use TextEncoder for exact byte counts
        s_pattern = r'function s\(a\)\{var b=encodeURI\(a\)[\s\S]*?return b\.length\+\(b\.length!=a\?3:0\)\}'
        new_s = 'function s(a){var bytes=new TextEncoder().encode(a);return bytes.length+(bytes.length!==a.length?3:0)}'
        qrcode_js = re.sub(s_pattern, new_s, qrcode_js)
        
        jsqr_js = download_lib(jsqr_js_url)
    except Exception as e:
        print(f"Error downloading libraries: {e}")
        return

    # Modern Web UI structure with HSL palettes, glassmorphism, responsive grids, and full offline Web Audio feedback
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Offline QR Text Transfer</title>
    <style>
        :root {{
            --bg-base: #0f172a;
            --bg-card: rgba(30, 41, 59, 0.7);
            --border-card: rgba(255, 255, 255, 0.08);
            --accent: #10b981;
            --accent-glow: rgba(16, 185, 129, 0.2);
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            -webkit-tap-highlight-color: transparent;
        }}

        body {{
            background-color: var(--bg-base);
            color: var(--text-main);
            font-family: var(--font-family);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            overflow-x: hidden;
            padding: 16px;
        }}

        .container {{
            width: 100%;
            max-width: 480px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}

        header {{
            text-align: center;
            margin-top: 10px;
            margin-bottom: 5px;
        }}

        h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            letter-spacing: -0.025em;
            background: linear-gradient(135deg, #34d399, #059669);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }}

        .subtitle {{
            font-size: 0.85rem;
            color: var(--text-muted);
        }}

        .tabs {{
            display: flex;
            background: rgba(15, 23, 42, 0.6);
            padding: 4px;
            border-radius: 12px;
            border: 1px solid var(--border-card);
        }}

        .tab-btn {{
            flex: 1;
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 10px;
            font-size: 0.9rem;
            font-weight: 600;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.25s ease;
        }}

        .tab-btn.active {{
            background: var(--bg-card);
            color: var(--text-main);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            border: 1px solid var(--border-card);
        }}

        .panel {{
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border-card);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.25);
            display: none;
            flex-direction: column;
            gap: 16px;
            min-height: 380px;
        }}

        .panel.active {{
            display: flex;
            animation: fadeIn 0.3s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Send Panel Elements */
        textarea {{
            width: 100%;
            height: 120px;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 12px;
            color: var(--text-main);
            font-family: var(--font-family);
            font-size: 0.9rem;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }}

        textarea:focus {{
            border-color: var(--accent);
        }}

        .char-counter {{
            font-size: 0.8rem;
            color: var(--text-muted);
            display: flex;
            justify-content: space-between;
        }}

        .btn {{
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 14px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
        }}

        .btn:active {{
            transform: scale(0.98);
            opacity: 0.9;
        }}

        .qr-display-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            margin-top: 10px;
        }}

        .qr-wrapper {{
            background: #fff;
            padding: 12px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            display: none;
            align-items: center;
            justify-content: center;
            width: 90vw;
            max-width: 340px;
            height: 90vw;
            max-height: 340px;
            box-sizing: border-box;
        }}

        #qrcode canvas, #qrcode img {{
            width: 100% !important;
            height: 100% !important;
            max-width: 316px;
            max-height: 316px;
            image-rendering: -moz-crisp-edges;
            image-rendering: -webkit-crisp-edges;
            image-rendering: pixelated;
            image-rendering: crisp-edges;
        }}

        .qr-controls {{
            display: flex;
            align-items: center;
            gap: 12px;
            width: 100%;
            justify-content: center;
            display: none;
        }}

        .speed-control {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            width: 100%;
            max-width: 250px;
            font-size: 0.8rem;
            color: var(--text-muted);
            margin-top: 6px;
            display: none;
        }}

        .speed-control input {{
            width: 100%;
            accent-color: var(--accent);
        }}

        /* Receive Panel Elements */
        .camera-container {{
            width: 100%;
            height: 250px;
            position: relative;
            background: #000;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-card);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        video {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
        }}

        .camera-placeholder {{
            color: var(--text-muted);
            text-align: center;
            font-size: 0.9rem;
            padding: 20px;
        }}

        .scanner-hud {{
            position: absolute;
            inset: 0;
            pointer-events: none;
            display: none;
            border: 3px solid transparent;
            box-sizing: border-box;
        }}

        .scanner-hud.active {{
            display: block;
        }}

        .scan-line {{
            position: absolute;
            width: 100%;
            height: 2px;
            background: var(--accent);
            top: 0;
            box-shadow: 0 0 10px var(--accent);
            animation: scan 2s linear infinite;
        }}

        @keyframes scan {{
            0% {{ top: 0%; }}
            50% {{ top: 100%; }}
            100% {{ top: 0%; }}
        }}

        .scan-corner {{
            position: absolute;
            width: 20px;
            height: 20px;
            border: 3px solid var(--accent);
        }}
        .corner-tl {{ top: 20px; left: 20px; border-right: none; border-bottom: none; }}
        .corner-tr {{ top: 20px; right: 20px; border-left: none; border-bottom: none; }}
        .corner-bl {{ bottom: 20px; left: 20px; border-right: none; border-top: none; }}
        .corner-br {{ bottom: 20px; right: 20px; border-left: none; border-top: none; }}

        .camera-select-wrapper {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        select {{
            width: 100%;
            background: rgba(15, 23, 42, 0.5);
            border: 1px solid var(--border-card);
            border-radius: 10px;
            padding: 10px;
            color: var(--text-main);
            outline: none;
            font-size: 0.85rem;
        }}

        /* HUD overlay progress card */
        .hud-status-card {{
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid var(--border-card);
            border-radius: 12px;
            padding: 12px;
            font-size: 0.85rem;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .progress-bar-bg {{
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress-bar-fill {{
            width: 0%;
            height: 100%;
            background: var(--accent);
            transition: width 0.15s ease;
        }}

        .success-box {{
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid var(--accent);
            border-radius: 12px;
            padding: 14px;
            display: none;
            flex-direction: column;
            gap: 10px;
            animation: fadeIn 0.3s ease;
        }}

        .success-title {{
            font-weight: 700;
            color: var(--accent);
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            gap: 6px;
        }}

        .success-preview {{
            background: rgba(15, 23, 42, 0.4);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 0.85rem;
            max-height: 80px;
            overflow-y: auto;
            word-break: break-all;
            white-space: pre-wrap;
            color: var(--text-main);
        }}

        /* File Mode specific styles */
        .badge {{
            display: inline-flex;
            align-items: center;
            background: rgba(239, 68, 68, 0.15);
            color: #ef4444;
            -webkit-text-fill-color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.3);
            padding: 2px 8px;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-left: 10px;
            vertical-align: middle;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0% {{ opacity: 0.8; }}
            50% {{ opacity: 1; box-shadow: 0 0 8px rgba(239, 68, 68, 0.4); }}
            100% {{ opacity: 0.8; }}
        }}

        .drop-zone {{
            border: 2px dashed rgba(255, 255, 255, 0.15);
            border-radius: 12px;
            padding: 30px 20px;
            text-align: center;
            background: rgba(255, 255, 255, 0.02);
            transition: all 0.25s ease;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            min-height: 160px;
        }}

        .drop-zone.dragover {{
            border-color: var(--accent);
            background: rgba(14, 165, 233, 0.05);
            box-shadow: 0 0 15px rgba(14, 165, 233, 0.15);
        }}

        .drop-icon {{
            width: 42px;
            height: 42px;
            fill: rgba(255, 255, 255, 0.4);
            transition: fill 0.25s ease;
        }}

        .drop-zone.dragover .drop-icon {{
            fill: var(--accent);
        }}

        .drop-text {{
            font-size: 0.9rem;
            color: rgba(255, 255, 255, 0.6);
        }}

        .browse-link {{
            color: var(--accent);
            text-decoration: underline;
            font-weight: 500;
        }}

        .file-info-container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            width: 100%;
        }}

        .file-name-display {{
            font-weight: 600;
            color: var(--text-main);
            font-size: 0.95rem;
            word-break: break-all;
        }}

        .file-size-display {{
            font-size: 0.8rem;
            color: rgba(255, 255, 255, 0.4);
        }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Offline QR Transfer<span id="file-mode-badge" class="badge" style="display: none;">File Mode</span></h1>
        <p class="subtitle">Secure, fast, paged text transfer via webcam</p>
    </header>

    <div class="tabs">
        <button id="btn-tab-send" class="tab-btn active" onclick="switchTab('send')">Send</button>
        <button id="btn-tab-receive" class="tab-btn" onclick="switchTab('receive')">Receive</button>
    </div>

    <!-- SEND PANEL -->
    <div id="panel-send" class="panel active">
        <div id="text-input-container" style="width: 100%; display: flex; flex-direction: column; gap: 10px;">
            <textarea id="send-input" placeholder="Type or paste your text here..." oninput="handleInput()"></textarea>
            <div class="char-counter">
                <span id="char-count">0 characters</span>
                <span id="chunk-count">0 chunks (100 chars/chunk)</span>
            </div>
            <button id="btn-start-send" class="btn" onclick="startSending()">Generate QR Loop</button>
        </div>
        
        <div id="file-input-container" style="display: none; width: 100%;">
            <div id="drop-zone" class="drop-zone" onclick="triggerFileBrowse()">
                <svg class="drop-icon" viewBox="0 0 24 24"><path d="M14 2H6c-1.1 0-1.99.9-1.99 2L4 20c0 1.1.89 2 1.99 2H18c1.1 0 2-.9 2-2V8l-6-6zm2 16H8v-2h8v2zm0-4H8v-2h8v2zm-3-5V3.5L18.5 9H13z"/></svg>
                <p id="drop-text">Drag & drop your file here, or <span class="browse-link">browse</span></p>
                <div id="file-info" class="file-info-container" style="display: none;">
                    <span id="file-name-display" class="file-name-display"></span>
                    <span id="file-size-display" class="file-size-display"></span>
                    <button type="button" id="btn-remove-file" class="btn btn-secondary" style="padding: 6px 12px; font-size: 0.8rem; margin-top: 5px;" onclick="removeFile(event)">Remove File</button>
                </div>
                <input type="file" id="file-loader" style="display: none;" onchange="handleFileSelect(this)">
            </div>
        </div>
        
        <div id="density-control" style="margin-top: 15px; display: flex; flex-direction: column; gap: 4px; width: 100%; box-sizing: border-box;">
            <div style="font-weight: 500; font-size: 0.85rem; color: var(--text-muted); display: flex; justify-content: space-between;">
                <span>QR Density / Pixel Size</span>
                <span id="density-val" style="font-weight: 600; color: var(--theme-color);">Medium (100 chars)</span>
            </div>
            <select id="density-select" class="select-input" style="padding: 8px; border-radius: 8px;" onchange="updateDensity(this.value)">
                <option value="low">Low Density (Big pixels - easiest to scan)</option>
                <option value="medium" selected>Medium Density (Balanced)</option>
                <option value="high">High Density (Smaller pixels)</option>
                <option value="very-high">Very High Density (Dense pixels)</option>
                <option value="extreme">Extreme Density (Faster - requires good camera)</option>
                <option value="max">Maximum Density (Highest speed - requires perfect focus)</option>
            </select>
        </div>
        
        <div class="qr-display-container">
            <div id="qr-wrapper" class="qr-wrapper">
                <div id="qrcode"></div>
            </div>
            
            <div id="speed-control" class="speed-control">
                <label for="speed-range">Frame Duration: <span id="speed-val">250</span>ms</label>
                <input type="range" id="speed-range" min="150" max="600" step="25" value="250" oninput="updateSpeed(this.value)">
            </div>
            
            <div id="qr-controls" class="qr-controls">
                <button class="btn" style="padding: 8px 16px;" onclick="togglePlay()">Play/Pause</button>
                <span id="frame-indicator" style="font-size: 0.85rem; color: var(--text-muted)">0 / 0</span>
            </div>
            
            <div id="sender-camera-panel" style="margin-top: 15px; display: flex; flex-direction: column; align-items: center; gap: 8px; width: 100%;">
                <div style="font-size: 0.8rem; font-weight: 600; color: var(--text-muted); display: flex; align-items: center; gap: 6px;">
                    <div id="sender-cam-status-dot" style="width: 8px; height: 8px; border-radius: 50%; background: #94a3b8; transition: background 0.3s;"></div>
                    <span>Bi-directional Optical Feedback Link</span>
                </div>
                <div id="sender-camera-controls" style="display: none; margin-bottom: 5px; width: 200px; gap: 6px;">
                    <select id="sender-camera-select" class="select-input" style="font-size: 0.75rem; padding: 4px 8px; height: auto; flex: 1;" onchange="switchSenderCamera(this.value)">
                        <option value="">Default Camera</option>
                    </select>
                    <button type="button" class="btn" style="padding: 4px 8px; font-size: 0.75rem; background: var(--bg-base); border: 1px solid var(--border-card);" onclick="flipSenderCamera()">Flip</button>
                </div>
                <div id="sender-video-container" style="position: relative; width: 200px; height: 150px; border-radius: 8px; overflow: hidden; border: 1px solid var(--border-card); background: #000; display: none;">
                    <video id="sender-video" style="width: 100%; height: 100%; object-fit: cover;" autoplay playsinline muted></video>
                    <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; box-shadow: inset 0 0 15px rgba(16, 185, 129, 0.4); pointer-events: none; border: 2px solid #10b981; border-radius: 8px; box-sizing: border-box; transition: all 0.3s;" id="sender-video-border"></div>
                </div>
                <button type="button" id="btn-toggle-sender-cam" class="btn" style="padding: 6px 12px; font-size: 0.8rem; background: var(--bg-base); border: 1px solid var(--border-card);" onclick="toggleSenderCam()">Enable Feedback Camera</button>
            </div>
        </div>
    </div>

    <!-- RECEIVE PANEL -->
    <div id="panel-receive" class="panel">
        <div class="camera-select-wrapper">
            <label for="camera-select" style="font-size: 0.8rem; color: var(--text-muted)">Webcam Source:</label>
            <select id="camera-select" onchange="changeCamera()"></select>
        </div>

        <div class="camera-container">
            <video id="webcam-video" playsinline></video>
            <div id="camera-placeholder" class="camera-placeholder">
                Camera is off. Click below to start scanning.
            </div>
            <div id="scanner-hud" class="scanner-hud">
                <div class="scan-line"></div>
                <div class="scan-corner corner-tl"></div>
                <div class="scan-corner corner-tr"></div>
                <div class="scan-corner corner-bl"></div>
                <div class="scan-corner corner-br"></div>
            </div>
        </div>

        <button id="btn-start-scan" class="btn" onclick="toggleScanner()">Start Scanner</button>
        
        <!-- Feedback QR Code Display -->
        <div id="receiver-feedback-card" style="display: none; flex-direction: column; align-items: center; gap: 10px; margin-top: 15px; padding: 15px; background: var(--bg-card); border-radius: 12px; border: 1px solid var(--border-card); width: 100%; box-sizing: border-box;">
            <div style="font-size: 0.85rem; font-weight: 600; color: var(--text-main);">Point this code at the sender's camera</div>
            <div id="feedback-qrcode" style="background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); display: inline-block;"></div>
            <div style="font-size: 0.75rem; color: var(--text-muted);" id="feedback-desc">Requesting missing chunks...</div>
            <button class="btn" style="padding: 6px 12px; font-size: 0.8rem; background: var(--theme-color); color: #000; font-weight: 600; width: 100%;" onclick="resumeReceiverScanning()">Resume Scanning</button>
        </div>

        <div id="hud-status" class="hud-status-card" style="display: none;">
            <div style="display: flex; justify-content: space-between; font-weight: 600;">
                <span id="scan-status">Align camera with rotating QR...</span>
                <span id="scan-ratio">0 / 0</span>
            </div>
            <div class="progress-bar-bg">
                <div id="scan-progress-bar" class="progress-bar-fill"></div>
            </div>
            <div style="margin-top: 10px; display: flex; gap: 8px; width: 100%;">
                <button type="button" id="btn-request-missing" class="btn" style="flex: 1; padding: 6px 12px; font-size: 0.8rem; background: rgba(16, 185, 129, 0.1); border: 1px solid var(--theme-color); color: var(--theme-color);" onclick="showMissingChunksQR()">Request Missing Chunks</button>
            </div>
        </div>

        <!-- Success display -->
        <div id="success-box" class="success-box">
            <div class="success-title">
                <svg width="18" height="18" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 0C4.48 0 0 4.48 0 10C0 15.52 4.48 20 10 20C15.52 20 20 15.52 20 10C20 4.48 15.52 0 10 0ZM8 15L3 10L4.41 8.59L8 12.17L15.59 4.58L17 6L8 15Z" fill="#10B981"/>
                </svg>
                Received Successfully!
            </div>
            <div id="success-preview" class="success-preview"></div>
            
            <button id="btn-copy-text-default" class="btn" style="background: var(--bg-base); border: 1px solid var(--border-card);" onclick="copyResult()">Copy to Clipboard</button>
            
            <div id="success-file-box" style="display: none; margin-top: 10px; flex-direction: column; gap: 8px; width: 100%;">
                <div style="font-size: 0.85rem; color: var(--text-muted); background: rgba(255,255,255,0.02); padding: 8px 12px; border-radius: 8px; text-align: left;">
                    <div style="font-weight: 600; color: var(--text-main); word-break: break-all;" id="received-file-name"></div>
                    <div style="font-size: 0.75rem; margin-top: 2px;" id="received-file-size"></div>
                </div>
                <div style="display: flex; gap: 8px; width: 100%;">
                    <button id="btn-download-file" class="btn" style="flex: 1;" onclick="downloadReceivedFile()">Download File</button>
                    <button id="btn-copy-file-text" class="btn" style="flex: 1; background: var(--bg-base); border: 1px solid var(--border-card);" onclick="copyResult()">Copy Text</button>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // --- LIBRARIES INLINED ---
    
    // 1. QRCode.js
    {qrcode_js}
    
    // 2. jsQR.js
    {jsqr_js}

    // --- APPLICATION LOGIC ---
    
    // Sound FX generator using Web Audio API
    function playSound(type) {{
        try {{
            var audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            var osc = audioCtx.createOscillator();
            var gain = audioCtx.createGain();
            
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            if (type === 'tick') {{
                osc.type = 'sine';
                osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.05);
            }} else if (type === 'success') {{
                // Chime sequence
                osc.type = 'sine';
                osc.frequency.setValueAtTime(880, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.1);
                osc.start();
                osc.stop(audioCtx.currentTime + 0.1);
                
                setTimeout(function() {{
                    var audioCtx2 = new (window.AudioContext || window.webkitAudioContext)();
                    var osc2 = audioCtx2.createOscillator();
                    var gain2 = audioCtx2.createGain();
                    osc2.connect(gain2);
                    gain2.connect(audioCtx2.destination);
                    osc2.type = 'sine';
                    osc2.frequency.setValueAtTime(1320, audioCtx2.currentTime);
                    gain2.gain.setValueAtTime(0.1, audioCtx2.currentTime);
                    gain2.gain.exponentialRampToValueAtTime(0.01, audioCtx2.currentTime + 0.25);
                    osc2.start();
                    osc2.stop(audioCtx2.currentTime + 0.25);
                }}, 80);
            }}
        }} catch(e) {{
            console.error("Audio error", e);
        }}
    }}

    // Tab switcher
    function switchTab(tab) {{
        document.getElementById('btn-tab-send').classList.remove('active');
        document.getElementById('btn-tab-receive').classList.remove('active');
        document.getElementById('panel-send').classList.remove('active');
        document.getElementById('panel-receive').classList.remove('active');
        
        if (tab === 'send') {{
            document.getElementById('btn-tab-send').classList.add('active');
            document.getElementById('panel-send').classList.add('active');
            stopScanner(); // Stop camera when switching tab
        }} else {{
            document.getElementById('btn-tab-receive').classList.add('active');
            document.getElementById('panel-receive').classList.add('active');
            loadCameras();
        }}
    }}

    // --- SENDER SECTION ---
    var qrGenerator = null;
    var qrChunks = [];
    var currentFrameIndex = 0;
    var sendTimer = null;
    var isSendingPlaying = true;
    var frameDuration = 250;
    
    // File upload state variables
    var selectedFile = null;
    var fileBase64 = "";
    
    // QR Density Config and State
    var densityConfig = {{
        text: {{
            low: 50,
            medium: 100,
            high: 180,
            'very-high': 300,
            extreme: 450,
            max: 600
        }},
        file: {{
            low: 150,
            medium: 300,
            high: 450,
            'very-high': 600,
            extreme: 800,
            max: 1000
        }}
    }};
    var currentDensityLevel = "medium";
    var chunkSize = 100; // Default text medium size

    // Feedback QR Sender Variables
    var senderCamStream = null;
    var senderCamIsActive = false;
    var senderFacingMode = "user"; // "user" or "environment"
    var senderScanTimer = null;
    var lastScannedFeedback = "";
    
    function toggleSenderCam() {{
        if (senderCamIsActive) {{
            stopSenderCam();
        }} else {{
            startSenderCam();
        }}
    }}

    function handleInput() {{
        var text = document.getElementById('send-input').value;
        document.getElementById('char-count').innerText = text.length + ' characters';
        
        var chunksCount = Math.ceil(text.length / chunkSize);
        document.getElementById('chunk-count').innerText = chunksCount + ' chunks (' + chunkSize + ' chars/chunk)';
    }}

    function getQrSize() {{
        var size = Math.min(316, window.innerWidth - 64);
        return size * 2;
    }}

    function startSending() {{
        var text = document.getElementById('send-input').value.trim();
        if (text === "/file") {{
            enableFileMode();
            document.getElementById('send-input').value = "";
            return;
        }}
        if (!text) {{
            alert("Please enter some text to send.");
            return;
        }}
        
        window.originalQrChunks = null; // Clear backup queue
        lastScannedFeedback = "";       // Clear feedback memory
        
        // Stop any current animation
        if (sendTimer) clearInterval(sendTimer);
        
        // Chunk (uses the outer chunkSize value)
        qrChunks = [];
        for (var i = 0; i < text.length; i += chunkSize) {{
            qrChunks.push(text.substring(i, i + chunkSize));
        }}
        
        // Show displays
        document.getElementById('qr-wrapper').style.display = 'flex';
        document.getElementById('qr-controls').style.display = 'flex';
        document.getElementById('speed-control').style.display = 'flex';
        
        // Initialize QR library
        var qrContainer = document.getElementById("qrcode");
        qrContainer.innerHTML = ''; // Clear
        var qrSize = getQrSize();
        qrGenerator = new QRCode(qrContainer, {{
            text: "1/1:Init",
            width: qrSize,
            height: qrSize,
            correctLevel: QRCode.CorrectLevel.L
        }});
        
        currentFrameIndex = 0;
        isSendingPlaying = true;
        
        // Start loop
        playFrames();
    }}

    function playFrames() {{
        if (sendTimer) clearInterval(sendTimer);
        
        // Start feedback webcam monitoring if active
        if (senderCamIsActive) {{
            if (!senderScanTimer) {{
                senderScanTimer = setInterval(scanSenderFrame, 300);
            }}
        }}
        
        function tickFrame() {{
            if (qrChunks.length === 0) return;
            
            var total = window.originalQrChunks ? window.originalQrChunks.length : qrChunks.length;
            var payload = qrChunks[currentFrameIndex];
            var isFile = (selectedFile !== null);
            
            // Determine dynamic indexToSend even in filtered sub-loop retransmissions
            var indexToSend = currentFrameIndex;
            if (window.originalQrChunks) {{
                var originalIdx = window.originalQrChunks.indexOf(payload);
                if (originalIdx !== -1) {{
                    indexToSend = originalIdx;
                }}
            }}
            
            if (!isFile) {{
                indexToSend += 1; // 1-based index for text mode
            }}
            
            var headerText = indexToSend + "/" + total + "/" + frameDuration + ":" + payload;
            
            qrGenerator.clear();
            qrGenerator.makeCode(headerText);
            
            var indicatorText = indexToSend + " / " + total;
            if (window.originalQrChunks) {{
                indicatorText += " (Re-sending " + qrChunks.length + " missing)";
            }}
            document.getElementById('frame-indicator').innerText = indicatorText;
            
            currentFrameIndex = (currentFrameIndex + 1) % qrChunks.length;
        }}
        
        tickFrame(); // Render first frame instantly
        sendTimer = setInterval(tickFrame, frameDuration);
    }}

    function startSenderCam() {{
        if (senderCamIsActive) return;
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {{
            alert("Feedback camera is not supported by your browser in this context (please use HTTPS).");
            return;
        }}
        
        var selectedCameraId = document.getElementById('sender-camera-select').value;
        var constraints = selectedCameraId ? 
            {{ video: {{ deviceId: {{ exact: selectedCameraId }} }} }} : 
            {{ video: {{ facingMode: senderFacingMode }} }};
        
        navigator.mediaDevices.getUserMedia(constraints)
            .then(function(stream) {{
                senderCamStream = stream;
                
                // Show container BEFORE calling play() to prevent browser rendering/power saving block!
                document.getElementById('sender-video-container').style.display = 'block';
                
                var video = document.getElementById('sender-video');
                video.style.display = 'block';
                video.setAttribute("playsinline", true);
                video.srcObject = stream;
                video.play().catch(function(e) {{
                    console.warn("Video play failed, browser policy might require click:", e);
                }});
                
                document.getElementById('btn-toggle-sender-cam').innerText = "Disable Feedback Camera";
                document.getElementById('sender-cam-status-dot').style.background = "#10b981";
                senderCamIsActive = true;
                
                // Load device lists for switching
                loadSenderCameras();
                
                // Start scan animation loop
                senderScanTimer = setInterval(scanSenderFrame, 300);
            }})
            .catch(function(err) {{
                console.error("Feedback webcam access failed", err);
                alert("Failed to access camera: " + err.message);
            }});
    }}

    function switchSenderCamera(deviceId) {{
        if (senderCamIsActive) {{
            if (senderCamStream) {{
                senderCamStream.getTracks().forEach(track => track.stop());
            }}
            
            var constraints = deviceId ? 
                {{ video: {{ deviceId: {{ exact: deviceId }} }} }} : 
                {{ video: true }};
            
            navigator.mediaDevices.getUserMedia(constraints)
                .then(function(stream) {{
                    senderCamStream = stream;
                    var video = document.getElementById('sender-video');
                    video.srcObject = stream;
                    video.play().catch(function(e) {{
                        console.warn("Video switch play failed:", e);
                    }});
                }})
                .catch(function(err) {{
                    console.error("Switching camera failed", err);
                }});
        }}
    }}

    function flipSenderCamera() {{
        if (senderCamIsActive) {{
            senderFacingMode = (senderFacingMode === "user") ? "environment" : "user";
            
            // Stop current stream
            if (senderCamStream) {{
                senderCamStream.getTracks().forEach(track => track.stop());
            }}
            
            // Clear dropdown select choice since we are switching based on facingMode
            document.getElementById('sender-camera-select').value = "";
            
            var constraints = {{
                video: {{ facingMode: senderFacingMode }}
            }};
            
            navigator.mediaDevices.getUserMedia(constraints)
                .then(function(stream) {{
                    senderCamStream = stream;
                    var video = document.getElementById('sender-video');
                    video.srcObject = stream;
                    video.play().catch(function(e) {{
                        console.warn("Video flip play failed:", e);
                    }});
                }})
                .catch(function(err) {{
                    console.error("Flipping camera failed", err);
                    // Re-start default cam
                    startSenderCam();
                }});
        }}
    }}

    function loadSenderCameras() {{
        var select = document.getElementById('sender-camera-select');
        if (!select) return;
        
        select.innerHTML = '<option value="">Default Camera</option>';
        
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
        
        navigator.mediaDevices.enumerateDevices()
            .then(function(devices) {{
                var count = 0;
                devices.forEach(function(device) {{
                    if (device.kind === 'videoinput') {{
                        var option = document.createElement('option');
                        option.value = device.deviceId;
                        option.text = device.label || 'Camera ' + (++count);
                        select.appendChild(option);
                    }}
                }});
                if (count > 0) {{
                    document.getElementById('sender-camera-controls').style.display = 'flex';
                }}
            }})
            .catch(function(err) {{
                console.warn("enumerateDevices failed for sender", err);
            }});
    }}

    function stopSenderCam() {{
        senderCamIsActive = false;
        if (senderScanTimer) {{
            clearInterval(senderScanTimer);
            senderScanTimer = null;
        }}
        if (senderCamStream) {{
            senderCamStream.getTracks().forEach(track => track.stop());
            senderCamStream = null;
        }}
        document.getElementById('sender-video-container').style.display = 'none';
        document.getElementById('sender-camera-controls').style.display = 'none';
        document.getElementById('btn-toggle-sender-cam').innerText = "Enable Feedback Camera";
        document.getElementById('sender-cam-status-dot').style.background = "#94a3b8";
    }}

    function scanSenderFrame() {{
        if (!senderCamIsActive) return;
        var video = document.getElementById('sender-video');
        if (video.readyState === video.HAVE_ENOUGH_DATA) {{
            var canvas = document.createElement('canvas');
            canvas.width = 320;
            canvas.height = 240;
            var ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
            var imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
            
            var code = jsQR(imageData.data, imageData.width, imageData.height, {{
                inversionAttempts: "dontInvert"
            }});
            
            if (code && code.data) {{
                handleFeedbackQR(code.data);
            }}
        }}
    }}

    function handleFeedbackQR(data) {{
        if (data === lastScannedFeedback) return; // Debounce repeats
        lastScannedFeedback = data;
        
        if (data === "FB:COMPLETE") {{
            console.log("Feedback Link: Transfer Complete confirmed!");
            try {{
                playSound('success');
            }} catch(e) {{}}
            
            flashSenderCamBorder("#10b981");
            
            if (isSendingPlaying) {{
                togglePlay();
            }}
            document.getElementById('frame-indicator').innerText = "Transfer Completed Successfully!";
            alert("Receiver confirmed successful file/text transfer!");
            
        }} else if (data.startsWith("FB:")) {{
            var missingStr = data.substring(3);
            var missingIndices = decompressMissingIndices(missingStr);
            
            console.log("Feedback Link: Missing indices received:", missingIndices);
            
            if (missingIndices.length > 0) {{
                try {{
                    playSound('tick');
                }} catch(e) {{}}
                
                flashSenderCamBorder("#f59e0b");
                
                if (!window.originalQrChunks) {{
                    window.originalQrChunks = [...qrChunks];
                }}
                
                var newChunks = [];
                var isFile = (selectedFile !== null);
                
                for (var i = 0; i < missingIndices.length; i++) {{
                    var idx = missingIndices[i];
                    var originalIdx = isFile ? idx : idx - 1;
                    if (window.originalQrChunks[originalIdx] !== undefined) {{
                        newChunks.push(window.originalQrChunks[originalIdx]);
                    }}
                }}
                
                if (newChunks.length > 0) {{
                    qrChunks = newChunks;
                    currentFrameIndex = 0;
                    
                    document.getElementById('frame-indicator').innerText = "Re-sending " + qrChunks.length + " missing chunks...";
                    playFrames();
                }}
            }}
        }}
    }}

    function flashSenderCamBorder(color) {{
        var border = document.getElementById('sender-video-border');
        if (!border) return;
        border.style.borderColor = color;
        border.style.boxShadow = "inset 0 0 20px " + color;
        setTimeout(function() {{
            border.style.borderColor = "#10b981";
            border.style.boxShadow = "inset 0 0 15px rgba(16, 185, 129, 0.4)";
        }}, 1000);
    }}

    function compressMissingIndices(arr) {{
        if (arr.length === 0) return "";
        var parts = [];
        var start = arr[0];
        var prev = arr[0];
        for (var i = 1; i <= arr.length; i++) {{
            var curr = arr[i];
            if (curr === prev + 1) {{
                prev = curr;
            }} else {{
                if (start === prev) {{
                    parts.push(start);
                }} else {{
                    parts.push(start + "-" + prev);
                }}
                start = curr;
                prev = curr;
            }}
        }}
        return parts.join(",");
    }}

    function decompressMissingIndices(str) {{
        if (!str) return [];
        var arr = [];
        var parts = str.split(",");
        for (var i = 0; i < parts.length; i++) {{
            var p = parts[i];
            if (p.indexOf("-") !== -1) {{
                var range = p.split("-");
                var s = parseInt(range[0]);
                var e = parseInt(range[1]);
                for (var j = s; j <= e; j++) {{
                    arr.push(j);
                }}
            }} else {{
                arr.push(parseInt(p));
            }}
        }}
        return arr;
    }}

    function togglePlay() {{
        if (isSendingPlaying) {{
            clearInterval(sendTimer);
            isSendingPlaying = false;
        }} else {{
            isSendingPlaying = true;
            playFrames();
        }}
    }}

    function updateSpeed(val) {{
        frameDuration = parseInt(val);
        document.getElementById('speed-val').innerText = val;
        if (isSendingPlaying) {{
            playFrames();
        }}
    }}

    function updateDensity(level) {{
        currentDensityLevel = level;
        
        var isFile = (selectedFile !== null);
        var mode = isFile ? "file" : "text";
        chunkSize = densityConfig[mode][level];
        
        var labelText = level.charAt(0).toUpperCase() + level.slice(1).replace("-", " ") + " (" + chunkSize + " chars)";
        var densityValEl = document.getElementById('density-val');
        if (densityValEl) {{
            densityValEl.innerText = labelText;
        }}
        
        // Refresh input counters
        handleInput();
        
        // If actively sending, regenerate chunks and restart loop instantly
        if (qrChunks.length > 0) {{
            if (isFile) {{
                setupFileChunks(selectedFile.name, selectedFile.type, selectedFile.sha256, selectedFile.size);
            }} else {{
                var text = document.getElementById('send-input').value.trim();
                if (text) {{
                    qrChunks = [];
                    for (var i = 0; i < text.length; i += chunkSize) {{
                        qrChunks.push(text.substring(i, i + chunkSize));
                    }}
                    currentFrameIndex = 0;
                    playFrames();
                }}
            }}
        }}
    }}

    // --- FILE TRANSFER SENDER HELPERS ---
    function triggerFileBrowse() {{
        document.getElementById('file-loader').click();
    }}

    function handleFileSelect(input) {{
        var file = input.files[0];
        if (file) {{
            processSelectedFile(file);
        }}
    }}

    function processSelectedFile(file) {{
        selectedFile = file;
        
        // Hide standard prompt text, show file metadata details
        document.getElementById('drop-text').style.display = 'none';
        document.getElementById('file-name-display').innerText = file.name;
        document.getElementById('file-size-display').innerText = formatSize(file.size);
        document.getElementById('file-info').style.display = 'flex';
        
        // Read file as Data URL (for Base64 payload)
        var reader = new FileReader();
        reader.onload = function(e) {{
            var dataUrl = e.target.result;
            var commaIdx = dataUrl.indexOf(',');
            fileBase64 = dataUrl.substring(commaIdx + 1);
            
            var mimeType = "application/octet-stream";
            var colonIdx = dataUrl.indexOf(':');
            var semiIdx = dataUrl.indexOf(';');
            if (colonIdx !== -1 && semiIdx !== -1) {{
                mimeType = dataUrl.substring(colonIdx + 1, semiIdx);
            }}
            
            // Read array buffer to calculate SHA-256
            var arrayBufReader = new FileReader();
            arrayBufReader.onload = function(evt) {{
                var arrayBuffer = evt.target.result;
                crypto.subtle.digest("SHA-256", arrayBuffer)
                    .then(function(hashBuffer) {{
                        var hashArray = Array.from(new Uint8Array(hashBuffer));
                        var hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
                        setupFileChunks(file.name, mimeType, hashHex, file.size);
                    }})
                    .catch(function(err) {{
                        console.error("SHA-256 generation failed, using fallback", err);
                        var fallbackHash = "sha256-fallback-" + file.size + "-" + Date.now();
                        setupFileChunks(file.name, mimeType, fallbackHash, file.size);
                    }});
            }};
            arrayBufReader.readAsArrayBuffer(file);
        }};
        reader.readAsDataURL(file);
    }}

    function removeFile(event) {{
        if (event) event.stopPropagation(); // Avoid triggering file browse handler on click
        
        selectedFile = null;
        fileBase64 = "";
        
        // Stop any sending loops and clear the QR view
        if (sendTimer) clearInterval(sendTimer);
        qrChunks = [];
        window.originalQrChunks = null;
        lastScannedFeedback = "";
        var qrContainer = document.getElementById("qrcode");
        qrContainer.innerHTML = '';
        document.getElementById('qr-wrapper').style.display = 'none';
        document.getElementById('qr-controls').style.display = 'none';
        document.getElementById('speed-control').style.display = 'none';
        
        // Reset file uploader input values
        document.getElementById('file-loader').value = "";
        
        // Reset Drop Zone visuals
        document.getElementById('file-info').style.display = 'none';
        document.getElementById('drop-text').style.display = 'block';
        
        // Reset chunkSize back to text mode density and update char counter
        updateDensity(currentDensityLevel);
    }}

    function setupFileChunks(filename, mimeType, sha256, size) {{
        // Clean filename of semicolons to prevent protocol parsing errors
        var cleanName = filename.replace(/;/g, "_");
        
        // Total data chunks (chunkSize chars per frame in file mode)
        var totalDataChunks = Math.ceil(fileBase64.length / chunkSize);
        var total = totalDataChunks + 1; // +1 for Manifest Frame at index 0
        
        qrChunks = [];
        // Frame 0: Manifest Frame (raw content, no prefix!)
        qrChunks.push(cleanName + ";" + mimeType + ";" + sha256 + ";" + size);
        
        // Frame 1 to N: Base64 data chunks (raw contents, no prefix!)
        for (var i = 0; i < totalDataChunks; i++) {{
            var start = i * chunkSize;
            var end = start + chunkSize;
            qrChunks.push(fileBase64.substring(start, end));
        }}
        
        // Show controls and immediately start playing the loop!
        document.getElementById('qr-wrapper').style.display = 'flex';
        document.getElementById('qr-controls').style.display = 'flex';
        document.getElementById('speed-control').style.display = 'flex';
        
        var qrContainer = document.getElementById("qrcode");
        qrContainer.innerHTML = ''; // Clear
        var qrSize = getQrSize();
        qrGenerator = new QRCode(qrContainer, {{
            text: "1/1:Init",
            width: qrSize,
            height: qrSize,
            correctLevel: QRCode.CorrectLevel.L
        }});
        
        currentFrameIndex = 0;
        isSendingPlaying = true;
        playFrames();
    }}

    function formatSize(bytes) {{
        if (bytes === 0) return '0 Bytes';
        var k = 1024;
        var sizes = ['Bytes', 'KB', 'MB'];
        var i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }}

    // --- RECEIVER SECTION ---
    var videoElement = document.getElementById('webcam-video');
    var canvasElement = document.createElement('canvas');
    var canvasContext = canvasElement.getContext('2d');
    var cameraStream = null;
    var scanAnimationId = null;
    
    var receivedChunks = {{}};
    var totalChunks = -1;
    var scanResult = "";
    var scanFrameCount = 0;
    var fileMetadata = null; // Stores parsed manifest frame details
    var receivedBlob = null;   // Stores decoded binary file Blob
    
    // Feedback QR Receiver Variables
    var feedbackQrGenerator = null;
    var isReceiverAcousticEnabled = false; // Kept for logic compatibility
    var senderFrameDuration = 250;         // Default fallback sender speed
    var lastDecodeTime = 0;                // For CPU throttling cool-down

    function loadCameras() {{
        var select = document.getElementById('camera-select');
        select.innerHTML = '';
        
        navigator.mediaDevices.enumerateDevices()
            .then(function(devices) {{
                var count = 0;
                devices.forEach(function(device) {{
                    if (device.kind === 'videoinput') {{
                        var option = document.createElement('option');
                        option.value = device.deviceId;
                        // iOS devices often return empty labels initially unless permission was granted
                        option.text = device.label || 'Camera ' + (++count);
                        select.appendChild(option);
                    }}
                }});
            }})
            .catch(function(err) {{
                console.error("Enumerate devices error", err);
            }});
    }}

    function changeCamera() {{
        if (cameraStream) {{
            // Restart camera with new ID
            stopScanner();
            startScanner();
        }}
    }}

    function toggleScanner() {{
        var btn = document.getElementById('btn-start-scan');
        if (cameraStream) {{
            stopScanner();
            btn.innerText = "Start Scanner";
        }} else {{
            startScanner();
            btn.innerText = "Stop Scanner";
        }}
    }}

    function startScanner(resume) {{
        if (!resume) {{
            receivedChunks = {{}};
            totalChunks = -1;
            scanResult = "";
            scanFrameCount = 0;
            fileMetadata = null;
            receivedBlob = null;
            senderFrameDuration = 250;
            lastDecodeTime = 0;
        }}
        
        document.getElementById('success-box').style.display = 'none';
        document.getElementById('hud-status').style.display = 'block';
        
        if (!resume) {{
            updateScanProgress(0, 0, "Initializing camera...");
        }}
        
        var selectedCameraId = document.getElementById('camera-select').value;
        var videoConstraints = selectedCameraId ? {{ deviceId: {{ exact: selectedCameraId }} }} : {{ facingMode: 'environment' }};
        videoConstraints.width = {{ ideal: 1280 }};
        videoConstraints.height = {{ ideal: 720 }};
        var constraints = {{
            video: videoConstraints
        }};
        
        navigator.mediaDevices.getUserMedia(constraints)
            .then(function(stream) {{
                cameraStream = stream;
                videoElement.srcObject = stream;
                videoElement.setAttribute("playsinline", true); // Required for iOS
                videoElement.style.display = 'block';
                document.getElementById('camera-placeholder').style.display = 'none';
                document.getElementById('scanner-hud').classList.add('active');
                videoElement.play();
                updateScanProgress(0, 0, "Looking for QR code...");
                
                // Start scan animation frame loop
                scanAnimationId = requestAnimationFrame(scanTick);
                
                // Re-load devices so labels are populated on iOS after permission grant
                loadCameras();
            }})
            .catch(function(err) {{
                alert("Camera access error: " + err.message);
                stopScanner();
            }});
    }}

    function stopScanner() {{
        if (scanAnimationId) {{
            cancelAnimationFrame(scanAnimationId);
            scanAnimationId = null;
        }}
        
        if (cameraStream) {{
            cameraStream.getTracks().forEach(function(track) {{
                track.stop();
            }});
            cameraStream = null;
        }}
        
        videoElement.pause();
        videoElement.srcObject = null;
        videoElement.style.display = 'none';
        document.getElementById('camera-placeholder').style.display = 'block';
        document.getElementById('scanner-hud').classList.remove('active');
        document.getElementById('btn-start-scan').innerText = "Start Scanner";
    }}

    function updateScanProgress(current, total, statusText) {{
        document.getElementById('scan-status').innerText = statusText;
        document.getElementById('scan-ratio').innerText = current + " / " + total;
        
        var percent = total > 0 ? (current / total) * 100 : 0;
        document.getElementById('scan-progress-bar').style.width = percent + '%';
    }}

    function scanTick() {{
        var now = Date.now();
        // Skip scanning canvas frames if we decoded a frame very recently (up to 70% of sender's cycle time)
        if (now - lastDecodeTime < (senderFrameDuration * 0.7)) {{
            if (cameraStream) {{
                scanAnimationId = requestAnimationFrame(scanTick);
            }}
            return;
        }}
        
        if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {{
            try {{
                scanFrameCount++;
                if (scanFrameCount % 6 === 0) {{
                    var count = Object.keys(receivedChunks).length;
                    if (count === 0) {{
                        document.getElementById('scan-status').innerText = "Looking for QR... (frames: " + scanFrameCount + ")";
                    }}
                }}
                
                var width = videoElement.videoWidth;
                var height = videoElement.videoHeight;
                
                // Downscale resolution for mobile CPU decoding performance (prevents browser lag)
                var maxDim = 720;
                if (width > maxDim || height > maxDim) {{
                    if (width > height) {{
                        height = Math.round((height * maxDim) / width);
                        width = maxDim;
                    }} else {{
                        width = Math.round((width * maxDim) / height);
                        height = maxDim;
                    }}
                }}
                
                canvasElement.width = width;
                canvasElement.height = height;
                canvasContext.drawImage(videoElement, 0, 0, width, height);
                
                var imageData = canvasContext.getImageData(0, 0, width, height);
                var code = jsQR(imageData.data, imageData.width, imageData.height, {{
                    inversionAttempts: "attemptBoth"
                }});
                
                if (code) {{
                    var matched = processDecodedText(code.data);
                    if (matched) {{
                        lastDecodeTime = Date.now(); // Trigger cool-down on successful decode
                        // Display sender transmission metrics in scanner status
                        var currentCount = Object.keys(receivedChunks).length;
                        var statusMsg = fileMetadata ? "Receiving file: " + fileMetadata.name : "Scanning chunks...";
                        statusMsg += " (" + senderFrameDuration + "ms sync)";
                        updateScanProgress(currentCount, totalChunks, statusMsg);
                    }} else {{
                        document.getElementById('scan-status').innerText = "QR found (invalid format): '" + code.data + "' (Please hard-refresh both devices to clear cache)";
                    }}
                }}
            }} catch (err) {{
                document.getElementById('scan-status').innerText = "Scanner Error: " + err.message;
                console.error("Scanner Error:", err);
            }}
        }}
        
        if (cameraStream) {{
            scanAnimationId = requestAnimationFrame(scanTick);
        }}
    }}

    function processDecodedText(data) {{
        // Strip UTF-8 BOM if present (added by some QR generators/encodings)
        if (data && data.charCodeAt(0) === 0xFEFF) {{
            data = data.substring(1);
        }}
        // Protocol matching: index/total/interval:payload or index/total:payload (whitespace tolerant)
        var regex = /^\s*(\d+)\/(\d+)(?:\/(\d+))?:([\s\S]*)$/;
        var match = regex.exec(data);
        if (!match) return false;
        
        var index = parseInt(match[1]);
        var total = parseInt(match[2]);
        var interval = match[3] ? parseInt(match[3]) : null;
        var payload = match[4];
        
        // Dynamically update scanner cool-down to match sender interval speed
        if (interval && interval >= 100) {{
            senderFrameDuration = interval;
        }}
        
        if (totalChunks !== -1 && totalChunks !== total) {{
            // Reset if chunk total changes (scanning a new code)
            receivedChunks = {{}};
            fileMetadata = null;
            receivedBlob = null;
        }}
        totalChunks = total;
        
        if (index === 0) {{
            // Manifest frame! Format: filename;mimeType;sha256;size
            var parts = payload.split(';');
            if (parts.length >= 4) {{
                fileMetadata = {{
                    name: parts[0],
                    mime: parts[1],
                    hash: parts[2],
                    size: parseInt(parts[3])
                }};
            }}
        }}
        
        var isNew = !receivedChunks[index];
        if (isNew) {{
            receivedChunks[index] = payload;
            
            // In silent/feedback optical mode, we don't play ticking sounds to keep it fully silent
            // unless the user wants fallback sounds.
            
            var count = Object.keys(receivedChunks).length;
            var statusText = fileMetadata ? "Receiving file: " + fileMetadata.name : "Scanning chunks...";
            updateScanProgress(count, total, statusText);
            
            if (count === total) {{
                finishScanning();
                return true;
            }}
        }}
        return true;
    }}

    function finishScanning() {{
        stopScanner();
        playSound('success');
        
        document.getElementById('hud-status').style.display = 'none';
        document.getElementById('success-box').style.display = 'flex';
        
        if (fileMetadata) {{
            // File Mode Reassembly
            var fullBase64 = "";
            for (var i = 1; i < totalChunks; i++) {{
                if (receivedChunks[i]) {{
                    fullBase64 += receivedChunks[i];
                }}
            }}
            
            // Asynchronously convert Base64 to Blob using browser's native data URI parser
            fetch("data:" + fileMetadata.mime + ";base64," + fullBase64)
                .then(r => r.blob())
                .then(blob => {{
                    receivedBlob = blob;
                    
                    // Display file metadata card
                    document.getElementById('received-file-name').innerText = fileMetadata.name;
                    document.getElementById('received-file-size').innerText = formatSize(fileMetadata.size);
                    document.getElementById('success-file-box').style.display = 'flex';
                    document.getElementById('btn-copy-text-default').style.display = 'none';
                    
                    // If file is text-based, allow text copying/preview
                    var isText = fileMetadata.mime.startsWith('text/') || 
                                 fileMetadata.mime === 'application/json' || 
                                 fileMetadata.name.endsWith('.js') || 
                                 fileMetadata.name.endsWith('.py') ||
                                 fileMetadata.name.endsWith('.pem') ||
                                 fileMetadata.name.endsWith('.yml') ||
                                 fileMetadata.name.endsWith('.yaml');
                                 
                    if (isText) {{
                        blob.text().then(text => {{
                            scanResult = text;
                            document.getElementById('success-preview').innerText = text;
                            document.getElementById('btn-copy-file-text').style.display = 'block';
                        }});
                    }} else {{
                        scanResult = "";
                        document.getElementById('success-preview').innerText = "Binary File (" + fileMetadata.name + ")\\nClick 'Download File' to save it.";
                        document.getElementById('btn-copy-file-text').style.display = 'none';
                    }}
                    
                    document.getElementById('scan-status').innerText = "File transfer completed!";
                }})
                .catch(err => {{
                    console.error("File reassembly error", err);
                    document.getElementById('scan-status').innerText = "Error reassembling file: " + err.message;
                }});
        }} else {{
            // Text Mode Assembly
            var fullText = "";
            for (var i = 1; i <= totalChunks; i++) {{
                if (receivedChunks[i]) {{
                    fullText += receivedChunks[i];
                }}
            }}
            
            scanResult = fullText;
            document.getElementById('success-preview').innerText = fullText;
            document.getElementById('success-file-box').style.display = 'none';
            document.getElementById('btn-copy-text-default').style.display = 'block';
            
            // Attempt auto clipboard copy (might require user interaction on iOS)
            navigator.clipboard.writeText(fullText)
                .then(function() {{
                    document.getElementById('scan-status').innerText = "Copied to clipboard!";
                }})
                .catch(function(e) {{
                    console.warn("Clipboard auto-copy blocked by iOS security, click copy manually.", e);
                }});
        }}
    }}

    function downloadReceivedFile() {{
        if (!receivedBlob || !fileMetadata) return;
        
        var url = URL.createObjectURL(receivedBlob);
        var a = document.createElement("a");
        a.href = url;
        a.download = fileMetadata.name;
        document.body.appendChild(a);
        a.click();
        
        // Cleanup
        document.body.removeChild(a);
        setTimeout(() => {{
            URL.revokeObjectURL(url);
        }}, 100);
    }}

    function copyResult() {{
        navigator.clipboard.writeText(scanResult)
            .then(function() {{
                alert("Copied to clipboard!");
            }})
            .catch(function(err) {{
                alert("Failed to copy: " + err);
            }});
    }}

    function showMissingChunksQR() {{
        stopScanner();
        
        var missingArray = [];
        var total = totalChunks;
        
        if (total > 0) {{
            var isFile = (fileMetadata !== null);
            var start = isFile ? 0 : 1;
            var end = isFile ? total : total + 1;
            
            for (var k = start; k < end; k++) {{
                if (!receivedChunks[k]) {{
                    missingArray.push(k);
                }}
            }}
        }}
        
        if (missingArray.length > 0) {{
            var compressed = compressMissingIndices(missingArray);
            var payload = "FB:" + compressed;
            document.getElementById('feedback-desc').innerText = "Requesting " + missingArray.length + " missing chunks.";
            
            if (!feedbackQrGenerator) {{
                feedbackQrGenerator = new QRCode(document.getElementById("feedback-qrcode"), {{
                    text: "Init",
                    width: 140,
                    height: 140,
                    correctLevel: QRCode.CorrectLevel.L
                }});
            }}
            feedbackQrGenerator.clear();
            feedbackQrGenerator.makeCode(payload);
            
            document.getElementById('hud-status').style.display = 'none';
            document.getElementById('receiver-feedback-card').style.display = 'flex';
        }}
    }}

    function resumeReceiverScanning() {{
        document.getElementById('receiver-feedback-card').style.display = 'none';
        document.getElementById('hud-status').style.display = 'block';
        startScanner(true); // Resume scanning
    }}

    function enableFileMode() {{
        document.getElementById('text-input-container').style.display = 'none';
        document.getElementById('file-input-container').style.display = 'block';
        document.getElementById('file-mode-badge').style.display = 'inline-flex';
        
        // Set file-mode chunkSize and update labels
        updateDensity(currentDensityLevel);
        
        // Push URL parameter dynamically without reloading page
        var newUrl = window.location.protocol + "//" + window.location.host + window.location.pathname + "?mode=file";
        window.history.pushState({{ path: newUrl }}, '', newUrl);
    }}

    // Check URL parameters for file mode activation
    var urlParams = new URLSearchParams(window.location.search);
    var isFileMode = urlParams.get("mode") === "file";
    
    if (isFileMode) {{
        enableFileMode();
    }}

    // Setup drag and drop event listeners
    var dropZone = document.getElementById('drop-zone');
    if (dropZone) {{
        ['dragenter', 'dragover'].forEach(eventName => {{
            dropZone.addEventListener(eventName, (e) => {{
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.add('dragover');
            }}, false);
        }});

        ['dragleave', 'drop'].forEach(eventName => {{
            dropZone.addEventListener(eventName, (e) => {{
                e.preventDefault();
                e.stopPropagation();
                dropZone.classList.remove('dragover');
            }}, false);
        }});

        dropZone.addEventListener('drop', (e) => {{
            var dt = e.dataTransfer;
            var file = dt.files[0];
            if (file) {{
                processSelectedFile(file);
            }}
        }}, false);
    }}
</script>

</body>
</html>
"""
    
    # Save index.html inside the qr-transfer folder
    target_file = "/Users/maxwell/Code/qr-transfer/index.html"
    with open(target_file, "w") as f:
        f.write(html_content)
        
    print(f"Web App successfully created at {target_file}!")

if __name__ == "__main__":
    main()
