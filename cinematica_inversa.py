"""
cinematica_inversa.py
Brazo Clasificador de Reciclaje — Robot 3R Planar
Cinemática Inversa con validación de workspace y múltiples soluciones

ODS 12: Producción y Consumo Responsables
Curso: Robótica Avanzada — Universidad de Costa Rica
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Slider, Button, RadioButtons
import matplotlib.patheffects as pe

# ──────────────────────────────────────────────
#  PARÁMETROS DEL ROBOT
# ──────────────────────────────────────────────
L1 = 2.0
L2 = 1.0
L3 = 0.6

BASE_X = 0.0
BASE_Y = 2.8

R_MAX = L1 + L2 + L3          # Alcance máximo
R_MIN = abs(L1 - L2 - L3)     # Alcance mínimo

# Orientación fija del efector (apuntando hacia abajo = -90°)
PHI_DEFAULT = np.radians(-90)

CONTAINERS = {
    "Plástico": (-2.5, 0.0),
    "Vidrio":   ( 0.0, 0.0),
    "Metal":    ( 2.5, 0.0),
}
CONTAINER_COLORS = {
    "Plástico": "#2196F3",
    "Vidrio":   "#4CAF50",
    "Metal":    "#FF9800",
}


def cinematica_directa(theta1, theta2, theta3):
    x0, y0 = BASE_X, BASE_Y
    x1 = x0 + L1 * np.cos(theta1)
    y1 = y0 + L1 * np.sin(theta1)
    x2 = x1 + L2 * np.cos(theta1 + theta2)
    y2 = y1 + L2 * np.sin(theta1 + theta2)
    x3 = x2 + L3 * np.cos(theta1 + theta2 + theta3)
    y3 = y2 + L3 * np.sin(theta1 + theta2 + theta3)
    return [(x0, y0), (x1, y1), (x2, y2), (x3, y3)]


def cinematica_inversa(x_target, y_target, phi=PHI_DEFAULT, codo_arriba=True):
    """
    Calcula θ1, θ2, θ3 para alcanzar (x_target, y_target) con orientación phi.

    Estrategia:
      1. Restar el aporte del eslabón 3 para obtener la muñeca (x_w, y_w).
      2. Resolver IK del sub-robot 2R para la muñeca.
      3. Calcular θ3 = phi - θ1 - θ2.

    Retorna:
        (theta1, theta2, theta3) si hay solución
        None si el punto está fuera del workspace
    """
    # Posición de la muñeca (descontamos eslabón 3)
    x_w = x_target - L3 * np.cos(phi)
    y_w = y_target - L3 * np.sin(phi)

    # Distancia de la base a la muñeca (coordenadas relativas a la base)
    dx = x_w - BASE_X
    dy = y_w - BASE_Y
    d = np.sqrt(dx**2 + dy**2)

    # Validación de workspace
    if d > L1 + L2 + 1e-6:
        return None, "fuera_alcance_max"
    if d < abs(L1 - L2) - 1e-6:
        return None, "fuera_alcance_min"

    # Ley del coseno para θ2
    cos_t2 = (d**2 - L1**2 - L2**2) / (2 * L1 * L2)
    cos_t2 = np.clip(cos_t2, -1, 1)

    if codo_arriba:
        theta2 = np.arccos(cos_t2)
    else:
        theta2 = -np.arccos(cos_t2)

    # θ1 usando atan2
    alpha = np.arctan2(dy, dx)
    beta  = np.arctan2(L2 * np.sin(theta2), L1 + L2 * np.cos(theta2))

    if codo_arriba:
        theta1 = alpha - beta
    else:
        theta1 = alpha + beta

    # θ3 para mantener la orientación deseada
    theta3 = phi - theta1 - theta2

    return (theta1, theta2, theta3), "ok"


def esta_en_workspace(x, y, phi=PHI_DEFAULT):
    """Retorna True si el punto (x,y) es alcanzable."""
    angles, status = cinematica_inversa(x, y, phi)
    return status == "ok"


def dibujar_workspace(ax):
    """Visualiza el workspace alcanzable del robot."""
    puntos_x, puntos_y = [], []
    for angulo in np.linspace(0, 2*np.pi, 360):
        for r in np.linspace(R_MIN, R_MAX, 50):
            px = BASE_X + r * np.cos(angulo)
            py = BASE_Y + r * np.sin(angulo)
            if esta_en_workspace(px, py):
                puntos_x.append(px)
                puntos_y.append(py)
    ax.scatter(puntos_x, puntos_y, c="#E3F2FD", s=2, alpha=0.3,
               zorder=0, label="Workspace alcanzable")


def dibujar_entorno(ax):
    cinta = patches.FancyBboxPatch((-3.5, -0.3), 7.0, 0.3,
                                   boxstyle="round,pad=0.05",
                                   linewidth=1.5, edgecolor="#555",
                                   facecolor="#888")
    ax.add_patch(cinta)
    ax.text(0, -0.5, "Cinta Transportadora", ha="center",
            fontsize=8, color="#555")

    for nombre, (cx, cy) in CONTAINERS.items():
        color = CONTAINER_COLORS[nombre]
        box = patches.FancyBboxPatch((cx-0.45, cy-0.8), 0.9, 0.8,
                                     boxstyle="round,pad=0.05",
                                     linewidth=2, edgecolor=color,
                                     facecolor=color + "33")
        ax.add_patch(box)
        ax.text(cx, cy - 1.05, nombre, ha="center",
                fontsize=8, fontweight="bold", color=color)

    ax.plot([BASE_X, BASE_X], [0, BASE_Y], color="#555",
            linewidth=4, solid_capstyle="round", zorder=1)
    ax.plot(BASE_X, BASE_Y, "ks", markersize=12, zorder=2)


def dibujar_robot(ax, puntos, color_linea="#1565C0"):
    colores = [color_linea, "#1976D2", "#42A5F5"]
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]

    for i in range(3):
        ax.plot([xs[i], xs[i+1]], [ys[i], ys[i+1]],
                color=colores[i], linewidth=5-i,
                solid_capstyle="round", zorder=3)

    for x, y in list(zip(xs, ys))[:-1]:
        ax.plot(x, y, "o", color="white", markersize=10,
                markeredgecolor="#333", markeredgewidth=1.5, zorder=4)

    ax.plot(xs[-1], ys[-1], "D", color="#F44336", markersize=10, zorder=5)


# ──────────────────────────────────────────────
#  FIGURA PRINCIPAL
# ──────────────────────────────────────────────
fig = plt.figure(figsize=(13, 9))
plt.subplots_adjust(left=0.05, bottom=0.28, right=0.75, top=0.93)

ax = fig.add_axes([0.05, 0.28, 0.62, 0.65])
ax.set_xlim(-5, 5)
ax.set_ylim(-1.5, 5.5)
ax.set_aspect("equal")
ax.set_facecolor("#F8F9FA")
ax.grid(True, linestyle="--", alpha=0.4)
ax.set_xlabel("X (m)", fontsize=10)
ax.set_ylabel("Y (m)", fontsize=10)
ax.set_title("Brazo Clasificador de Reciclaje — Cinemática Inversa 3R",
             fontsize=12, fontweight="bold", color="#1A237E")

dibujar_workspace(ax)
dibujar_entorno(ax)

# Target inicial: contenedor plástico
target_x_init = -2.8
target_y_init =  0.2

target_dot, = ax.plot(target_x_init, target_y_init, "*",
                      color="#E91E63", markersize=18, zorder=6,
                      label="Punto objetivo")

# ──────────────────────────────────────────────
#  PANEL LATERAL DE INFORMACIÓN
# ──────────────────────────────────────────────
ax_info = fig.add_axes([0.70, 0.35, 0.27, 0.58])
ax_info.set_axis_off()
info_box = ax_info.text(0.05, 0.98, "", transform=ax_info.transAxes,
                        fontsize=9, verticalalignment="top",
                        bbox=dict(boxstyle="round", facecolor="#E8F5E9",
                                  edgecolor="#388E3C", alpha=0.95))

# ──────────────────────────────────────────────
#  WIDGETS
# ──────────────────────────────────────────────
ax_x   = plt.axes([0.10, 0.18, 0.55, 0.03])
ax_y   = plt.axes([0.10, 0.13, 0.55, 0.03])
ax_phi = plt.axes([0.10, 0.08, 0.55, 0.03])
ax_rst = plt.axes([0.10, 0.02, 0.12, 0.04])

slider_x   = Slider(ax_x,   "X objetivo", -4.5,  4.5, valinit=target_x_init, color="#E91E63")
slider_y   = Slider(ax_y,   "Y objetivo", -1.0,  4.5, valinit=target_y_init, color="#9C27B0")
slider_phi = Slider(ax_phi, "φ (°)",     -180,  180, valinit=np.degrees(PHI_DEFAULT), color="#607D8B")

btn_reset = Button(ax_rst, "Reset", color="#EEE", hovercolor="#CCC")

# Radio buttons para codo arriba/abajo
ax_radio = plt.axes([0.70, 0.10, 0.25, 0.12])
radio = RadioButtons(ax_radio, ("Codo arriba", "Codo abajo"), active=0)
ax_radio.set_title("Configuración", fontsize=9)


def actualizar(val):
    ax.cla()
    ax.set_xlim(-5, 5)
    ax.set_ylim(-1.5, 5.5)
    ax.set_aspect("equal")
    ax.set_facecolor("#F8F9FA")
    ax.grid(True, linestyle="--", alpha=0.4)
    ax.set_xlabel("X (m)", fontsize=10)
    ax.set_ylabel("Y (m)", fontsize=10)
    ax.set_title("Brazo Clasificador de Reciclaje — Cinemática Inversa 3R",
                 fontsize=12, fontweight="bold", color="#1A237E")

    dibujar_workspace(ax)
    dibujar_entorno(ax)

    xt = slider_x.val
    yt = slider_y.val
    phi = np.radians(slider_phi.val)
    codo = (radio.value_selected == "Codo arriba")

    ax.plot(xt, yt, "*", color="#E91E63", markersize=18, zorder=6)

    angles, status = cinematica_inversa(xt, yt, phi, codo)

    if status == "ok":
        t1, t2, t3 = angles
        puntos = cinematica_directa(t1, t2, t3)
        dibujar_robot(ax, puntos)

        # Ambas soluciones (codo arriba y abajo)
        angles2, s2 = cinematica_inversa(xt, yt, phi, not codo)
        if s2 == "ok":
            t1b, t2b, t3b = angles2
            puntos2 = cinematica_directa(t1b, t2b, t3b)
            for i in range(3):
                ax.plot([puntos2[i][0], puntos2[i+1][0]],
                        [puntos2[i][1], puntos2[i+1][1]],
                        color="#BDBDBD", linewidth=2, linestyle="--",
                        alpha=0.5, zorder=2)

        estado = "[OK] Solución encontrada"
        color_info = "#E8F5E9"
        color_borde = "#388E3C"
        info = (f"{estado}\n\n"
                f"Objetivo:\n  x = {xt:.3f} m\n  y = {yt:.3f} m\n"
                f"  φ = {np.degrees(phi):.1f}°\n\n"
                f"Ángulos calculados:\n"
                f"  θ₁ = {np.degrees(t1):.2f}°\n"
                f"  θ₂ = {np.degrees(t2):.2f}°\n"
                f"  θ₃ = {np.degrees(t3):.2f}°\n\n"
                f"Verificación FK:\n"
                f"  x = {puntos[-1][0]:.3f} m\n"
                f"  y = {puntos[-1][1]:.3f} m\n\n"
                f"Configuración:\n  {'Codo arriba ↑' if codo else 'Codo abajo ↓'}\n\n"
                f"Línea gris = solución\nalternativa")
    else:
        motivo = "radio máximo superado" if status == "fuera_alcance_max" \
                 else "radio mínimo no alcanzado"
        estado = f"[X] Sin solución\n({motivo})"
        color_info = "#FFEBEE"
        color_borde = "#C62828"
        info = (f"{estado}\n\n"
                f"Objetivo:\n  x = {xt:.3f} m\n  y = {yt:.3f} m\n\n"
                f"Límites del workspace:\n"
                f"  R_max = {R_MAX:.2f} m\n"
                f"  R_min = {R_MIN:.2f} m\n\n"
                f"Distancia base-objetivo:\n"
                f"  d = {np.sqrt((xt-BASE_X)**2+(yt-BASE_Y)**2):.3f} m")

    ax_info.cla()
    ax_info.set_axis_off()
    ax_info.text(0.05, 0.98, info, transform=ax_info.transAxes,
                 fontsize=9, verticalalignment="top",
                 bbox=dict(boxstyle="round", facecolor=color_info,
                           edgecolor=color_borde, alpha=0.95))

    fig.canvas.draw_idle()


def reset(event):
    slider_x.set_val(target_x_init)
    slider_y.set_val(target_y_init)
    slider_phi.set_val(np.degrees(PHI_DEFAULT))


slider_x.on_changed(actualizar)
slider_y.on_changed(actualizar)
slider_phi.on_changed(actualizar)
radio.on_clicked(actualizar)
btn_reset.on_clicked(reset)

actualizar(None)
plt.show()
