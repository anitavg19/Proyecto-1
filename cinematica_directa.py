"""
cinematica_directa.py
Brazo Clasificador de Reciclaje — Robot 3R Planar
Cinemática Directa con visualización interactiva

ODS 12: Producción y Consumo Responsables
Curso: Robótica Avanzada — Universidad de Costa Rica
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button

# ──────────────────────────────────────────────
#  PARÁMETROS DEL ROBOT
# ──────────────────────────────────────────────
L1 = 2.0   # Longitud eslabón 1 (boom)
L2 = 1.0   # Longitud eslabón 2 (antebrazo)
L3 = 0.6   # Longitud eslabón 3 (garra)

BASE_X = 0.0
BASE_Y = 2.8  # Base elevada sobre la cinta

# Posiciones de los contenedores
CONTAINERS = {
    "Plástico":  (-2.5, 0.0, "#2196F3"),
    "Vidrio":    ( 0.0, 0.0, "#4CAF50"),
    "Metal":     ( 2.5, 0.0, "#FF9800"),
}


def cinematica_directa(theta1, theta2, theta3):
    """
    Calcula la posición de cada articulación y el efector final.

    Parámetros:
        theta1, theta2, theta3 : ángulos en radianes

    Retorna:
        puntos : lista de (x, y) para base, junta1, junta2, efector
        phi    : orientación total del efector
    """
    # Posición de cada junta
    x0, y0 = BASE_X, BASE_Y

    x1 = x0 + L1 * np.cos(theta1)
    y1 = y0 + L1 * np.sin(theta1)

    x2 = x1 + L2 * np.cos(theta1 + theta2)
    y2 = y1 + L2 * np.sin(theta1 + theta2)

    x3 = x2 + L3 * np.cos(theta1 + theta2 + theta3)
    y3 = y2 + L3 * np.sin(theta1 + theta2 + theta3)

    phi = theta1 + theta2 + theta3

    puntos = [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]
    return puntos, phi


def dibujar_entorno(ax):
    """Dibuja la cinta transportadora y contenedores."""
    # Cinta transportadora
    cinta = patches.FancyBboxPatch((-3.5, -0.3), 7.0, 0.3,
                                   boxstyle="round,pad=0.05",
                                   linewidth=1.5, edgecolor="#555",
                                   facecolor="#888")
    ax.add_patch(cinta)
    ax.text(0, -0.5, "Cinta Transportadora", ha="center",
            fontsize=8, color="#555")

    # Contenedores
    for nombre, (cx, cy, color) in CONTAINERS.items():
        box = patches.FancyBboxPatch((cx - 0.45, cy - 0.8), 0.9, 0.8,
                                     boxstyle="round,pad=0.05",
                                     linewidth=2, edgecolor=color,
                                     facecolor=color + "33")
        ax.add_patch(box)
        ax.text(cx, cy - 1.05, nombre, ha="center",
                fontsize=8, fontweight="bold", color=color)

    # Soporte de la base
    ax.plot([BASE_X, BASE_X], [0, BASE_Y], color="#555",
            linewidth=4, solid_capstyle="round", zorder=1)
    ax.plot(BASE_X, BASE_Y, "ks", markersize=12, zorder=2)


def dibujar_robot(ax, puntos, phi):
    """Dibuja el brazo robótico sobre el eje dado."""
    colores = ["#1565C0", "#1976D2", "#42A5F5"]
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]

    # Eslabones
    for i in range(3):
        ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=colores[i], linewidth=5 - i,
                solid_capstyle="round", zorder=3)

    # Juntas
    for i, (x, y) in enumerate(puntos[:-1]):
        ax.plot(x, y, "o", color="white", markersize=10,
                markeredgecolor="#333", markeredgewidth=1.5, zorder=4)

    # Garra (efector final)
    ax.plot(xs[-1], ys[-1], "D", color="#F44336",
            markersize=10, zorder=5, label="Efector final")

    # Info del efector
    ax.text(xs[-1] + 0.15, ys[-1] + 0.15,
            f"({xs[-1]:.2f}, {ys[-1]:.2f})",
            fontsize=8, color="#F44336", fontweight="bold")


# ──────────────────────────────────────────────
#  INTERFAZ CON SLIDERS
# ──────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 8))
plt.subplots_adjust(left=0.1, bottom=0.28, right=0.95, top=0.93)

ax.set_xlim(-5, 5)
ax.set_ylim(-1.5, 5)
ax.set_aspect("equal")
ax.set_facecolor("#F8F9FA")
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_xlabel("X (m)", fontsize=10)
ax.set_ylabel("Y (m)", fontsize=10)
ax.set_title("Brazo Clasificador de Reciclaje — Cinemática Directa 3R",
             fontsize=12, fontweight="bold", color="#1A237E")

dibujar_entorno(ax)
robot_lines = []

# Valores iniciales
t1_init = np.radians(-60)
t2_init = np.radians(-45)
t3_init = np.radians(-30)

puntos_init, phi_init = cinematica_directa(t1_init, t2_init, t3_init)
dibujar_robot(ax, puntos_init, phi_init)

# Sliders
ax_t1 = plt.axes([0.15, 0.18, 0.70, 0.03])
ax_t2 = plt.axes([0.15, 0.13, 0.70, 0.03])
ax_t3 = plt.axes([0.15, 0.08, 0.70, 0.03])
ax_rst = plt.axes([0.42, 0.02, 0.15, 0.04])

slider_t1 = Slider(ax_t1, "θ₁ (°)", -180, 0,
                   valinit=np.degrees(t1_init), color="#1976D2")
slider_t2 = Slider(ax_t2, "θ₂ (°)", -150, 150,
                   valinit=np.degrees(t2_init), color="#388E3C")
slider_t3 = Slider(ax_t3, "θ₃ (°)", -150, 150,
                   valinit=np.degrees(t3_init), color="#F57C00")
btn_reset = Button(ax_rst, "Reset", color="#EEE", hovercolor="#CCC")

# Panel de información
info_text = ax.text(3.5, 4.5, "", fontsize=9,
                    bbox=dict(boxstyle="round", facecolor="#E3F2FD",
                              edgecolor="#1976D2", alpha=0.9),
                    verticalalignment="top")


def actualizar(val):
    ax.cla()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-1.5, 5)
    ax.set_aspect("equal")
    ax.set_facecolor("#F8F9FA")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xlabel("X (m)", fontsize=10)
    ax.set_ylabel("Y (m)", fontsize=10)
    ax.set_title("Brazo Clasificador de Reciclaje — Cinemática Directa 3R",
                 fontsize=12, fontweight="bold", color="#1A237E")

    dibujar_entorno(ax)

    t1 = np.radians(slider_t1.val)
    t2 = np.radians(slider_t2.val)
    t3 = np.radians(slider_t3.val)

    puntos, phi = cinematica_directa(t1, t2, t3)
    dibujar_robot(ax, puntos, phi)

    x_ef, y_ef = puntos[-1]
    info = (f"Efector final\n"
            f"x = {x_ef:.3f} m\n"
            f"y = {y_ef:.3f} m\n"
            f"φ = {np.degrees(phi):.1f}°\n"
            f"θ₁={slider_t1.val:.1f}°  "
            f"θ₂={slider_t2.val:.1f}°  "
            f"θ₃={slider_t3.val:.1f}°")
    ax.text(3.5, 4.8, info, fontsize=8,
            bbox=dict(boxstyle="round", facecolor="#E3F2FD",
                      edgecolor="#1976D2", alpha=0.9),
            verticalalignment="top")

    fig.canvas.draw_idle()


def reset(event):
    slider_t1.reset()
    slider_t2.reset()
    slider_t3.reset()


slider_t1.on_changed(actualizar)
slider_t2.on_changed(actualizar)
slider_t3.on_changed(actualizar)
btn_reset.on_clicked(reset)

actualizar(None)

plt.show(

