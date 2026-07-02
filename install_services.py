import os
import plistlib

def install_services():
    services_dir = os.path.expanduser("~/Library/Services")
    os.makedirs(services_dir, exist_ok=True)
    
    # 1. Share via QR Service
    share_dir = os.path.join(services_dir, "Share via QR.workflow")
    share_contents = os.path.join(share_dir, "Contents")
    share_resources = os.path.join(share_contents, "Resources")
    os.makedirs(share_resources, exist_ok=True)
    
    share_info = {
        "NSServices": [
            {
                "NSMessage": "runWorkflowAsService",
                "NSMenuItem": {
                    "default": "Share via QR"
                },
                "NSSendTypes": ["public.utf8-plain-text"]
            }
        ]
    }
    
    with open(os.path.join(share_contents, "Info.plist"), "wb") as f:
        plistlib.dump(share_info, f)
        
    share_wflow = {
        "actions": [
            {
                "action": {
                    "ActionBundleID": "com.apple.RunShellScript",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "COMMAND_STRING": "TEXT=\"$1\"\nif [ -z \"$TEXT\" ]; then\n  TEXT=$(pbpaste)\nfi\nGIF_PATH=$($HOME/Code/qr-transfer/qr-gif-generator \"$TEXT\")\nopen \"$GIF_PATH\"",
                        "inputMethod": 1,
                        "shell": "/bin/zsh"
                    },
                    "BundleIdentifier": "com.apple.RunShellScript"
                }
            }
        ],
        "workflowMetaData": {
            "serviceInputTypeIdentifier": "com.apple.Automator.text",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu"
        }
    }
    
    with open(os.path.join(share_resources, "document.wflow"), "wb") as f:
        plistlib.dump(share_wflow, f)
        
    # 2. Scan QR Code Service
    scan_dir = os.path.join(services_dir, "Scan QR Code.workflow")
    scan_contents = os.path.join(scan_dir, "Contents")
    scan_resources = os.path.join(scan_contents, "Resources")
    os.makedirs(scan_resources, exist_ok=True)
    
    scan_info = {
        "NSServices": [
            {
                "NSMessage": "runWorkflowAsService",
                "NSMenuItem": {
                    "default": "Scan QR Code"
                }
            }
        ]
    }
    
    with open(os.path.join(scan_contents, "Info.plist"), "wb") as f:
        plistlib.dump(scan_info, f)
        
    scan_wflow = {
        "actions": [
            {
                "action": {
                    "ActionBundleID": "com.apple.RunShellScript",
                    "ActionName": "Run Shell Script",
                    "ActionParameters": {
                        "COMMAND_STRING": "$HOME/Code/qr-transfer/qr-scanner",
                        "inputMethod": 1,
                        "shell": "/bin/zsh"
                    },
                    "BundleIdentifier": "com.apple.RunShellScript"
                }
            }
        ],
        "workflowMetaData": {
            "serviceInputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
            "serviceProcessesInput": 0,
            "workflowTypeIdentifier": "com.apple.Automator.servicesMenu"
        }
    }
    
    with open(os.path.join(scan_resources, "document.wflow"), "wb") as f:
        plistlib.dump(scan_wflow, f)
        
    print("Services installed successfully to ~/Library/Services")

if __name__ == "__main__":
    install_services()
