# Offline QR Text Transfer

This project provides a native, zero-dependency, and offline-capable solution for transferring text (from simple passwords/URLs to large scripts and notes) between two MacBooks using **animated QR codes**.

It consists of two native binaries compiled on your system (written in Objective-C) and two macOS **Quick Actions (Services)** that tie them into the system.

## Files
- `qr-gif-generator.m`: Objective-C source file for chunking text and rendering the animated QR code GIF.
- `qr-gif-generator`: The compiled, optimized universal binary for the sender.
- `qr-scanner.m`: Objective-C source file for the receiver camera scanning window, HUD UI, and reassembly.
- `qr-scanner`: The compiled, optimized universal binary for the receiver.
- `install.command`: Double-clickable shell script to install files and register the Quick Actions.
- `install_services.py`: Python script to generate and place the `.workflow` folders in `~/Library/Services/`.

For full setup, installation on other devices, and usage instructions, please refer to the system documentation.
