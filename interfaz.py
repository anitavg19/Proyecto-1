"""
interfaz.py
Brazo Clasificador de Reciclaje — Interfaz Interactiva Principal
Robot 3R con cinta transportadora animada y clasificación automática

ODS 12: Producción y Consumo Responsables
Curso: Robótica Avanzada — Universidad de Costa Rica
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.animation as animation
from matplotlib.widgets import Button, Slider
import random

# ──────────────────────────────────────────────
#  PARÁMETROS DEL ROBOT
# ──────────────────────────────────────────────
L1, L2, L3 = 1.5, 1.0, 0.6
BASE_X, BASE_Y = 0.0, 2.5
PHI_ABAJO = np.radians(-90)      # Efector apuntando al suelo

# Posiciones de detección e ítems
DETECTION_X    =  0.0            # Donde el brazo recoge el ítem
DETECTION_Y    = -0.05
CONVEYOR_Y     = -0.05
CONVEYOR_SPEED =  0.04

CONTAINERS = {
    "Plástico": {"x": -2.8, "y": 0.0,  "color": "#2196F3", "count": 0},
    "Vidrio":   {"x":  0.0, "y": 0.0,  "color": "#4CAF50", "count": 0},
    "Metal":    {"x":  2.8, "y": 0.0,  "color": "#FF9800", "count": 0},
}

ITEM_COLORS = {
    "Plástico": "#64B5F6",
    "Vidrio":   "#81C784",
    "Metal":    "#FFB74D",
}

ITEM_SHAPES = {
    "Plástico": "o",
    "Vidrio":   "s",
    "Metal":    "^",
}

HOME_ANGLES = (np.radians(-90), np.radians(60), np.radians(30))


# ──────────────────────────────────────────────
#  CINEMÁTICA
# ──────────────────────────────────────────────
def fk(t1, t2, t3):
    x0, y0 = BASE_X, BASE_Y
    x1 = x0 + L1 * np.cos(t1)
    y1 = y0 + L1 * np.sin(t1)
    x2 = x1 + L2 * np.cos(t1 + t2)
    y2 = y1 + L2 * np.sin(t1 + t2)
    x3 = x2 + L3 * np.cos(t1 + t2 + t3)
    y3 = y2 + L3 * np.sin(t1 + t2 + t3)
    return [(x0,y0),(x1,y1),(x2,y2),(x3,y3)]


def ik(xt, yt, phi=PHI_ABAJO, codo_arriba=True):
    xw = xt - L3 * np.cos(phi)
    yw = yt - L3 * np.sin(phi)
    dx, dy = xw - BASE_X, yw - BASE_Y
    d = np.hypot(dx, dy)
    if d > L1 + L2 + 1e-6 or d < abs(L1 - L2) - 1e-6:
        return None
    cos2 = np.clip((d**2 - L1**2 - L2**2) / (2*L1*L2), -1, 1)
    t2 = np.arccos(cos2) if codo_arriba else -np.arccos(cos2)
    alpha = np.arctan2(dy, dx)
    beta  = np.arctan2(L2*np.sin(t2), L1 + L2*np.cos(t2))
    t1 = (alpha - beta) if codo_arriba else (alpha + beta)
    t3 = phi - t1 - t2
    return (t1, t2, t3)


def interpolar_angulos(a_ini, a_fin, t, pasos=30):
    """Genera interpolación suave entre dos configuraciones angulares."""
    idx = min(int(t * pasos), pasos - 1)
    factor = idx / (pasos - 1)
    factor = 0.5 - 0.5 * np.cos(np.pi * factor)  # ease in-out
    return tuple(a + factor * (b - a) for a, b in zip(a_ini, a_fin))


# ──────────────────────────────────────────────
#  ESTADO DE LA SIMULACIÓN
# ──────────────────────────────────────────────
estado = {
    "activo":        False,
    "angulos":       HOME_ANGLES,
    "items_cinta":   [],
    "item_actual":   None,
    "fase":          "espera",   # espera | ir_recoger | recoger | ir_contenedor | depositar | volver
    "paso":          0,
    "total_pasos":   25,
    "target_ang":    HOME_ANGLES,
    "inicio_ang":    HOME_ANGLES,
    "stats":         {"Plástico": 0, "Vidrio": 0, "Metal": 0},
    "velocidad":     1.0,
    "items_clasif":  [],
}


def generar_item():
    tipo = random.choice(list(CONTAINERS.keys()))
    return {
        "tipo":  tipo,
        "x":     -4.5,
        "y":     CONVEYOR_Y,
        "color": ITEM_COLORS[tipo],
        "shape": ITEM_SHAPES[tipo],
    }


# ──────────────────────────────────────────────
#  FIGURA
# ──────────────────────────────────────────────
fig = plt.figure(figsize=(13, 9), facecolor="#1A1A2E")
ax  = fig.add_axes([0.03, 0.18, 0.72, 0.78])

ax.set_facecolor("#16213E")
ax.set_xlim(-5, 5)
ax.set_ylim(-1.8, 5.2)
ax.set_aspect("equal")
ax.tick_params(colors="white")
ax.xaxis.label.set_color("white")
ax.yaxis.label.set_color("white")
ax.set_xlabel("X (m)", fontsize=9)
ax.set_ylabel("Y (m)", fontsize=9)
for spine in ax.spines.values():
    spine.set_edgecolor("#333")

# Panel lateral
ax_panel = fig.add_axes([0.77, 0.18, 0.21, 0.78])
ax_panel.set_facecolor("#0F3460")
ax_panel.set_xlim(0, 1)
ax_panel.set_ylim(0, 1)
ax_panel.set_axis_off()
ax_panel.set_title("Sistema de Clasificación", color="white",
                   fontsize=10, fontweight="bold", pad=8)

# Widgets
ax_btn_start = fig.add_axes([0.05, 0.08, 0.14, 0.06])
ax_btn_stop  = fig.add_axes([0.21, 0.08, 0.14, 0.06])
ax_btn_reset = fig.add_axes([0.37, 0.08, 0.14, 0.06])
ax_vel       = fig.add_axes([0.58, 0.10, 0.18, 0.03])

btn_start = Button(ax_btn_start, "▶ Iniciar",   color="#1B5E20", hovercolor="#2E7D32")
btn_stop  = Button(ax_btn_stop,  "⏸ Pausar",   color="#B71C1C", hovercolor="#C62828")
btn_reset = Button(ax_btn_reset, "⟳ Reiniciar", color="#0D47A1", hovercolor="#1565C0")
slider_vel = Slider(ax_vel, "Velocidad", 0.5, 3.0, valinit=1.0, color="#7B1FA2")

for btn in [btn_start, btn_stop, btn_reset]:
    btn.label.set_color("white")
    btn.label.set_fontweight("bold")


def dibujar_escena():
    ax.cla()
    ax.set_facecolor("#16213E")
    ax.set_xlim(-5, 5)
    ax.set_ylim(-1.8, 5.2)
    ax.set_aspect("equal")
    ax.tick_params(colors="#888")
    ax.set_xlabel("X (m)", color="#888", fontsize=9)
    ax.set_ylabel("Y (m)", color="#888", fontsize=9)
    for spine in ax.spines.values():
        spine.set_edgecolor("#333")
    ax.grid(True, linestyle="--", alpha=0.15, color="#555")

    # Zona de detección
    ax.axvline(DETECTION_X, color="#E91E63", linewidth=1,
               linestyle=":", alpha=0.6)
    ax.text(DETECTION_X + 0.1, 0.8, "Zona\ndetección",
            color="#E91E63", fontsize=7, alpha=0.8)

    # Cinta
    cinta = patches.FancyBboxPatch((-4.6, -0.35), 9.2, 0.35,
                                   boxstyle="round,pad=0.03",
                                   linewidth=1, edgecolor="#555",
                                   facecolor="#37474F")
    ax.add_patch(cinta)
    # Líneas de movimiento de la cinta
    for xi in np.arange(-4.5, 4.5, 0.6):
        ax.plot([xi, xi+0.3], [-0.18, -0.18], color="#546E7A",
                linewidth=1.5, alpha=0.5)

    # Contenedores
    for nombre, data in CONTAINERS.items():
        cx, cy, color = data["x"], data["y"], data["color"]
        # Sombra
        ax.add_patch(patches.FancyBboxPatch(
            (cx-0.48, cy-0.85), 0.96, 0.85,
            boxstyle="round,pad=0.05",
            linewidth=0, facecolor="#000", alpha=0.3,
            zorder=1))
        # Caja
        ax.add_patch(patches.FancyBboxPatch(
            (cx-0.45, cy-0.8), 0.9, 0.8,
            boxstyle="round,pad=0.05",
            linewidth=2, edgecolor=color,
            facecolor=color + "22", zorder=2))
        ax.text(cx, cy - 1.1, nombre, ha="center",
                fontsize=8, fontweight="bold", color=color)
        ax.text(cx, cy - 0.4, str(estado["stats"][nombre]),
                ha="center", fontsize=14, fontweight="bold",
                color=color, zorder=3)

    # Ítems clasificados en contenedores
    for it in estado["items_clasif"]:
        ax.plot(it["x"], it["y"], it["shape"],
                color=it["color"], markersize=6, alpha=0.7, zorder=3)

    # Soporte base
    ax.plot([BASE_X, BASE_X], [0, BASE_Y], color="#90A4AE",
            linewidth=5, solid_capstyle="round", zorder=2)
    ax.add_patch(patches.Circle((BASE_X, BASE_Y), 0.12,
                                 color="#CFD8DC", zorder=3))

    # Ítems en cinta
    for item in estado["items_cinta"]:
        ax.plot(item["x"], item["y"], item["shape"],
                color=item["color"], markersize=10,
                markeredgecolor="white", markeredgewidth=0.8, zorder=4)

    # Robot
    t1, t2, t3 = estado["angulos"]
    puntos = fk(t1, t2, t3)
    colores_esl = ["#42A5F5", "#29B6F6", "#80DEEA"]
    grosor_esl  = [6, 4, 3]
    for i in range(3):
        ax.plot([puntos[i][0], puntos[i+1][0]],
                [puntos[i][1], puntos[i+1][1]],
                color=colores_esl[i],
                linewidth=grosor_esl[i],
                solid_capstyle="round",
                path_effects=[plt.matplotlib.patheffects.SimpleLineShadow(
                    offset=(1,-1), shadow_color="#000", alpha=0.3),
                    plt.matplotlib.patheffects.Normal()],
                zorder=5)

    for i, (px, py) in enumerate(puntos[:-1]):
        size = 10 - i * 2
        ax.plot(px, py, "o", color="white", markersize=size,
                markeredgecolor="#333", markeredgewidth=1.2, zorder=6)

    # Efector final
    ax.plot(puntos[-1][0], puntos[-1][1], "D",
            color="#F44336", markersize=9, zorder=7,
            markeredgecolor="white", markeredgewidth=0.8)

    # Ítem siendo cargado
    if estado["item_actual"] and estado["fase"] in ("ir_contenedor", "depositar", "recoger"):
        ax.plot(puntos[-1][0], puntos[-1][1] + 0.1,
                estado["item_actual"]["shape"],
                color=estado["item_actual"]["color"],
                markersize=10, zorder=8,
                markeredgecolor="white", markeredgewidth=0.8)

    # Info de posición
    x_ef, y_ef = puntos[-1]
    ax.text(-4.8, 5.0,
            f"Efector: ({x_ef:.2f}, {y_ef:.2f}) m  |  "
            f"θ₁={np.degrees(t1):.1f}°  θ₂={np.degrees(t2):.1f}°  θ₃={np.degrees(t3):.1f}°",
            color="#B0BEC5", fontsize=8, zorder=10)

    # Título
    fase_txt = {
        "espera": "⏳ Esperando ítem",
        "ir_recoger": "🔄 Desplazándose a recoger",
        "recoger": "📦 Recogiendo ítem",
        "ir_contenedor": "🚀 Transportando a contenedor",
        "depositar": "✅ Depositando",
        "volver": "🏠 Volviendo a home",
    }.get(estado["fase"], "")

    ax.set_title(f"Brazo Clasificador de Reciclaje  |  {fase_txt}",
                 color="white", fontsize=11, fontweight="bold", pad=6)


def actualizar_panel():
    ax_panel.cla()
    ax_panel.set_facecolor("#0F3460")
    ax_panel.set_xlim(0, 1)
    ax_panel.set_ylim(0, 1)
    ax_panel.set_axis_off()

    total = sum(estado["stats"].values())
    ax_panel.text(0.5, 0.96, "♻ Clasificados", color="white",
                  fontsize=10, fontweight="bold", ha="center",
                  transform=ax_panel.transAxes)
    ax_panel.text(0.5, 0.88, f"Total: {total}", color="#E0E0E0",
                  fontsize=13, fontweight="bold", ha="center",
                  transform=ax_panel.transAxes)

    y_pos = 0.78
    for nombre, data in CONTAINERS.items():
        color = data["color"]
        pct = (estado["stats"][nombre] / total * 100) if total > 0 else 0
        ax_panel.text(0.08, y_pos, f"{ITEM_SHAPES[nombre]} {nombre}",
                      color=color, fontsize=9, fontweight="bold",
                      transform=ax_panel.transAxes)
        ax_panel.text(0.92, y_pos, f"{estado['stats'][nombre]}",
                      color=color, fontsize=11, fontweight="bold",
                      ha="right", transform=ax_panel.transAxes)
        # Barra de progreso
        bar_bg = patches.FancyBboxPatch((0.08, y_pos-0.065), 0.84, 0.04,
                                         boxstyle="round,pad=0.01",
                                         facecolor="#1A3A6A",
                                         transform=ax_panel.transAxes,
                                         zorder=1)
        ax_panel.add_patch(bar_bg)
        if pct > 0:
            bar = patches.FancyBboxPatch((0.08, y_pos-0.065),
                                          0.84 * pct/100, 0.04,
                                          boxstyle="round,pad=0.01",
                                          facecolor=color, alpha=0.8,
                                          transform=ax_panel.transAxes,
                                          zorder=2)
            ax_panel.add_patch(bar)
        y_pos -= 0.15

    ax_panel.text(0.5, 0.25, "ODS 12", color="#FFD54F",
                  fontsize=10, fontweight="bold", ha="center",
                  transform=ax_panel.transAxes)
    ax_panel.text(0.5, 0.18, "Producción y Consumo\nResponsables", color="#FFF9C4",
                  fontsize=8, ha="center", transform=ax_panel.transAxes)

    estado_sim = "▶ ACTIVO" if estado["activo"] else "⏸ PAUSADO"
    color_est  = "#69F0AE" if estado["activo"] else "#FF8A65"
    ax_panel.text(0.5, 0.07, estado_sim, color=color_est,
                  fontsize=10, fontweight="bold", ha="center",
                  transform=ax_panel.transAxes)


def paso_simulacion():
    vel = estado["velocidad"]
    total_p = max(8, int(25 / vel))

    # Mover ítems en la cinta
    for item in estado["items_cinta"]:
        item["x"] += CONVEYOR_SPEED * vel

    # Eliminar ítems que salen de pantalla
    estado["items_cinta"] = [i for i in estado["items_cinta"] if i["x"] < 5.5]

    # Generar nuevos ítems
    if random.random() < 0.015 * vel and len(estado["items_cinta"]) < 4:
        estado["items_cinta"].append(generar_item())

    # Máquina de estados del brazo
    fase = estado["fase"]

    if fase == "espera":
        # Buscar ítem cerca de la zona de detección
        for item in estado["items_cinta"]:
            if abs(item["x"] - DETECTION_X) < 0.2:
                estado["item_actual"] = item
                estado["items_cinta"].remove(item)
                estado["fase"] = "ir_recoger"
                estado["paso"] = 0
                estado["inicio_ang"] = estado["angulos"]
                sol = ik(DETECTION_X, DETECTION_Y + 0.3)
                estado["target_ang"] = sol if sol else HOME_ANGLES
                estado["total_pasos"] = total_p
                break

    elif fase == "ir_recoger":
        estado["paso"] += 1
        t = estado["paso"] / estado["total_pasos"]
        estado["angulos"] = interpolar_angulos(estado["inicio_ang"],
                                               estado["target_ang"],
                                               t, estado["total_pasos"])
        if estado["paso"] >= estado["total_pasos"]:
            estado["fase"] = "recoger"
            estado["paso"] = 0
            estado["total_pasos"] = max(3, int(5 / vel))

    elif fase == "recoger":
        estado["paso"] += 1
        if estado["paso"] >= estado["total_pasos"]:
            tipo = estado["item_actual"]["tipo"]
            cx = CONTAINERS[tipo]["x"]
            cy = CONTAINERS[tipo]["y"] + 0.5
            sol = ik(cx, cy)
            estado["fase"] = "ir_contenedor"
            estado["paso"] = 0
            estado["inicio_ang"] = estado["angulos"]
            estado["target_ang"] = sol if sol else HOME_ANGLES
            estado["total_pasos"] = total_p

    elif fase == "ir_contenedor":
        estado["paso"] += 1
        t = estado["paso"] / estado["total_pasos"]
        estado["angulos"] = interpolar_angulos(estado["inicio_ang"],
                                               estado["target_ang"],
                                               t, estado["total_pasos"])
        if estado["paso"] >= estado["total_pasos"]:
            estado["fase"] = "depositar"
            estado["paso"] = 0
            estado["total_pasos"] = max(3, int(5 / vel))

    elif fase == "depositar":
        estado["paso"] += 1
        if estado["paso"] >= estado["total_pasos"]:
            tipo = estado["item_actual"]["tipo"]
            estado["stats"][tipo] += 1
            CONTAINERS[tipo]["count"] += 1
            # Agregar al acumulado visual
            cx = CONTAINERS[tipo]["x"] + random.uniform(-0.3, 0.3)
            cy_off = -0.3 - (estado["stats"][tipo] % 4) * 0.15
            estado["items_clasif"].append({
                "x": cx, "y": cy_off,
                "color": estado["item_actual"]["color"],
                "shape": estado["item_actual"]["shape"]
            })
            estado["item_actual"] = None
            estado["fase"] = "volver"
            estado["paso"] = 0
            estado["inicio_ang"] = estado["angulos"]
            estado["target_ang"] = HOME_ANGLES
            estado["total_pasos"] = total_p

    elif fase == "volver":
        estado["paso"] += 1
        t = estado["paso"] / estado["total_pasos"]
        estado["angulos"] = interpolar_angulos(estado["inicio_ang"],
                                               HOME_ANGLES,
                                               t, estado["total_pasos"])
        if estado["paso"] >= estado["total_pasos"]:
            estado["angulos"] = HOME_ANGLES
            estado["fase"] = "espera"


def animar(frame):
    if estado["activo"]:
        for _ in range(2):
            paso_simulacion()
    dibujar_escena()
    actualizar_panel()
    return []


def iniciar(event):
    estado["activo"] = True


def pausar(event):
    estado["activo"] = False


def reiniciar(event):
    estado["activo"] = False
    estado["angulos"]      = HOME_ANGLES
    estado["items_cinta"]  = []
    estado["item_actual"]  = None
    estado["fase"]         = "espera"
    estado["paso"]         = 0
    estado["stats"]        = {"Plástico": 0, "Vidrio": 0, "Metal": 0}
    estado["items_clasif"] = []
    for k in CONTAINERS:
        CONTAINERS[k]["count"] = 0


def cambiar_vel(val):
    estado["velocidad"] = slider_vel.val


btn_start.on_clicked(iniciar)
btn_stop.on_clicked(pausar)
btn_reset.on_clicked(reiniciar)
slider_vel.on_changed(cambiar_vel)

# Añadir algunos ítems iniciales
for _ in range(3):
    item = generar_item()
    item["x"] = random.uniform(-4.5, -1.0)
    estado["items_cinta"].append(item)

ani = animation.FuncAnimation(fig, animar, interval=50,
                               blit=False, cache_frame_data=False)

dibujar_escena()
actualizar_panel()

fig.text(0.5, 0.005,
         "Brazo Clasificador de Reciclaje 3R  |  ODS 12  |  Robótica Avanzada — UCR",
         ha="center", color="#546E7A", fontsize=8)

plt.show()
