import urllib.request
import os

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
        # Patch the minifier bug in qrcode.js where 'b' is only initialized once in the loop header
        qrcode_js = qrcode_js.replace('for(var b=[],d=0,e=this.data.length;e>d;d++){', 'for(var b=[],d=0,e=this.data.length;e>d;d++){b=[];')
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
    </style>
</head>
<body>

<div class="container">
    <header>
        <h1>Offline QR Transfer</h1>
        <p class="subtitle">Secure, fast, paged text transfer via webcam</p>
    </header>

    <div class="tabs">
        <button id="btn-tab-send" class="tab-btn active" onclick="switchTab('send')">Send</button>
        <button id="btn-tab-receive" class="tab-btn" onclick="switchTab('receive')">Receive</button>
    </div>

    <!-- SEND PANEL -->
    <div id="panel-send" class="panel active">
        <textarea id="send-input" placeholder="Type or paste your text here..." oninput="handleInput()"></textarea>
        <div class="char-counter">
            <span id="char-count">0 characters</span>
            <span id="chunk-count">0 chunks (100 chars/chunk)</span>
        </div>
        <button id="btn-start-send" class="btn" onclick="startSending()">Generate QR Loop</button>
        
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
            <button class="btn" style="background: var(--bg-base); border: 1px solid var(--border-card);" onclick="copyResult()">Copy to Clipboard</button>
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

    function handleInput() {{
        var text = document.getElementById('send-input').value;
        document.getElementById('char-count').innerText = text.length + ' characters';
        
        var chunksCount = Math.ceil(text.length / 100);
        document.getElementById('chunk-count').innerText = chunksCount + ' chunks (100 chars/chunk)';
    }}

    function startSending() {{
        var text = document.getElementById('send-input').value.trim();
        if (!text) {{
            alert("Please enter some text to send.");
            return;
        }}
        
        // Stop any current animation
        if (sendTimer) clearInterval(sendTimer);
        
        // Chunk
        var chunkSize = 100;
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
        
        function tickFrame() {{
            if (qrChunks.length === 0) return;
            
            var total = qrChunks.length;
            var payload = qrChunks[currentFrameIndex];
            var headerText = (currentFrameIndex + 1) + "/" + total + ":" + payload;
            
            qrGenerator.clear();
            qrGenerator.makeCode(headerText);
            
            document.getElementById('frame-indicator').innerText = (currentFrameIndex + 1) + " / " + total;
            
            currentFrameIndex = (currentFrameIndex + 1) % total;
        }}
        
        tickFrame(); // Render first frame instantly
        sendTimer = setInterval(tickFrame, frameDuration);
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

    // --- RECEIVER SECTION ---
    var videoElement = document.getElementById('webcam-video');
    var canvasElement = document.createElement('canvas');
    var canvasContext = canvasElement.getContext('2d');
    var cameraStream = null;
    var scanAnimationId = null;
    
    var receivedChunks = {{}};
    var totalChunks = -1;
    var scanResult = "";

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
                    processDecodedText(code.data);
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
        // Protocol matching: index/total:payload
        var regex = /^(\d+)\/(\d+):([\s\S]*)$/;
        var match = regex.exec(data);
        if (!match) return;
        
        var index = parseInt(match[1]);
        var total = parseInt(match[2]);
        var payload = match[3];
        
        if (totalChunks !== -1 && totalChunks !== total) {{
            // Reset if chunk total changes (scanning a new code)
            receivedChunks = {{}};
        }}
        totalChunks = total;
        
        if (!receivedChunks[index]) {{
            receivedChunks[index] = payload;
            playSound('tick');
            
            var count = Object.keys(receivedChunks).length;
            updateScanProgress(count, total, "Scanning chunks...");
            
            if (count === total) {{
                finishScanning();
            }}
        }}
    }}

    function finishScanning() {{
        stopScanner();
        playSound('success');
        
        // Assemble text
        var fullText = "";
        for (var i = 1; i <= totalChunks; i++) {{
            if (receivedChunks[i]) {{
                fullText += receivedChunks[i];
            }}
        }}
        
        scanResult = fullText;
        
        // Update UI
        document.getElementById('hud-status').style.display = 'none';
        document.getElementById('success-box').style.display = 'flex';
        document.getElementById('success-preview').innerText = fullText;
        
        // Attempt auto clipboard copy (might require user interaction on iOS)
        navigator.clipboard.writeText(fullText)
            .then(function() {{
                document.getElementById('scan-status').innerText = "Copied to clipboard!";
            }})
            .catch(function(e) {{
                console.warn("Clipboard auto-copy blocked by iOS security, click copy manually.", e);
            }});
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
