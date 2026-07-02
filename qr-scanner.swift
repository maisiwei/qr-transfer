import Cocoa
import AVFoundation
import CoreImage
import CoreMedia
import CoreVideo

class ScannerOverlayView: NSView {
    var progress: CGFloat = 0.0
    var statusText: String = "Align camera with the QR code..."
    var scanLineY: CGFloat = 0.0
    var scanLineDirection: CGFloat = 1.0
    var timer: Timer?
    
    override init(frame frameRect: NSRect) {
        super.init(frame: frameRect)
        wantsLayer = true
        timer = Timer.scheduledTimer(withTimeInterval: 0.03, repeats: true) { [weak self] _ in
            self?.updateScanLine()
        }
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
    }
    
    deinit {
        timer?.invalidate()
    }
    
    func updateScanLine() {
        let height = bounds.height
        // Animate scan line up and down
        scanLineY += scanLineDirection * 3.5
        if scanLineY >= height - 60 || scanLineY <= 60 {
            scanLineDirection *= -1
        }
        needsDisplay = true
    }
    
    override func draw(_ dirtyRect: NSRect) {
        super.draw(dirtyRect)
        
        guard let ctx = NSGraphicsContext.current?.cgContext else { return }
        
        let width = bounds.width
        let height = bounds.height
        
        // 1. Draw Scanner Corners (Reticle) in the center
        let reticleSize: CGFloat = 280
        let reticleRect = CGRect(
            x: (width - reticleSize) / 2,
            y: (height - reticleSize) / 2,
            width: reticleSize,
            height: reticleSize
        )
        
        ctx.setStrokeColor(NSColor.systemGreen.withAlphaComponent(0.6).cgColor)
        ctx.setLineWidth(4.0)
        
        let cornerLen: CGFloat = 30
        
        // Top-left corner
        ctx.move(to: CGPoint(x: reticleRect.minX, y: reticleRect.maxY - cornerLen))
        ctx.addLine(to: CGPoint(x: reticleRect.minX, y: reticleRect.maxY))
        ctx.addLine(to: CGPoint(x: reticleRect.minX + cornerLen, y: reticleRect.maxY))
        
        // Top-right corner
        ctx.move(to: CGPoint(x: reticleRect.maxX - cornerLen, y: reticleRect.maxY))
        ctx.addLine(to: CGPoint(x: reticleRect.maxX, y: reticleRect.maxY))
        ctx.addLine(to: CGPoint(x: reticleRect.maxX, y: reticleRect.maxY - cornerLen))
        
        // Bottom-right corner
        ctx.move(to: CGPoint(x: reticleRect.maxX, y: reticleRect.minY + cornerLen))
        ctx.addLine(to: CGPoint(x: reticleRect.maxX, y: reticleRect.minY))
        ctx.addLine(to: CGPoint(x: reticleRect.maxX - cornerLen, y: reticleRect.minY))
        
        // Bottom-left corner
        ctx.move(to: CGPoint(x: reticleRect.minX + cornerLen, y: reticleRect.minY))
        ctx.addLine(to: CGPoint(x: reticleRect.minX, y: reticleRect.minY))
        ctx.addLine(to: CGPoint(x: reticleRect.minX, y: reticleRect.minY + cornerLen))
        
        ctx.strokePath()
        
        // 2. Draw Moving Scan Line
        ctx.setStrokeColor(NSColor.systemGreen.withAlphaComponent(0.8).cgColor)
        ctx.setLineWidth(2.0)
        ctx.move(to: CGPoint(x: reticleRect.minX + 10, y: scanLineY))
        ctx.addLine(to: CGPoint(x: reticleRect.maxX - 10, y: scanLineY))
        ctx.strokePath()
        
        // Draw linear gradient glow behind the scan line
        let colors = [
            NSColor.systemGreen.withAlphaComponent(0.25).cgColor,
            NSColor.clear.cgColor
        ]
        let colorSpace = CGColorSpaceCreateDeviceRGB()
        if let gradient = CGGradient(colorsSpace: colorSpace, colors: colors as CFArray, locations: [0.0, 1.0]) {
            ctx.drawLinearGradient(
                gradient,
                start: CGPoint(x: width / 2, y: scanLineY),
                end: CGPoint(x: width / 2, y: scanLineY - scanLineDirection * 18),
                options: []
            )
        }
        
        // 3. Draw Bottom UI Card (Glassmorphism overlay)
        let uiBoxRect = CGRect(x: 40, y: 30, width: width - 80, height: 80)
        let path = NSBezierPath(roundedRect: uiBoxRect, xRadius: 16, yRadius: 16)
        NSColor.black.withAlphaComponent(0.65).set()
        path.fill()
        
        NSColor.white.withAlphaComponent(0.15).set()
        path.lineWidth = 1.0
        path.stroke()
        
        // 4. Draw Status Text
        let textStyle = NSMutableParagraphStyle()
        textStyle.alignment = .center
        let textFont = NSFont.systemFont(ofSize: 13, weight: .semibold)
        let textAttrs: [NSAttributedString.Key: Any] = [
            .font: textFont,
            .foregroundColor: NSColor.white,
            .paragraphStyle: textStyle
        ]
        
        let textRect = CGRect(x: uiBoxRect.minX + 10, y: uiBoxRect.maxY - 32, width: uiBoxRect.width - 20, height: 22)
        statusText.draw(in: textRect, withAttributes: textAttrs)
        
        // 5. Draw Progress Bar background
        let pBarBgRect = CGRect(x: uiBoxRect.minX + 30, y: uiBoxRect.minY + 18, width: uiBoxRect.width - 60, height: 8)
        let bgPath = NSBezierPath(roundedRect: pBarBgRect, xRadius: 4, yRadius: 4)
        NSColor.white.withAlphaComponent(0.12).set()
        bgPath.fill()
        
        // Draw Progress Bar Fill
        if progress > 0 {
            let pBarFillRect = CGRect(x: pBarBgRect.minX, y: pBarBgRect.minY, width: pBarBgRect.width * progress, height: 8)
            let fillPath = NSBezierPath(roundedRect: pBarFillRect, xRadius: 4, yRadius: 4)
            NSColor.systemGreen.set()
            fillPath.fill()
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate, NSWindowDelegate, AVCaptureVideoDataOutputSampleBufferDelegate {
    var window: NSWindow!
    var captureSession: AVCaptureSession!
    var previewLayer: AVCaptureVideoPreviewLayer!
    var overlayView: ScannerOverlayView!
    var videoDataOutput: AVCaptureVideoDataOutput!
    var videoQueue: DispatchQueue!
    
    // Chunk tracking
    var receivedChunks: [Int: String] = [:]
    var totalChunks: Int? = nil
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        let windowWidth: CGFloat = 640
        let windowHeight: CGFloat = 480
        
        let screenRect = NSScreen.main?.frame ?? CGRect(x: 0, y: 0, width: 1024, height: 768)
        let windowRect = CGRect(
            x: (screenRect.width - windowWidth) / 2,
            y: (screenRect.height - windowHeight) / 2,
            width: windowWidth,
            height: windowHeight
        )
        
        window = NSWindow(
            contentRect: windowRect,
            styleMask: [.titled, .closable, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )
        
        window.title = "Offline Text Scanner"
        window.titlebarAppearsTransparent = true
        window.titleVisibility = .hidden
        window.level = .floating // Floating on top of other windows
        window.delegate = self
        window.isMovableByWindowBackground = true
        
        let contentView = NSView(frame: window.contentView!.bounds)
        contentView.wantsLayer = true
        contentView.layer?.backgroundColor = NSColor.black.cgColor
        window.contentView = contentView
        
        setupCamera()
        
        overlayView = ScannerOverlayView(frame: contentView.bounds)
        overlayView.autoresizingMask = [.width, .height]
        contentView.addSubview(overlayView)
        
        window.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
    
    func setupCamera() {
        captureSession = AVCaptureSession()
        captureSession.sessionPreset = .v1_640x480
        
        guard let videoDevice = AVCaptureDevice.default(for: .video) else {
            showErrorAndExit(message: "No camera device found.")
            return
        }
        
        do {
            let videoInput = try AVCaptureDeviceInput(device: videoDevice)
            if captureSession.canAddInput(videoInput) {
                captureSession.addInput(videoInput)
            } else {
                showErrorAndExit(message: "Cannot add video camera input.")
                return
            }
        } catch {
            showErrorAndExit(message: "Camera initialization failed: \(error.localizedDescription)")
            return
        }
        
        videoDataOutput = AVCaptureVideoDataOutput()
        videoDataOutput.alwaysDiscardsLateVideoFrames = true
        videoQueue = DispatchQueue(label: "videoQueue", qos: .userInteractive)
        videoDataOutput.setSampleBufferDelegate(self, queue: videoQueue)
        
        if captureSession.canAddOutput(videoDataOutput) {
            captureSession.addOutput(videoDataOutput)
        }
        
        previewLayer = AVCaptureVideoPreviewLayer(session: captureSession)
        previewLayer.videoGravity = .resizeAspectFill
        previewLayer.frame = window.contentView!.bounds
        window.contentView!.layer?.addSublayer(previewLayer)
        
        // Request/check authorization status
        let status = AVCaptureDevice.authorizationStatus(for: .video)
        if status == .authorized {
            captureSession.startRunning()
        } else if status == .notDetermined {
            AVCaptureDevice.requestAccess(for: .video) { [weak self] granted in
                DispatchQueue.main.async {
                    if granted {
                        self?.captureSession.startRunning()
                    } else {
                        self?.showErrorAndExit(message: "Camera access permission denied.")
                    }
                }
            }
        } else {
            showErrorAndExit(message: "Camera access is restricted or denied.")
        }
    }
    
    func captureOutput(_ output: AVCaptureOutput, didOutput sampleBuffer: CMSampleBuffer, from connection: AVCaptureConnection) {
        guard let imageBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        
        let ciImage = CIImage(cvImageBuffer: imageBuffer)
        
        // Use high accuracy detector for reliable scanner reading
        let options = [CIDetectorAccuracy: CIDetectorAccuracyHigh]
        guard let detector = CIDetector(ofType: CIDetectorTypeQRCode, context: nil, options: options) else { return }
        
        let features = detector.features(in: ciImage)
        
        for feature in features {
            if let qrFeature = feature as? CIQRCodeFeature, let message = qrFeature.messageString {
                processQRCodeMessage(message)
            }
        }
    }
    
    func processQRCodeMessage(_ message: String) {
        // Regex format matching "index/total:payload"
        let pattern = "^(\\d+)/(\\d+):(.*)$"
        guard let regex = try? NSRegularExpression(pattern: pattern, options: [.dotMatchesLineSeparators]) else { return }
        
        let nsString = message as NSString
        let results = regex.matches(in: message, options: [], range: NSRange(location: 0, length: nsString.length))
        
        guard let match = results.first else { return }
        
        let indexStr = nsString.substring(with: match.range(at: 1))
        let totalStr = nsString.substring(with: match.range(at: 2))
        let payload = nsString.substring(with: match.range(at: 3))
        
        guard let index = Int(indexStr), let total = Int(totalStr) else { return }
        
        DispatchQueue.main.async { [weak self] in
            self?.handleChunkReceived(index: index, total: total, payload: payload)
        }
    }
    
    func handleChunkReceived(index: Int, total: Int, payload: String) {
        if let currentTotal = totalChunks {
            if currentTotal != total {
                // If total chunks count differs, reset state
                receivedChunks.removeAll()
            }
        }
        totalChunks = total
        
        if receivedChunks[index] == nil {
            receivedChunks[index] = payload
            
            // Play audio feedback for successful frame detection
            NSSound(named: "Tink")?.play()
            
            let progressRatio = CGFloat(receivedChunks.count) / CGFloat(total)
            overlayView.progress = progressRatio
            overlayView.statusText = "Received chunk \(receivedChunks.count) of \(total)..."
            overlayView.needsDisplay = true
            
            if receivedChunks.count == total {
                finishScanning()
            }
        }
    }
    
    func finishScanning() {
        captureSession.stopRunning()
        
        guard let total = totalChunks else { return }
        var fullText = ""
        for i in 1...total {
            if let chunk = receivedChunks[i] {
                fullText += chunk
            }
        }
        
        // Write the fully assembled text to pasteboard
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(fullText, forType: .string)
        
        // Play success sound
        NSSound(named: "Glass")?.play()
        
        overlayView.statusText = "Complete! Copied to clipboard."
        overlayView.progress = 1.0
        overlayView.needsDisplay = true
        
        // Exit app after a short delay
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.6) {
            NSApp.terminate(nil)
        }
    }
    
    func showErrorAndExit(message: String) {
        DispatchQueue.main.async {
            fputs("Error: \(message)\n", stderr)
            let alert = NSAlert()
            alert.messageText = "QR Scanner Error"
            alert.informativeText = message
            alert.alertStyle = .critical
            alert.addButton(withTitle: "OK")
            alert.runModal()
            NSApp.terminate(nil)
        }
    }
    
    func windowShouldClose(_ sender: NSWindow) -> Bool {
        NSApp.terminate(nil)
        return true
    }
}

let app = NSApplication.shared
let delegate = AppDelegate()
app.delegate = delegate
app.setActivationPolicy(.accessory)
app.run()
