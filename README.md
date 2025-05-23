# 🦾 Wikipedia Scraper GUI App

A modern, multi-feature Python desktop app for searching, previewing, and exporting Wikipedia articles — built with Tkinter, Requests, Pillow, python-docx, and ReportLab.  
Polished, fast, and super customizable!

---

## ✨ Features

- 🔍 **Smart Search**: Enter any keyword and see a list of matching Wikipedia articles.
- 📋 **Preview on Click**: Double-click any result for a preview snippet before you load the full article.
- 🌐 **Language Support**: Instantly switch between English, French, German, Spanish, Italian, Portuguese, or Romanian Wikipedia.
- 🖼️ **Image Display**: Main article image shown (if available).
- 🖨️ **Export Formats**: Save the article as PDF, TXT, or DOCX — always Unicode-friendly.
- 🖊️ **Custom Fonts & Themes**: Pick your font family, font size, and choose between Light, Dark, Solarized, or Dracula themes.
- 🚦 **Progress Bar**: No more frozen GUIs while searching/loading!
- ↩️ **Back to List**: Jump back and choose another article any time.

---

## 🚀 Quick Start

1. **Clone this repo:**
    ```bash
    git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
    cd YOUR-REPO-NAME
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Run the app:**
    ```bash
    python src/main.py
    ```

---

## 🛠️ Dependencies

- Python 3.7+
- `requests`
- `pillow`
- `reportlab`
- `python-docx`

(See [`requirements.txt`](./requirements.txt) for details)

---

## 📸 **Screenshots**

| Search & Preview                      | Full Article View & Export |
| ------------------------------------- | --------------------------|
| ![search-preview](screenshots/search.png) | ![full-article](screenshots/full.png) |

---

## 🤓 **How it Works**

- **Type your keyword** in the search bar and hit Enter (or click Search).
- **Double-click** a result to preview it.
- **Click “Load Article”** to view the full article (plus image, if available).
- **Export** in your favorite format with the buttons below the article.

---

## 📦 Folder Structure

