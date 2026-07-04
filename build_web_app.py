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
            padding: 16px;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            display: none;
            align-items: center;
            justify-content: center;
            width: 250px;
            height: 250px;
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
            
            <div style="margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.85rem; color: var(--text-muted);">
                <input type="checkbox" id="sender-acoustic-toggle" onchange="toggleSenderAcoustic(this.checked)" style="cursor: pointer;">
                <label for="sender-acoustic-toggle" style="cursor: pointer; user-select: none;">Acoustic Sync Loop (Beta)</label>
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
        
        <div style="margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 8px; font-size: 0.85rem; color: var(--text-muted);">
            <input type="checkbox" id="receiver-acoustic-toggle" onchange="toggleReceiverAcoustic(this.checked)" style="cursor: pointer;">
            <label for="receiver-acoustic-toggle" style="cursor: pointer; user-select: none;">Acoustic Sync Handshake (Beta)</label>
        </div>

        <div id="hud-status" class="hud-status-card" style="display: none;">
            <div style="display: flex; justify-content: space-between; font-weight: 600;">
                <span id="scan-status">Align camera with rotating QR...</span>
                <span id="scan-ratio">0 / 0</span>
            </div>
            <div class="progress-bar-bg">
                <div id="scan-progress-bar" class="progress-bar-fill"></div>
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
    var chunkSize = 100; // Will be set to 800 in file mode
    
    // Acoustic Sync Sender Variables
    var isSenderAcousticEnabled = false;
    var currentBatchIndex = 0;
    var batchSize = 25;
    var isWaitingForAck = false;
    var ackTimeout = null;
    var senderAudioCtx = null;
    var senderAnalyser = null;
    var senderMicStream = null;
    var senderIsListening = false;
    
    function toggleSenderAcoustic(enabled) {{
        isSenderAcousticEnabled = enabled;
        if (!enabled) {{
            stopSenderListening();
            if (ackTimeout) clearTimeout(ackTimeout);
            isWaitingForAck = false;
        }}
    }}

    function handleInput() {{
        var text = document.getElementById('send-input').value;
        document.getElementById('char-count').innerText = text.length + ' characters';
        
        var chunksCount = Math.ceil(text.length / 100);
        document.getElementById('chunk-count').innerText = chunksCount + ' chunks (100 chars/chunk)';
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
        qrGenerator = new QRCode(qrContainer, {{
            text: "1/1:Init",
            width: 218,
            height: 218,
            correctLevel: QRCode.CorrectLevel.L
        }});
        
        currentFrameIndex = 0;
        isSendingPlaying = true;
        
        // Start loop
        playFrames();
    }}

    function playFrames() {{
        if (sendTimer) clearInterval(sendTimer);
        
        if (isSenderAcousticEnabled) {{
            isWaitingForAck = true;
            startSenderListening();
        }}
        
        function tickFrame() {{
            if (qrChunks.length === 0) return;
            
            var total = qrChunks.length;
            
            // Calculate batch range boundaries
            var batchStart = 0;
            var batchEnd = total;
            if (isSenderAcousticEnabled) {{
                batchStart = currentBatchIndex * batchSize;
                batchEnd = Math.min(batchStart + batchSize, total);
                
                // Wrap frame index strictly within the current batch boundary
                if (currentFrameIndex < batchStart || currentFrameIndex >= batchEnd) {{
                    currentFrameIndex = batchStart;
                }}
            }}
            
            var payload = qrChunks[currentFrameIndex];
            var headerText = (currentFrameIndex + 1) + "/" + total + ":" + payload;
            
            qrGenerator.clear();
            qrGenerator.makeCode(headerText);
            
            var indicatorText = (currentFrameIndex + 1) + " / " + total;
            if (isSenderAcousticEnabled) {{
                indicatorText += " (Batch " + (currentBatchIndex + 1) + ")";
            }}
            document.getElementById('frame-indicator').innerText = indicatorText;
            
            if (isSenderAcousticEnabled) {{
                // Loop continuously inside the current batch
                var range = batchEnd - batchStart;
                currentFrameIndex = batchStart + (currentFrameIndex - batchStart + 1) % range;
            }} else {{
                currentFrameIndex = (currentFrameIndex + 1) % total;
            }}
        }}
        
        tickFrame(); // Render first frame instantly
        sendTimer = setInterval(tickFrame, frameDuration);
    }}

    function startSenderListening() {{
        if (senderIsListening) {{
            if (isWaitingForAck) {{
                detectAckTone();
            }}
            return;
        }}
        
        if (!senderAudioCtx) {{
            senderAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
            senderAnalyser = senderAudioCtx.createAnalyser();
            senderAnalyser.fftSize = 2048;
        }}
        if (senderAudioCtx.state === 'suspended') {{
            senderAudioCtx.resume();
        }}
        
        document.getElementById('frame-indicator').innerText = "Waiting for audio ACK...";
        
        navigator.mediaDevices.getUserMedia({{ audio: true }})
            .then(function(stream) {{
                senderMicStream = stream;
                var source = senderAudioCtx.createMediaStreamSource(stream);
                source.connect(senderAnalyser);
                senderIsListening = true;
                
                if (isWaitingForAck) {{
                    detectAckTone();
                }}
            }})
            .catch(function(err) {{
                console.error("Microphone access failed", err);
            }});
    }}

    function stopSenderListening() {{
        senderIsListening = false;
        if (senderMicStream) {{
            senderMicStream.getTracks().forEach(track => track.stop());
            senderMicStream = null;
        }}
    }}

    function detectAckTone() {{
        if (!senderIsListening || !isWaitingForAck) return;
        
        var now = Date.now();
        // Ignore microphone detection during 2-second cool-down to let iPhone tone stop playing
        if (now - lastSenderAckTime < 2000) {{
            requestAnimationFrame(detectAckTone);
            return;
        }}
        
        var dataArray = new Uint8Array(senderAnalyser.frequencyBinCount);
        senderAnalyser.getByteFrequencyData(dataArray);
        
        var binIndex = Math.round(15000 / (senderAudioCtx.sampleRate / 2048));
        
        var peak = 0;
        for (var offset = -2; offset <= 2; offset++) {{
            var val = dataArray[binIndex + offset] || 0;
            if (val > peak) peak = val;
        }}
        
        if (qrChunks.length > 0) {{
            document.getElementById('frame-indicator').innerText = 
                (currentFrameIndex + 1) + " / " + qrChunks.length + 
                " | Mic Peak: " + peak + " / 90 (Batch " + (currentBatchIndex + 1) + ")";
        }}
        
        if (peak > 90) {{
            console.log("Acoustic ACK received successfully! Peak: " + peak);
            isWaitingForAck = false;
            lastSenderAckTime = now; // Initialize cool-down timestamp
            
            // Clear any active interval before spawning the next playFrames
            if (sendTimer) clearInterval(sendTimer);
            
            currentBatchIndex++;
            var totalBatches = Math.ceil(qrChunks.length / batchSize);
            if (currentBatchIndex >= totalBatches) {{
                currentBatchIndex = 0; // Loop completed
            }}
            currentFrameIndex = currentBatchIndex * batchSize;
            
            try {{
                playSound('tick');
            }} catch(e) {{}}
            
            playFrames();
        }} else {{
            requestAnimationFrame(detectAckTone);
        }}
    }}

    function togglePlay() {{
        if (isSendingPlaying) {{
            clearInterval(sendTimer);
            isWaitingForAck = false;
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
    }}

    function setupFileChunks(filename, mimeType, sha256, size) {{
        // Clean filename of semicolons to prevent protocol parsing errors
        var cleanName = filename.replace(/;/g, "_");
        
        // Total data chunks (800 chars per frame in file mode)
        var totalDataChunks = Math.ceil(fileBase64.length / 800);
        var total = totalDataChunks + 1; // +1 for Manifest Frame at index 0
        
        qrChunks = [];
        // Frame 0: Manifest Frame
        qrChunks.push("0/" + total + ":" + cleanName + ";" + mimeType + ";" + sha256 + ";" + size);
        
        // Frame 1 to N: Base64 data chunks
        for (var i = 0; i < totalDataChunks; i++) {{
            var start = i * 800;
            var end = start + 800;
            var chunkData = fileBase64.substring(start, end);
            qrChunks.push((i + 1) + "/" + total + ":" + chunkData);
        }}
        
        // Show controls and immediately start playing the loop!
        document.getElementById('qr-wrapper').style.display = 'flex';
        document.getElementById('qr-controls').style.display = 'flex';
        document.getElementById('speed-control').style.display = 'flex';
        
        var qrContainer = document.getElementById("qrcode");
        qrContainer.innerHTML = ''; // Clear
        qrGenerator = new QRCode(qrContainer, {{
            text: "1/1:Init",
            width: 218,
            height: 218,
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
    
    // Acoustic Sync Receiver Variables
    var isReceiverAcousticEnabled = false;
    var receiverAudioCtx = null;
    var lastAckedBatch = -1;
    var lastScannedIndex = -1;
    var lastAckTime = 0;
    
    function toggleReceiverAcoustic(enabled) {{
        isReceiverAcousticEnabled = enabled;
        if (enabled) {{
            if (!receiverAudioCtx) {{
                receiverAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }}
            if (receiverAudioCtx.state === 'suspended') {{
                receiverAudioCtx.resume();
            }}
            // Play a dummy silent tone to unlock iOS audio pipeline immediately
            try {{
                var osc = receiverAudioCtx.createOscillator();
                var gain = receiverAudioCtx.createGain();
                gain.gain.setValueAtTime(0, receiverAudioCtx.currentTime);
                osc.connect(gain);
                gain.connect(receiverAudioCtx.destination);
                osc.start();
                osc.stop(receiverAudioCtx.currentTime + 0.01);
            }} catch(e) {{
                console.warn("Audio unlock failed", e);
            }}
        }}
    }}

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

    function startScanner() {{
        receivedChunks = {{}};
        totalChunks = -1;
        scanResult = "";
        scanFrameCount = 0;
        fileMetadata = null;
        receivedBlob = null;
        lastAckedBatch = -1;
        lastScannedIndex = -1;
        lastAckTime = 0;
        
        document.getElementById('success-box').style.display = 'none';
        document.getElementById('hud-status').style.display = 'block';
        updateScanProgress(0, 0, "Initializing camera...");
        
        var selectedCameraId = document.getElementById('camera-select').value;
        var constraints = {{
            video: selectedCameraId ? {{ deviceId: {{ exact: selectedCameraId }} }} : {{ facingMode: 'environment' }}
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
                var maxDim = 480;
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
                    if (!matched) {{
                        document.getElementById('scan-status').innerText = "QR found (invalid format): " + code.data.substring(0, 15) + "...";
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
        // Protocol matching: index/total:payload
        var regex = /^(\d+)\/(\d+):([\s\S]*)$/;
        var match = regex.exec(data);
        if (!match) return false;
        
        var index = parseInt(match[1]);
        var total = parseInt(match[2]);
        var payload = match[3];
        
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
        
        if (!receivedChunks[index]) {{
            receivedChunks[index] = payload;
            
            // Suppress repeating tick sounds if Acoustic Handshake is enabled
            if (!isReceiverAcousticEnabled) {{
                playSound('tick');
            }}
            
            var count = Object.keys(receivedChunks).length;
            var statusText = fileMetadata ? "Receiving file: " + fileMetadata.name : "Scanning chunks...";
            updateScanProgress(count, total, statusText);
            
            if (count === total) {{
                finishScanning();
            }} else if (isReceiverAcousticEnabled) {{
                // Align 0-based (File) and 1-based (Text) indices for sync range calculation
                var zeroBasedIndex = fileMetadata ? index : index - 1;
                
                // Check if the MacBook rewound/retried the loop
                if (zeroBasedIndex < lastScannedIndex) {{
                    lastAckedBatch = Math.floor(zeroBasedIndex / batchSize) - 1;
                }}
                lastScannedIndex = zeroBasedIndex;
                
                // Determine boundaries of the current batch
                var batchNum = Math.floor(zeroBasedIndex / batchSize);
                var batchStartZero = batchNum * batchSize;
                var batchEndZero = Math.min(batchStartZero + batchSize, total);
                
                // Verify if we have collected all frames in the current range
                var hasAllCurrentBatch = true;
                for (var k = batchStartZero; k < batchEndZero; k++) {{
                    var actualKey = fileMetadata ? k : k + 1;
                    if (!receivedChunks[actualKey]) {{
                        hasAllCurrentBatch = false;
                        break;
                    }}
                }}
                
                if (hasAllCurrentBatch) {{
                    var now = Date.now();
                    if (batchNum > lastAckedBatch) {{
                        playAcousticAck();
                        lastAckedBatch = batchNum;
                        lastAckTime = now;
                    }} else if (batchNum === lastAckedBatch && (now - lastAckTime > 2500)) {{
                        // MacBook missed the previous chime; re-emit ACK
                        playAcousticAck();
                        lastAckTime = now;
                    }}
                }}
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

    function playAcousticAck() {{
        if (!receiverAudioCtx) {{
            receiverAudioCtx = new (window.AudioContext || window.webkitAudioContext)();
        }}
        if (receiverAudioCtx.state === 'suspended') {{
            receiverAudioCtx.resume();
        }}
        console.log("Emitting quiet 15.0 kHz ACK tone");
        
        var osc = receiverAudioCtx.createOscillator();
        var gainNode = receiverAudioCtx.createGain();
        
        osc.type = 'sine';
        osc.frequency.setValueAtTime(15000, receiverAudioCtx.currentTime);
        
        // Drastically lowered volume to a soft, comfortable 5% (0.05) to protect ears/pets
        gainNode.gain.setValueAtTime(0.05, receiverAudioCtx.currentTime);
        
        osc.connect(gainNode);
        gainNode.connect(receiverAudioCtx.destination);
        
        osc.start();
        // Shortened chime to 250ms with a clean fade-out to prevent speaker pop
        gainNode.gain.exponentialRampToValueAtTime(0.0001, receiverAudioCtx.currentTime + 0.25);
        osc.stop(receiverAudioCtx.currentTime + 0.25);
    }}

    function enableFileMode() {{
        chunkSize = 800; // Update the dynamic chunk size
        document.getElementById('text-input-container').style.display = 'none';
        document.getElementById('file-input-container').style.display = 'block';
        document.getElementById('file-mode-badge').style.display = 'inline-flex';
        document.getElementById('chunk-count').innerText = '0 chunks (800 chars/chunk)';
        
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
