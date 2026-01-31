# Quick Start Guide for FTPChat (**Making FTP Server**)

### Using **ZTE ZXHN H188A** SuperVectoring (Telecom Egypt) — FTP Server Setup Guide

Transform your Telecom Egypt-issued H188A router into a USB-powered FTP server using its default functionality — no firmware flashing or OpenWRT required.

---

## 🧰 Requirements

- **ZTE ZXHN H188A** router (Telecom Egypt / WE)
- USB flash drive formatted as FAT32 or NTFS
- PC or server connected to the router (Windows or Linux)
- Router login credentials (default: `admin` / check label for password)

---

## 🔌 Step 1: Prepare USB Storage

1. Format the USB drive as FAT32 or NTFS.
2. Create folders such as `/Public`, `/Media`, or `/Shared`.
3. Insert the USB drive into the router’s rear USB 2.0 port.
4. Wait 10–20 seconds for detection.

---

## 🌐 Step 2: Access Router Admin Panel

1. Launch a browser and go to: `http://192.168.1.1`.
2. Log in with credentials:
   - Username: `admin`
   - Password: (found on router label)

---

## ⚙️ Step 3: Enable FTP Server

1. Navigate to: `Application > USB Storage > FTP Server`.
2. Enable the FTP service.
3. Choose folders on the USB to share.
4. Set access preferences:
   - **Anonymous** (optional)
   - **User-based** (recommended):
     - Username: `ftpuser`
     - Password: `yourpassword`
     - Permission: Read/Write or Read-Only

---

## 🧪 Step 4: Test FTP Access Locally

### 🖥️ Windows

- Open File Explorer
- Enter: `ftp://192.168.1.1` in the address bar
- Enter credentials if prompted

### 🖥️ Linux (with `curl`)

```bash
curl ftp://ftpuser:yourpassword@192.168.1.1/
```

> 💡 Replace `ftpuser` and `yourpassword` with your actual login. The command lists shared folder contents.

---

## 📊 FTP User & Network Capacity

| Interface         | Max Devices | Notes                             |
| ----------------- | ----------- | --------------------------------- |
| **2.4 GHz Wi-Fi** | ~32 users   | Light browsing and file access    |
| **5 GHz Wi-Fi**   | ~32 users   | Ideal for FTP and media streaming |
| **LAN Ports**     | 3 devices   | Stable, high-speed transfers      |
| **FTP Users**     | 5–10 users  | Stable performance recommended    |

> 🧠 For simultaneous large file transfers, prioritize LAN or 5 GHz. Performance may drop beyond ~10 active users.

---

## ✅ Setup Complete

Your router is now a functional FTP server, ready to share files across your local network.

---

## 🌐 Additional Information

**ZTE ZXHN H188A** SuperVectoring (Telecom Egypt): [Purchase Link](https://bit.ly/supervectoring)

> To acquire this device, Telecom Egypt partnership is required.
