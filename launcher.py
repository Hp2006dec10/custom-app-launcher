import tkinter as tk
from tkinter import font, ttk
import subprocess
from PIL import Image, ImageTk
from pathlib import Path

CWD = Path(__file__).parent

COMMANDS = [
    (f"{CWD}/icons/IIITK2-icon.png", "LMS IIITKottayam", "brave https://lmsug24.iiitkottayam.ac.in"),
    (f"{CWD}/icons/ChatGPT.png", "ChatGPT", "brave https://chatgpt.com"),
    (f"{CWD}/icons/whatsapp.webp", "WhatsApp", "brave https://web.whatsapp.com"),
    (f"{CWD}/icons/notion.webp", "Notion", "brave https://notion.so"),
    (f"{CWD}/icons/codeforces.png", "Codeforces", "brave https://codeforces.com")
]

# ---------------- Rounded Button with Icon ----------------
class RoundedButton(tk.Canvas):
    def __init__(
        self, parent, icon_path, text, command,
        height=50, radius=18,
        bg="#2d2d2d", hover="#3a3a3a",
        fg="white", text_font=("Segoe UI", 11)
    ):
        super().__init__(parent, height=height, highlightthickness=0, bg=parent["bg"])
        self.command = command
        self.bg = bg
        self.hover = hover
        self.fg = fg
        self.radius = radius
        self.text = text
        self.text_font = text_font
        self.is_selected = False

        img = Image.open(icon_path).resize((18, 18), Image.LANCZOS)
        self.icon_img = ImageTk.PhotoImage(img)

        self.bind("<Configure>", self.draw)
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.draw(hover=True))
        self.bind("<Leave>", lambda e: self.draw(hover=False))

    def set_selected(self, value: bool):
        self.is_selected = value
        self.draw()

    def draw(self, event=None, hover=False):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        r = self.radius

        if self.is_selected:
            color = "#131313"
        else:
            color = self.hover if hover else self.bg

        # Rounded background
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=color, outline=color)
        self.create_arc((w - r*2, 0, w, r*2), start=0, extent=90, fill=color, outline=color)
        self.create_arc((0, h - r*2, r*2, h), start=180, extent=90, fill=color, outline=color)
        self.create_arc((w - r*2, h - r*2, w, h), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle(r, 0, w - r, h, fill=color, outline=color)
        self.create_rectangle(0, r, w, h - r, fill=color, outline=color)

        # Icon
        cx = 26
        cy = h // 2
        self.create_image(cx, cy, image=self.icon_img)

        # Text
        self.create_text(52, h // 2, anchor="w", text=self.text, fill=self.fg, font=self.text_font)


# ---------------- Launcher App ----------------
class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quick Launcher")
        self.configure(bg="#1e1e1e")
        self.resizable(False, False)
        self.set_centered_size()

        self.selected_index = 0
        self.buttons = []
        self.current_results = COMMANDS.copy()

        self.btn_text_font = font.Font(family="Segoe UI", size=11)
        self.search_font = font.Font(family="Segoe UI", size=11)

        # ---------------- Search Bar ----------------
        search_frame = tk.Frame(self, bg="#1e1e1e")
        search_frame.pack(fill="x", padx=15, pady=(15, 10))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            bg="#2a2a2a",
            fg="white",
            insertbackground="white",
            relief="flat",
            font=self.search_font
        )
        self.search_entry.pack(fill="x", ipady=6, padx=6)

        self.search_entry.bind("<KeyRelease>", self.filter_buttons)
        self.search_entry.bind("<Return>", self.run_selected)
        self.search_entry.bind("<Down>", self.select_next)
        self.search_entry.bind("<Up>", self.select_prev)

        self.after(100, self.search_entry.focus_set)

        # ---------------- Scroll Area ----------------
        container = tk.Frame(self, bg="#1e1e1e")
        container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.list_frame = tk.Frame(self.canvas, bg="#1e1e1e")
        self.window_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")

        self.list_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.window_id, width=e.width))

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.bind_scroll()
        self.create_buttons(COMMANDS)

    # ---------------- Window Size ----------------
    def set_centered_size(self):
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        height = sh // 4 + 50
        width = height * 2
        x = (sw - width) // 2
        y = (sh - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    # ---------------- Create Buttons ----------------
    def create_buttons(self, data):
        self.current_results = data
        self.selected_index = 0
        self.buttons.clear()

        for w in self.list_frame.winfo_children():
            w.destroy()

        for i, (icon, name, cmd) in enumerate(data):
            btn = RoundedButton(
                self.list_frame,
                icon_path=icon,
                text=name,
                command=lambda c=cmd: self.run_command(c),
                text_font=self.btn_text_font
            )
            btn.pack(fill="x", pady=6)
            self.buttons.append(btn)

        self.update_selection()

    # ---------------- Selection Logic ----------------
    def update_selection(self):
        for i, btn in enumerate(self.buttons):
            btn.set_selected(i == self.selected_index)

        if self.buttons:
            self.canvas.update_idletasks()
            btn = self.buttons[self.selected_index]
            self.canvas.yview_moveto(btn.winfo_y() / max(1, self.list_frame.winfo_height()))

    def select_next(self, event=None):
        if not self.buttons:
            return
        self.selected_index = min(self.selected_index + 1, len(self.buttons) - 1)
        self.update_selection()

    def select_prev(self, event=None):
        if not self.buttons:
            return
        self.selected_index = max(self.selected_index - 1, 0)
        self.update_selection()

    # ---------------- Run Selected ----------------
    def run_selected(self, event=None):
        if self.current_results:
            _, _, cmd = self.current_results[self.selected_index]
            self.run_command(cmd)

    # ---------------- Run Command ----------------
    def run_command(self, cmd):
        subprocess.Popen(cmd, shell=True)
        self.destroy()

    # ---------------- Search Filter ----------------
    def filter_buttons(self, event=None):
        if event and event.keysym in ("Up", "Down", "Return"):
            return

        q = self.search_var.get().lower()
        filtered = [c for c in COMMANDS if q in c[1].lower()]
        self.create_buttons(filtered)

    # ---------------- Scroll Bind ----------------
    def bind_scroll(self):
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")


# ---------------- Run ----------------
if __name__ == "__main__":
    app = Launcher()
    app.mainloop()
