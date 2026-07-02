import Cocoa
import CoreImage
import ImageIO
import CoreServices

// Helper to read stdin
func readStdin() -> String? {
    var data = Data()
    while let line = readLine(strippingNewline: false) {
        if let lineData = line.data(using: .utf8) {
            data.append(lineData)
        }
    }
    return String(data: data, encoding: .utf8)
}

func generateQRCode(from string: String) -> CGImage? {
    guard let data = string.data(using: .utf8) else { return nil }
    guard let filter = CIFilter(name: "CIQRCodeGenerator") else { return nil }
    filter.setValue(data, forKey: "inputMessage")
    filter.setValue("M", forKey: "inputCorrectionLevel") // Medium error correction
    guard let ciImage = filter.outputImage else { return nil }
    
    // Scale the image up (CIQRCodeGenerator outputs a tiny image, around 27x27 pixels)
    // We scale to 450x450 to make it large and easy to scan
    let scaleX = 450.0 / ciImage.extent.width
    let scaleY = 450.0 / ciImage.extent.height
    
    // Use CGAffineTransform for scaling
    let scaledImage = ciImage.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))
    
    let context = CIContext(options: [CIContextOption.useSoftwareRenderer: false])
    return context.createCGImage(scaledImage, from: scaledImage.extent)
}

func createGIF(from images: [CGImage], delay: Double, destinationURL: URL) -> Bool {
    guard let destination = CGImageDestinationCreateWithURL(destinationURL as CFURL, kUTTypeGIF, images.count, nil) else {
        return false
    }
    
    // Loop count of 0 makes the GIF loop forever
    let fileProperties = [kCGImagePropertyGIFDictionary as String: [kCGImagePropertyGIFLoopCount as String: 0]]
    CGImageDestinationSetProperties(destination, fileProperties as CFDictionary)
    
    let frameProperties = [kCGImagePropertyGIFDictionary as String: [kCGImagePropertyGIFDelayTime as String: delay]]
    
    for image in images {
        CGImageDestinationAddImage(destination, image, frameProperties as CFDictionary)
    }
    
    return CGImageDestinationFinalize(destination)
}

func main() {
    var text = ""
    
    // 1. Check arguments
    if CommandLine.arguments.count > 1 {
        text = CommandLine.arguments.dropFirst().joined(separator: " ")
    } else {
        // 2. Check stdin
        let isPipable = !isatty(STDIN_FILENO)
        if isPipable, let stdinText = readStdin(), !stdinText.isEmpty {
            text = stdinText
        } else {
            // 3. Check clipboard
            if let clipboardText = NSPasteboard.general.string(forType: .string), !clipboardText.isEmpty {
                text = clipboardText
            }
        }
    }
    
    text = text.trimmingCharacters(in: .whitespacesAndNewlines)
    
    if text.isEmpty {
        fputs("Error: Input text is empty. Please copy some text to clipboard, pass it as an argument, or pipe it to stdin.\n", stderr)
        exit(1)
    }
    
    // Chunk size: 250 characters ensures a very low density QR code that scans instantly
    let chunkSize = 250
    var chunks: [String] = []
    
    let chars = Array(text)
    var index = 0
    while index < chars.count {
        let endIndex = min(index + chunkSize, chars.count)
        let chunkPayload = String(chars[index..<endIndex])
        chunks.append(chunkPayload)
        index += chunkSize
    }
    
    let total = chunks.count
    var qrImages: [CGImage] = []
    
    for (i, payload) in chunks.enumerated() {
        // Format: index/total:payload
        let formattedText = "\(i + 1)/\(total):\(payload)"
        if let cgImage = generateQRCode(from: formattedText) {
            qrImages.append(cgImage)
        } else {
            fputs("Error: Failed to generate QR code for chunk \(i + 1).\n", stderr)
            exit(1)
        }
    }
    
    let tempURL = URL(fileURLWithPath: NSTemporaryDirectory()).appendingPathComponent("qr_transfer.gif")
    // Delay: 0.25 seconds per frame
    let success = createGIF(from: qrImages, delay: 0.25, destinationURL: tempURL)
    
    if success {
        print(tempURL.path)
    } else {
        fputs("Error: Failed to write animated GIF.\n", stderr)
        exit(1)
    }
}

main()
