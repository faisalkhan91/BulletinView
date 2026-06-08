# BulletinView 📌

An interactive, real-time digital bulletin board built with Flask and SQLite. Drag-and-drop or paste notes, images, audio, and web links to organize your ideas visually.

![BulletinView Screenshot](assets/images/screenshot.jpg) <!-- Placeholder for screenshot -->

## ✨ Features

- **Toggleable Layouts**: 
  - **Grid View**: Clean, structured organization for quick reading.
  - **Freeform Canvas**: Drag and drop notes anywhere to visually group ideas. Positions are persisted!
- **Interactive UI**: 
  - Floating Action Button (+) for easy note creation.
  - Inline **Edit (✎)** and **Delete (🗑)** controls for every note.
  - **Color Coding**: Choose from 5 different colors to categorize your notes.
- **Multimedia Support**:
  - **Smart Link Previews**: Paste any URL to automatically generate a preview card with image and description.
  - **Drag & Drop / Paste**: Support for images and audio files.
  - **Built-in Players**: Play audio files directly within their notes.
- **Persistence**: Powered by SQLite to keep your notes, colors, and spatial coordinates safe across sessions.

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Flask
- linkpreview

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/BulletinView.git
   cd BulletinView
   ```
2. Install dependencies:
   ```bash
   pip install flask linkpreview
   ```
3. Run the application:
   ```bash
   python BulletinView.py
   ```
4. Open your browser and navigate to `http://localhost:5000`.

## 🛠 Tech Stack
- **Backend**: Python, Flask, SQLite
- **Frontend**: HTML5, CSS3 (Grid/Flexbox), JavaScript, jQuery, jQuery UI
- **Libraries**: linkpreview (for Open Graph data)

## 📄 License
MIT
