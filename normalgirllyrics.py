import tkinter as tk
from tkinter import messagebox
from pathlib import Path 

import pygame


# O MP3 fica no caminho informado. Se mover o arquivo, atualize este caminho.
MUSIC_FILE = Path(r"C:\Users\PICHAU\Documents\codigos\testes\normalgirl.mp3")

# Tempos iniciais aproximados, em segundos desde o começo do MP3.
# Ajuste o primeiro número de cada linha para sincronizar com a sua versão.
LYRICS = [
    (0.0, "Wanna be the type of girl you take home to your mama"),
    (4.0, "The type of girl, I know your fellas, they'd be proud of"),
    (7.60, "Uh, be proud of, uh, be proud of"),
    (10.00, "Uh, be proud of, boy, you know"),
    (13.10, "Normal girl (normal girl), oh"),
    (17.30, "I wish I was a normal girl, oh, my"),
    (21.10, "How do I be? How do I be your baby?"),
    (24.80, "Normal girl, oh"),
    (29.20, "I wish I was a normal girl"),
    (34.00, "I'll never be, no, never be, uh, oh."),
]

BOX_W, BOX_H = 350, 220
FONT = ("Helvetica", 23, "bold")
BG_COLOR = "#F6EBDD"  # creme
FG_COLOR = "#684B3A"  # marrom
HEART_COLOR = "#9A7460"

RISE_SPEED = 100  # pixels por segundo
BOTTOM_SPAWN_OFFSET = 0
GAP = 35
TYPEWRITER_INTERVAL_MS = 53


class LyricCard:
    def __init__(self, parent, text, x, y):
        self.win = tk.Toplevel(parent)
        self.win.overrideredirect(True)
        self.win.attributes("-topmost", True)
        self.win.configure(bg=BG_COLOR)
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(x)}+{int(y)}")
        self.win.resizable(False, False)

        self.full_text = text
        self.label = tk.Label(
            self.win,
            text="",
            font=FONT,
            bg=BG_COLOR,
            fg=FG_COLOR,
            wraplength=BOX_W - 30,
            justify="center",
        )
        self.label.pack(expand=True, fill="both", padx=15, pady=15)

        # Corações minimalistas nos cantos.
        tk.Label(
            self.win,
            text="♡",
            font=("Segoe UI Symbol", 20),
            bg=BG_COLOR,
            fg=HEART_COLOR,
        ).place(x=12, y=8)
        tk.Label(
            self.win,
            text="♡",
            font=("Segoe UI Symbol", 15),
            bg=BG_COLOR,
            fg=HEART_COLOR,
        ).place(relx=1.0, rely=1.0, x=-30, y=-34)
        self.typewriter_index = 0
        self.x = x
        self.y = float(y)
        self.flip_state = False
        self.typewriter()

    def typewriter(self):
        if self.typewriter_index <= len(self.full_text):
            self.label.config(text=self.full_text[: self.typewriter_index])
            self.typewriter_index += 1
            self.win.after(TYPEWRITER_INTERVAL_MS, self.typewriter)

    def rise(self, dy):
        self.y -= dy
        self.win.geometry(f"{BOX_W}x{BOX_H}+{int(self.x)}+{int(self.y)}")

    def is_offscreen(self):
        return self.y + BOX_H < -50


class LyricFloatApp:
    def __init__(self, root):
        self.root = root
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()
        self.next_lyric_idx = 0
        self.boxes = []
        self.last_frame_time = None
        self.current_side = "left"
        self.playback_started = False

        self.root.withdraw()
        self.root.after(100, self.start)

    def random_safe_x(self):
        center_x = self.screen_w // 2
        spacing = BOX_W + 60
        left_x = max(0, center_x - spacing)
        right_x = min(self.screen_w - BOX_W, center_x + 60)
        if self.current_side == "left":
            self.current_side = "right"
            return left_x
        self.current_side = "left"
        return right_x

    def start(self):
        if not MUSIC_FILE.is_file():
            self.root.deiconify()
            messagebox.showerror(
                "MP3 não encontrado",
                f"Não encontrei o arquivo de música neste caminho:\n{MUSIC_FILE}",
            )
            self.root.destroy()
            return

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(str(MUSIC_FILE))
            pygame.mixer.music.play()
        except pygame.error as error:
            self.root.deiconify()
            messagebox.showerror("Erro ao tocar o MP3", str(error))
            self.root.destroy()
            return

        self.playback_started = True
        self.last_frame_time = pygame.mixer.music.get_pos() / 1000.0
        self.tick()

    def tick(self):
        if not self.playback_started:
            return

        # Usa a posição reportada pelo pygame para acompanhar o áudio tocando.
        audio_pos = pygame.mixer.music.get_pos() / 1000.0
        if audio_pos < 0:  # música terminou
            for box in self.boxes:
                box.win.destroy()
            self.boxes.clear()
            pygame.mixer.quit()
            self.root.destroy()
            return

        dt = max(0.0, audio_pos - self.last_frame_time)
        self.last_frame_time = audio_pos

        while (
            self.next_lyric_idx < len(LYRICS)
            and LYRICS[self.next_lyric_idx][0] <= audio_pos
        ):
            _, text = LYRICS[self.next_lyric_idx]
            x = self.random_safe_x()
            if self.boxes:
                y = self.boxes[-1].y + BOX_H + GAP
            else:
                y = self.screen_h - BOX_H - BOTTOM_SPAWN_OFFSET
            self.boxes.append(LyricCard(self.root, text, x, y))
            self.next_lyric_idx += 1

        dy = RISE_SPEED * dt
        visible_boxes = []
        for box in self.boxes:
            box.rise(dy)
            if box.is_offscreen():
                box.win.destroy()
            else:
                visible_boxes.append(box)
        self.boxes = visible_boxes

        if self.next_lyric_idx < len(LYRICS) or self.boxes:
            self.root.after(16, self.tick)
        else:
            self.root.after(100, self.tick)


if __name__ == "__main__":
    root = tk.Tk()
    app = LyricFloatApp(root)
    root.mainloop()
