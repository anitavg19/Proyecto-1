# ♻️ Brazo Clasificador de Reciclaje — Robot 3R

> **Robótica Avanzada | Universidad de Costa Rica**  
> Proyecto Integrador — Diseño y Simulación de un Sistema Robótico con Interfaz Interactiva  
> **ODS 12: Producción y Consumo Responsables**

---

## 👥 Equipo

| Nombre | Carné |
|--------|-------|
| [Ana 1] | [B98211] |
| [Christofer 2] | [B96464] |
| [Gloriana 3] | [B80941] |
| [Manrique 4] | [B85188] |

---

## 📌 Descripción del Robot

El **Brazo Clasificador de Reciclaje** es un robot planar de 3 grados de libertad (3R) diseñado para automatizar la separación de residuos sólidos en plantas de tratamiento. El robot está montado sobre una cinta transportadora y clasifica ítems de **plástico**, **vidrio** y **metal** depositándolos en sus respectivos contenedores.

### Problema que resuelve
La clasificación manual de residuos es lenta, costosa y peligrosa para los trabajadores. Un robot 3R con cinemática inversa puede detectar y clasificar materiales de forma autónoma, incrementando la eficiencia del proceso y reduciendo la exposición humana a residuos tóxicos.

### Conexión con ODS 12
Este sistema apoya el ODS 12 (Producción y Consumo Responsables) al:
- Aumentar las tasas de recuperación de materiales reciclables
- Reducir el desperdicio industrial mediante automatización precisa
- Disminuir costos operativos de separación de residuos

---

## 🤖 Especificación Técnica

| Parámetro | Valor |
|-----------|-------|
| Tipo de robot | Planar 3R (3 articulaciones revoluta) |
| DOF | 3 |
| Longitud eslabón 1 (L1) | 1.5 m |
| Longitud eslabón 2 (L2) | 1.0 m |
| Longitud eslabón 3 (L3) | 0.6 m |
| Alcance máximo | 3.1 m |
| Alcance mínimo | 0.1 m |
| Posición de la base | (0, 2.5) m |
| Orientación efector | −90° (perpendicular al suelo) |

### Cinemática Directa

Dado $\theta_1, \theta_2, \theta_3$, la posición del efector final es:

$$x = L_1\cos\theta_1 + L_2\cos(\theta_1+\theta_2) + L_3\cos(\theta_1+\theta_2+\theta_3)$$
$$y = L_1\sin\theta_1 + L_2\sin(\theta_1+\theta_2) + L_3\sin(\theta_1+\theta_2+\theta_3)$$

### Cinemática Inversa

Para un punto objetivo $(x_t, y_t)$ con orientación $\phi$:

1. **Posición de muñeca:** $x_w = x_t - L_3\cos\phi$, $y_w = y_t - L_3\sin\phi$
2. **Distancia:** $d = \sqrt{(x_w - x_b)^2 + (y_w - y_b)^2}$
3. **Ley del coseno:** $\cos\theta_2 = \frac{d^2 - L_1^2 - L_2^2}{2L_1L_2}$
4. **Ángulo 1:** $\theta_1 = \text{atan2}(\Delta y, \Delta x) \mp \beta$ (codo arriba/abajo)
5. **Ángulo 3:** $\theta_3 = \phi - \theta_1 - \theta_2$

---

## 📁 Estructura del Repositorio

```
/
├── cinematica_directa.py   # FK con visualización interactiva (sliders)
├── cinematica_inversa.py   # IK con validación de workspace y múltiples soluciones
├── interfaz.py             # Interfaz animada principal con cinta transportadora
├── README.md               # Este archivo
├── copilot_prompts.md      # Registro de prompts usados con GitHub Copilot
└── docs/
    └── informe.pdf         # Documento de diseño del proyecto
```

---

## ⚙️ Instalación

### Requisitos
- Python 3.9 o superior
- pip

### Dependencias

```bash
pip install numpy matplotlib
```

---

## ▶️ Ejecución

### 1. Cinemática Directa
Controla manualmente los 3 ángulos del robot con sliders:
```bash
python cinematica_directa.py
```

### 2. Cinemática Inversa
Mueve el punto objetivo y el robot calcula sus ángulos automáticamente:
```bash
python cinematica_inversa.py
```
- Desliza **X** e **Y** para definir el punto objetivo
- Cambia entre **codo arriba** y **codo abajo**
- La zona azul muestra el workspace alcanzable
- El robot se vuelve rojo si el punto está fuera del workspace

### 3. Interfaz Principal (Simulación Completa)
Animación del robot clasificando ítems en tiempo real:
```bash
python interfaz.py
```
- Presiona **▶ Iniciar** para comenzar la simulación
- Ajusta la **velocidad** con el slider
- Observa los contadores de clasificación en el panel derecho
- Presiona **⟳ Reiniciar** para volver a cero

---

## 🏭 Arquitectura del Sistema Real

| Componente | Tipo | Ejemplo real |
|-----------|------|--------------|
| Sensor de material | Sensor NIR / inductivo / capacitivo | Titech Autosort |
| Actuador articular | Servomotor DC con encoder | Dynamixel MX-64 |
| Garra | Electroimán / ventosa neumática | Schmalz VASB |
| Controlador | PLC / PC industrial | Siemens S7-1200 |
| Visión artificial | Cámara RGB-D | Intel RealSense D435 |

---

## 📊 Resultados esperados

El sistema puede clasificar aproximadamente **15–20 ítems por minuto** en simulación, comparable con sistemas industriales reales de picking robótico de baja velocidad.

---

## 📝 Notas adicionales

- El workspace se visualiza en `cinematica_inversa.py` como la zona de puntos alcanzables
- La IK soporta dos configuraciones: **codo arriba** y **codo abajo**
- Puntos fuera del workspace muestran mensaje de error y no mueven el robot
