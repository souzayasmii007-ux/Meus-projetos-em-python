#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌙 Fases da Lua — App de Desktop Fofinho 🌙
=============================================
Aplicativo com janela própria (tkinter, já incluso no Python) que mostra
a fase da lua de hoje e um calendário mensal navegável, com visual
pastel e bonitinho.

Como rodar:
    python3 fases_lua_app.py

Não precisa instalar nada — tkinter já vem com o Python na maioria
dos sistemas (Windows e macOS trazem por padrão; no Linux, se faltar,
instale com: sudo apt install python3-tk).
"""

import calendar
import tkinter as tk
from datetime import datetime, timedelta

# ───────────────────────── Cálculo das fases ─────────────────────────
SYNODIC_MONTH = 29.53058867
REFERENCE_NEW_MOON = datetime(2000, 1, 6, 18, 14)

# (limite superior da fase, nome, emoji, cor de fundo, cor do texto)
FASES = [
    (0.0,   "Lua Nova",              "🌑", "#E4E1F7", "#5b4e9e"),
    (0.125, "Lua Crescente Côncava", "🌒", "#DCEEFB", "#2f6fa3"),
    (0.25,  "Quarto Crescente",      "🌓", "#DCEEFB", "#2f6fa3"),
    (0.375, "Lua Crescente Gibosa",  "🌔", "#FBEADD", "#b06a2e"),
    (0.5,   "Lua Cheia",             "🌕", "#FDF1D2", "#a3790b"),
    (0.625, "Lua Minguante Gibosa",  "🌖", "#FBEADD", "#b06a2e"),
    (0.75,  "Quarto Minguante",      "🌗", "#FCE4EF", "#a8386b"),
    (0.875, "Lua Minguante Côncava", "🌘", "#E4E1F7", "#5b4e9e"),
    (1.0,   "Lua Nova",              "🌑", "#E4E1F7", "#5b4e9e"),
]

MESES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

DIAS_SEMANA_PT = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]

# Paleta geral do app
COR_FUNDO = "#FFF7FB"
COR_FUNDO_CARD = "#FFFFFF"
COR_TEXTO = "#4a4a4a"
COR_TEXTO_SUAVE = "#8a8a8a"
COR_BOTAO = "#F4D9E8"
COR_BOTAO_TEXTO = "#8a3f66"


def idade_da_lua(dt: datetime) -> float:
    diff = (dt - REFERENCE_NEW_MOON).total_seconds() / 86400.0
    return diff % SYNODIC_MONTH


def fase_da_lua(dt: datetime):
    """Retorna (nome, emoji, cor_fundo, cor_texto, percentual_iluminado)."""
    idade = idade_da_lua(dt)
    posicao = idade / SYNODIC_MONTH

    nome, emoji, cor_fundo, cor_texto = FASES[0][1], FASES[0][2], FASES[0][3], FASES[0][4]
    for i in range(len(FASES) - 1):
        limite_inf, nome_inf, emoji_inf, cf_inf, ct_inf = FASES[i]
        limite_sup = FASES[i + 1][0]
        if limite_inf <= posicao < limite_sup:
            meio = (limite_inf + limite_sup) / 2
            if posicao >= meio:
                nome, emoji, cor_fundo, cor_texto = FASES[i + 1][1], FASES[i + 1][2], FASES[i + 1][3], FASES[i + 1][4]
            else:
                nome, emoji, cor_fundo, cor_texto = nome_inf, emoji_inf, cf_inf, ct_inf
            break

    iluminacao = (1 - abs(posicao - 0.5) / 0.5) * 100 if posicao <= 1 else 0
    return nome, emoji, cor_fundo, cor_texto, round(iluminacao, 1)


# ───────────────────────── Interface (tkinter) ─────────────────────────
class AppFasesLua(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌙 Fases da Lua")
        self.configure(bg=COR_FUNDO)
        self.geometry("420x560")
        self.resizable(False, False)

        hoje = datetime.now()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year

        self._montar_cabecalho()
        self._montar_card_hoje()
        self._montar_navegacao_mes()
        self._montar_calendario()

        self._atualizar_tudo()

    # ---------- Construção da UI ----------
    def _montar_cabecalho(self):
        titulo = tk.Label(
            self, text="🌙 Fases da Lua", font=("Segoe UI", 20, "bold"),
            bg=COR_FUNDO, fg="#c96a9b"
        )
        titulo.pack(pady=(18, 4))

    def _montar_card_hoje(self):
        self.card_hoje = tk.Frame(self, bg=COR_FUNDO_CARD, highlightbackground="#eee0e8",
                                   highlightthickness=1, bd=0)
        self.card_hoje.pack(padx=24, pady=10, fill="x")

        self.lbl_data = tk.Label(self.card_hoje, font=("Segoe UI", 11), fg=COR_TEXTO_SUAVE)
        self.lbl_data.pack(pady=(14, 0))

        self.lbl_emoji = tk.Label(self.card_hoje, font=("Segoe UI Emoji", 46))
        self.lbl_emoji.pack(pady=(4, 0))

        self.lbl_fase = tk.Label(self.card_hoje, font=("Segoe UI", 15, "bold"))
        self.lbl_fase.pack(pady=(0, 6))

        self.canvas_barra = tk.Canvas(self.card_hoje, width=260, height=14,
                                       bg=COR_FUNDO_CARD, highlightthickness=0)
        self.canvas_barra.pack(pady=(0, 4))

        self.lbl_pct = tk.Label(self.card_hoje, font=("Segoe UI", 10), fg=COR_TEXTO_SUAVE,
                                 bg=COR_FUNDO_CARD)
        self.lbl_pct.pack(pady=(0, 14))

    def _montar_navegacao_mes(self):
        nav = tk.Frame(self, bg=COR_FUNDO)
        nav.pack(pady=(14, 4))

        btn_prev = tk.Button(nav, text="◀", font=("Segoe UI", 11), width=3,
                              bg=COR_BOTAO, fg=COR_BOTAO_TEXTO, relief="flat",
                              activebackground="#eec3db", command=self._mes_anterior)
        btn_prev.grid(row=0, column=0, padx=6)

        self.lbl_mes = tk.Label(nav, font=("Segoe UI", 13, "bold"), bg=COR_FUNDO, fg=COR_TEXTO)
        self.lbl_mes.grid(row=0, column=1, padx=10)

        btn_next = tk.Button(nav, text="▶", font=("Segoe UI", 11), width=3,
                              bg=COR_BOTAO, fg=COR_BOTAO_TEXTO, relief="flat",
                              activebackground="#eec3db", command=self._mes_seguinte)
        btn_next.grid(row=0, column=2, padx=6)

    def _montar_calendario(self):
        self.frame_calendario = tk.Frame(self, bg=COR_FUNDO)
        self.frame_calendario.pack(padx=16, pady=6, fill="both", expand=True)

        for col, dia_semana in enumerate(DIAS_SEMANA_PT):
            lbl = tk.Label(self.frame_calendario, text=dia_semana, font=("Segoe UI", 9, "bold"),
                            bg=COR_FUNDO, fg=COR_TEXTO_SUAVE, width=5)
            lbl.grid(row=0, column=col, pady=(0, 4))

    # ---------- Lógica de atualização ----------
    def _atualizar_tudo(self):
        self._atualizar_card_hoje()
        self._atualizar_grade_calendario()

    def _atualizar_card_hoje(self):
        hoje = datetime.now()
        nome, emoji, cor_fundo, cor_texto, iluminacao = fase_da_lua(hoje)

        self.card_hoje.configure(bg=cor_fundo)
        for widget in (self.lbl_data, self.lbl_emoji, self.lbl_fase, self.lbl_pct):
            widget.configure(bg=cor_fundo)

        self.lbl_data.configure(text=hoje.strftime("Hoje, %d de %B de %Y"), fg=cor_texto)
        self.lbl_emoji.configure(text=emoji, bg=cor_fundo)
        self.lbl_fase.configure(text=nome, fg=cor_texto, bg=cor_fundo)
        self.lbl_pct.configure(text=f"{iluminacao}% iluminada", fg=cor_texto, bg=cor_fundo)

        self.canvas_barra.configure(bg=cor_fundo)
        self.canvas_barra.delete("all")
        largura_total = 260
        preenchido = int((iluminacao / 100) * largura_total)
        self.canvas_barra.create_rectangle(0, 0, largura_total, 14, fill="#ffffff", outline="")
        self.canvas_barra.create_rectangle(0, 0, preenchido, 14, fill=cor_texto, outline="")

    def _atualizar_grade_calendario(self):
        # Limpa células antigas (mantém cabeçalho dos dias da semana)
        for widget in self.frame_calendario.grid_slaves():
            info = widget.grid_info()
            if int(info["row"]) > 0:
                widget.destroy()

        self.lbl_mes.configure(text=f"{MESES_PT[self.mes_atual]} de {self.ano_atual}")

        cal = calendar.Calendar(firstweekday=0)  # segunda-feira primeiro
        semanas = cal.monthdayscalendar(self.ano_atual, self.mes_atual)

        for linha, semana in enumerate(semanas, start=1):
            for col, dia in enumerate(semana):
                if dia == 0:
                    continue
                dt = datetime(self.ano_atual, self.mes_atual, dia, 12, 0)
                _, emoji, cor_fundo, cor_texto, _ = fase_da_lua(dt)

                celula = tk.Frame(self.frame_calendario, bg=cor_fundo, width=48, height=42)
                celula.grid(row=linha, column=col, padx=2, pady=2)
                celula.grid_propagate(False)

                lbl_dia = tk.Label(celula, text=str(dia), font=("Segoe UI", 8), bg=cor_fundo, fg=cor_texto)
                lbl_dia.pack()
                lbl_emoji = tk.Label(celula, text=emoji, font=("Segoe UI Emoji", 12), bg=cor_fundo)
                lbl_emoji.pack()

    # ---------- Navegação ----------
    def _mes_anterior(self):
        self.mes_atual -= 1
        if self.mes_atual == 0:
            self.mes_atual = 12
            self.ano_atual -= 1
        self._atualizar_grade_calendario()

    def _mes_seguinte(self):
        self.mes_atual += 1
        if self.mes_atual == 13:
            self.mes_atual = 1
            self.ano_atual += 1
        self._atualizar_grade_calendario()


if __name__ == "__main__":
    app = AppFasesLua()
    app.mainloop()