# 👁️‍🗨️ Artificial Intelligence-Based Real-Time Human Detection System

A real-time **AI-powered Human Detection System** built using **YOLOv8**, designed for security monitoring and intelligent zone-based alerts. The system accurately detects humans in live video streams, triggers real-time audio warnings, and stores alert data securely.

---

## 🚀 Features

- 🎯 **Real-time human detection** using YOLOv8n  
- 🟩🟧🟥 **Multi-zone monitoring** with color-coded alerts  
  - **Green Zone:** Normal  
  - **Orange Zone:** Caution  
  - **Red Zone:** High alert  
- 🔊 **Audio alerts** for immediate notifications  
- 🗄️ **Secure alert archiving** in PostgreSQL  
- 🌐 **Web interface** built with HTML + CSS + Flask  
- 📊 **Dashboard for viewing past alerts**  
- ⚡ High accuracy and low-latency performance  

---

## 🛠️ Technologies Used

- **Python**  
- **Flask**  
- **YOLOv8 (Ultralytics)**  
- **PostgreSQL**  
- **HTML / CSS**  

---

## 📌 System Description

This project implements an AI-based surveillance system capable of **detecting humans in real time** from a live video feed. The YOLOv8n model is optimized for fast processing and high accuracy.  

The detected person’s location determines the alert level:
- **Green:** Safe  
- **Orange:** Approaching restricted area  
- **Red:** Zone breach — audio alarm triggered  

All alerts—including timestamp, detected zone, and camera source—are securely stored in PostgreSQL for later review.

---

## 🖼️ Screenshot (Add your image)

Place your screenshot in the project folder and add it like this:

```md
![System Screenshot](./screenshot.png)
