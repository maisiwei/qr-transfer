# Offline QR Text Transfer

This project provides a secure, zero-dependency, and offline-capable solution for transferring text (from simple passwords/URLs to large scripts and notes) between MacBooks and mobile devices using **animated QR codes**.

It features both **native macOS Quick Actions (Services)** for MacBook-to-MacBook transfers and a **fully responsive, offline Web App** for transfers involving iPhones and other mobile devices.

---

## 🚀 Web App Version (iPhone & Universal)

The Web App version is designed to work on any modern device (iOS, Android, macOS, Windows, Linux) via the browser.

### 🌐 Live Link
You can open the app directly at:
👉 **[https://maisiwei.github.io/qr-transfer/](https://maisiwei.github.io/qr-transfer/)**

### 📱 Installation on iPhone (Add to Home Screen)
To use the Web App like a native mobile app:
1. Open the [Live Link](https://maisiwei.github.io/qr-transfer/) in **Safari** on your iPhone.
2. Tap the **Share** button (box with an up arrow at the bottom).
3. Scroll down and select **Add to Home Screen**.
4. Tap **Add** in the top right corner.

Once added, you can run the app from your home screen. It will load instantly and work **100% offline** (in Airplane Mode) for future uses.

### 🛡️ Corporate Security & Air-Gapped Setup
The Web App is designed with maximum data privacy in mind:
* **No Server Uploads**: 100% of the text generation, camera scanning, and code parsing are performed locally in the browser memory. No data is ever transmitted over the network.
* **Self-Contained**: All libraries (`qrcode.js` and `jsQR.js`) are fully inlined as text inside the HTML. No external scripts are downloaded at runtime.
* **Air-Gap Run**: For absolute security, you can save the file locally (`Save Page As...` -> `index.html`) on your computer, disconnect from the internet entirely, and open it from your local drive.

---

## 💻 Native macOS Quick Actions (Mac-to-Mac)

For seamless MacBook-to-MacBook transfers, you can compile and install the native Objective-C tools.

### Key Features
* **Send QR Loop**: Highlight any text, right-click, select **Services -> Send QR Loop**, and an animated QR code will loop on your screen.
* **Scan QR Loop**: On the receiving MacBook, right-click (or use a shortcut), select **Services -> Scan QR Loop**, and your webcam will open to scan the screen of the sender, automatically reassembling and copying the full text to your clipboard.

### Installation
Double-click `install.command` in the project folder. This will:
1. Compile the native binaries for your Mac's architecture.
2. Create and register the system Quick Actions inside `~/Library/Services/`.

---

## 📂 Project Structure

*   `build_web_app.py`: Python script that pulls CDN dependencies, patches standard `qrcode.js` minification bugs, and compiles the final single-file web app.
*   `index.html` / `qr-transfer.html`: The generated, fully inlined single-file Web App.
*   `qr-gif-generator.m`: Objective-C source code for the native sender binary.
*   `qr-scanner.m`: Objective-C source code for the native receiver camera scanner window.
*   `install.command`: Double-clickable shell script to compile native tools and install Quick Actions.
*   `install_services.py`: Helper script to build the `.workflow` directories.
