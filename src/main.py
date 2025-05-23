import requests
from tkinter import (
    Tk, Label, Entry, Text, filedialog, END, RIGHT, Y,
    StringVar, OptionMenu, Frame, BooleanVar, messagebox, Listbox, SINGLE, ttk, N, E, S, W, Scrollbar
)
from PIL import Image, ImageTk, UnidentifiedImageError
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
import threading

# === Globals ===
font_size = 12
theme = "Dark"
font_family = "Arial"
article_titles = []
article_snippets = []
progress_bar = None

# === Color Themes (Add More if You Like) ===
THEMES = {
    "Light":  {"bg": "#f0f0f0", "fg": "#000000", "entry": "#ffffff"},
    "Dark":   {"bg": "#1e1e1e", "fg": "#ffffff", "entry": "#2e2e2e"},
    "Dracula": {"bg": "#282a36", "fg": "#f8f8f2", "entry": "#44475a"},
    "Solarized": {"bg": "#fdf6e3", "fg": "#657b83", "entry": "#eee8d5"}
}

FONTS = ["Arial", "Times New Roman", "Courier New", "Verdana", "Comic Sans MS"]

def search_articles_threaded(*args):
    # Show progress bar, then search
    start_progress()
    threading.Thread(target=search_articles).start()

def search_articles():
    topic = entry.get()
    lang = language_var.get()
    if not topic:
        update_status("Please enter a keyword.")
        stop_progress()
        return

    update_status("Searching for articles...")
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "format": "json"
    }

    try:
        response = requests.get(url, params=params)
        results = response.json().get("query", {}).get("search", [])
    except Exception as e:
        update_status("Network error.")
        stop_progress()
        return

    listbox.delete(0, END)
    article_titles.clear()
    article_snippets.clear()

    for res in results:
        title = res["title"]
        snippet = res.get("snippet", "")
        article_titles.append(title)
        article_snippets.append(snippet)
        listbox.insert(END, title)

    if article_titles:
        update_status(f"Found {len(article_titles)} articles.")
        show_list_frame()
    else:
        update_status("No articles found.")

    stop_progress()

def on_listbox_select(event):
    selection = listbox.curselection()
    if selection:
        snippet = article_snippets[selection[0]]
        snippet_clean = snippet.replace('<span class="searchmatch">', '').replace('</span>', '')
        messagebox.showinfo("Article Preview", snippet_clean if snippet_clean else "No preview available.")

def fetch_selected_article_threaded():
    start_progress()
    threading.Thread(target=fetch_selected_article).start()

def fetch_selected_article():
    selection = listbox.curselection()
    if not selection:
        update_status("Select an article from the list.")
        stop_progress()
        return

    title = article_titles[selection[0]]
    fetch_article(title)

def fetch_article(title):
    lang = language_var.get()
    url = f"https://{lang}.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "prop": "extracts|pageimages",
        "titles": title,
        "explaintext": 1,
        "redirects": 1,
        "pithumbsize": 400
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
    except Exception:
        update_status("Network error.")
        stop_progress()
        return

    page = next(iter(data["query"]["pages"].values()))
    content = page.get("extract", "No article found.")
    text_box.delete(1.0, END)
    text_box.insert(END, content)

    # Load image if available and valid
    image_label.pack_forget()
    if "thumbnail" in page:
        image_url = page["thumbnail"]["source"]
        try:
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            img_data = img_response.content
            image_data = Image.open(BytesIO(img_data))
            image_data = image_data.convert("RGB")
            image_data = image_data.resize((200, 200))
            img_tk = ImageTk.PhotoImage(image_data)
            image_label.configure(image=img_tk)
            image_label.image = img_tk
            image_label.pack()
        except (UnidentifiedImageError, Exception):
            image_label.pack_forget()

    update_status(f"Article '{title}' loaded.")
    show_article_frame()
    stop_progress()

def save_as_pdf():
    text = text_box.get(1.0, END).strip()
    if not text:
        update_status("Nothing to save.")
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not file_path:
        update_status("Save cancelled.")
        return

    try:
        c = canvas.Canvas(file_path, pagesize=letter)
        text_object = c.beginText(40, 750)
        text_object.setFont(font_family, font_size)
        max_width = 90
        for line in text.split('\n'):
            while len(line) > max_width:
                text_object.textLine(line[:max_width])
                line = line[max_width:]
            text_object.textLine(line)
        c.drawText(text_object)
        c.save()
        update_status("Saved as PDF.")
    except Exception as e:
        update_status("Failed to save PDF.")
        messagebox.showerror("Error", str(e))

def save_as_txt():
    text = text_box.get(1.0, END).strip()
    if not text:
        update_status("Nothing to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if not file_path:
        update_status("Save cancelled.")
        return
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)
        update_status("Saved as TXT.")
    except Exception as e:
        update_status("Failed to save TXT.")
        messagebox.showerror("Error", str(e))

def save_as_docx():
    text = text_box.get(1.0, END).strip()
    if not text:
        update_status("Nothing to save.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".docx", filetypes=[("Word Document", "*.docx")])
    if not file_path:
        update_status("Save cancelled.")
        return
    try:
        doc = Document()
        doc.styles['Normal'].font.name = font_family
        for line in text.split('\n'):
            doc.add_paragraph(line)
        doc.save(file_path)
        update_status("Saved as DOCX.")
    except Exception as e:
        update_status("Failed to save DOCX.")
        messagebox.showerror("Error", str(e))

def change_theme(selected_theme):
    global theme
    theme = selected_theme
    apply_theme()

def change_font(selected_font):
    global font_family
    font_family = selected_font
    text_box.configure(font=(font_family, font_size))

def toggle_dark_mode():
    # Theme switching via dropdown, but this can be kept for compatibility
    pass

def apply_theme():
    colors = THEMES[theme]
    bg, fg, entry_bg = colors["bg"], colors["fg"], colors["entry"]

    root.configure(bg=bg)
    for widget in root.winfo_children():
        if widget.winfo_class() in ("Frame", "Label", "Button", "Text", "Entry", "OptionMenu", "Listbox", "TButton"):
            try:
                widget.configure(bg=bg, fg=fg)
                if widget.winfo_class() == "Entry":
                    widget.configure(bg=entry_bg, fg=fg, insertbackground=fg)
                if widget.winfo_class() == "Text":
                    widget.configure(bg=entry_bg, fg=fg, insertbackground=fg)
                if widget.winfo_class() == "Button" or widget.winfo_class() == "TButton":
                    widget.configure(activebackground="#5a5a5a")
            except:
                pass
    text_box.configure(font=(font_family, font_size))
    status_label.configure(bg=bg, fg="#aaaaaa")
    if progress_bar:
        progress_bar.configure(mode="indeterminate", maximum=100)
        progress_bar["style"] = "TProgressbar"

def set_font_size(selection):
    global font_size
    font_size = int(selection)
    text_box.configure(font=(font_family, font_size))

def update_status(msg):
    status_label.config(text=msg)

def show_list_frame():
    article_frame.pack_forget()
    list_frame.pack(pady=10)

def show_article_frame():
    list_frame.pack_forget()
    article_frame.pack(pady=10)

def start_progress():
    progress_bar.grid(row=2, column=0, columnspan=10, sticky="ew", padx=10, pady=2)
    progress_bar.start()

def stop_progress():
    progress_bar.stop()
    progress_bar.grid_remove()

# === GUI Setup ===
root = Tk()
root.title("Wikipedia Scraper App")
root.geometry("880x850")

# === Top Frame ===
top_frame = Frame(root)
top_frame.pack(pady=10)

Label(top_frame, text="Search Keyword:").grid(row=0, column=0, padx=5)
entry = Entry(top_frame, width=40)
entry.grid(row=0, column=1, padx=5)
entry.bind('<Return>', search_articles_threaded)  # Search on Enter!

# Use ttk for styled/rounded buttons
style = ttk.Style()
style.configure("Rounded.TButton", relief="flat", padding=6, borderwidth=0, font=('Arial', 10), bordercolor="#cccccc", focusthickness=3)
style.configure("TProgressbar", troughcolor="#444", bordercolor="#888", background="#49f", lightcolor="#49f", darkcolor="#036")

ttk.Button(top_frame, text="Search", command=search_articles_threaded, style="Rounded.TButton").grid(row=0, column=2, padx=5)

font_var = StringVar(value="12")
font_menu = OptionMenu(top_frame, font_var, "10", "12", "14", "16", "18", command=set_font_size)
font_menu.grid(row=0, column=3, padx=5)
Label(top_frame, text="Font Size").grid(row=0, column=4)

font_family_var = StringVar(value=FONTS[0])
font_family_menu = OptionMenu(top_frame, font_family_var, *FONTS, command=change_font)
font_family_menu.grid(row=0, column=5, padx=5)
Label(top_frame, text="Font").grid(row=0, column=6)

language_var = StringVar(value="en")
language_menu = OptionMenu(top_frame, language_var, "en", "fr", "de", "es", "it", "pt", "ro")
language_menu.grid(row=0, column=7, padx=5)
Label(top_frame, text="Lang").grid(row=0, column=8)

theme_var = StringVar(value=theme)
theme_menu = OptionMenu(top_frame, theme_var, *THEMES.keys(), command=change_theme)
theme_menu.grid(row=0, column=9, padx=8)
Label(top_frame, text="Theme").grid(row=0, column=10)

# Progress Bar (initially hidden)
progress_bar = ttk.Progressbar(top_frame, orient="horizontal", mode="indeterminate", length=250)

# === Article List Frame ===
list_frame = Frame(root)

Label(list_frame, text="Select an article (double-click for preview):").pack()
listbox = Listbox(list_frame, width=80, height=10, selectmode=SINGLE)
listbox.pack()
listbox.bind("<Double-Button-1>", on_listbox_select)  # Double-click shows preview

ttk.Button(list_frame, text="Load Article", command=fetch_selected_article_threaded, style="Rounded.TButton").pack(pady=5)

# === Article Display Frame ===
article_frame = Frame(root)
image_label = Label(article_frame)
image_label.pack()

scrollbar = Scrollbar(article_frame)
scrollbar.pack(side=RIGHT, fill=Y)

text_box = Text(article_frame, wrap="word", yscrollcommand=scrollbar.set, height=25, width=100, font=(font_family, font_size))
text_box.pack()
scrollbar.config(command=text_box.yview)

ttk.Button(article_frame, text="Save as PDF", command=save_as_pdf, style="Rounded.TButton").pack(pady=2)
ttk.Button(article_frame, text="Save as TXT", command=save_as_txt, style="Rounded.TButton").pack(pady=2)
ttk.Button(article_frame, text="Save as DOCX", command=save_as_docx, style="Rounded.TButton").pack(pady=2)
ttk.Button(article_frame, text="Back to List", command=show_list_frame, style="Rounded.TButton").pack()

# === Status Bar ===
status_label = Label(root, text="Ready", anchor="w")
status_label.pack(fill="x", side="bottom")

apply_theme()
root.mainloop()
