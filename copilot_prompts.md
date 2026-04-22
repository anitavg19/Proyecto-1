# 🤖 Registro de Prompts — GitHub Copilot

> **Proyecto:** Brazo Clasificador de Reciclaje 3R  
> **Curso:** Robótica Avanzada — Universidad de Costa Rica  
> Este archivo documenta los prompts más importantes utilizados con GitHub Copilot durante el desarrollo del proyecto, junto con una reflexión crítica sobre su uso.

---

## Prompt 1 — Cinemática Directa base

**Archivo:** `cinematica_directa.py`

**Prompt utilizado:**
```
Implement the forward kinematics for a 3R planar robot arm with link lengths L1=1.5, L2=1.0, L3=0.6.
The base is fixed at position (0, 2.5). Given three joint angles theta1, theta2, theta3 in radians,
return the (x, y) position of each joint and the end effector.
```

**Resultado de Copilot:**
Copilot generó correctamente la función usando la suma de transformaciones angulares acumuladas:
- `x1 = x0 + L1*cos(theta1)`
- `x2 = x1 + L2*cos(theta1+theta2)`
- `x3 = x2 + L3*cos(theta1+theta2+theta3)`

**¿Ayudó?** ✅ Sí — generó la estructura base en segundos. Solo se ajustaron los parámetros de la base.

**¿Dónde falló?** ⚠️ Inicialmente no incluyó la posición de la base como offset; asumió que la base estaba en el origen.

---

## Prompt 2 — Cinemática Inversa con ley del coseno

**Archivo:** `cinematica_inversa.py`

**Prompt utilizado:**
```
Write a Python function to compute the inverse kinematics of a 3R planar robot.
The robot has link lengths L1=1.5, L2=1.0, L3=0.6 and base at (0, 2.5).
The end effector orientation phi is fixed at -90 degrees (pointing down).
Use the wrist decoupling method: subtract L3 contribution to get wrist position,
then solve 2R IK for the wrist using the law of cosines.
Return None if the target is outside the workspace.
Support elbow-up and elbow-down configurations.
```

**Resultado de Copilot:**
Generó correctamente el método de desacoplamiento de muñeca y el uso de `arccos` para theta2. También incluyó el manejo del codo arriba/abajo con signo de theta2.

**¿Ayudó?** ✅ Sí — ahorró al menos 30 minutos de derivación matemática manual.

**¿Dónde falló?** ⚠️ No validó correctamente los casos límite del workspace. Hubo errores de dominio en `arccos` cuando el punto estaba justo en el borde. Se tuvo que agregar manualmente `np.clip(cos_t2, -1, 1)`.

---

## Prompt 3 — Animación con Matplotlib

**Archivo:** `interfaz.py`

**Prompt utilizado:**
```
Create a matplotlib animation showing a conveyor belt with items (plastic, glass, metal)
moving from left to right. A 3R robot arm mounted above the belt should detect items
reaching the center, pick them up using inverse kinematics, and deposit them in
labeled containers on each side. Use FuncAnimation. Include start/stop buttons and
a speed slider.
```

**Resultado de Copilot:**
Generó la estructura general de la máquina de estados (fases: espera, ir_recoger, recoger, ir_contenedor, depositar, volver) y el loop de animación básico.

**¿Ayudó?** ✅ Sí — la lógica de la máquina de estados fue sugerida completamente por Copilot y era correcta.

**¿Dónde falló?** ⚠️ La interpolación entre ángulos era lineal y producía movimientos bruscos. Se tuvo que agregar manualmente la interpolación con función de ease-in-out (`0.5 - 0.5*cos(pi*t)`).

---

## Prompt 4 — Visualización del workspace

**Archivo:** `cinematica_inversa.py`

**Prompt utilizado:**
```
Add a function to visualize the reachable workspace of the 3R robot.
Sample points in polar coordinates (angle 0 to 2pi, radius R_min to R_max)
and check which ones have a valid IK solution. Plot them as a scatter plot.
```

**Resultado de Copilot:**
Generó el muestreo polar y el loop de verificación correctamente en el primer intento.

**¿Ayudó?** ✅ Sí — fue una de las respuestas más limpias y directas del proceso.

**¿Dónde falló?** ⚠️ El número de puntos era demasiado alto por defecto (>10,000), lo que hacía el programa muy lento. Se redujo manualmente.

---

## Prompt 5 — Panel de estadísticas

**Archivo:** `interfaz.py`

**Prompt utilizado:**
```
Add a side panel in matplotlib showing real-time classification statistics.
For each material type (Plastic, Glass, Metal), show the count and a horizontal
progress bar. Use dark theme colors matching the main plot.
```

**Resultado de Copilot:**
Generó el panel lateral con `add_axes` y las barras con `FancyBboxPatch`. El estilo visual requirió ajustes manuales de colores y posiciones.

**¿Ayudó?** ✅ Sí — estructuralmente correcto desde el inicio.

**¿Dónde falló?** ⚠️ Los colores por defecto eran muy claros para el tema oscuro. Se ajustaron manualmente todos los valores de color.

---

## 🔍 Reflexión General sobre el uso de GitHub Copilot

### Lo que Copilot hizo muy bien:
- Generó funciones matemáticas estándar (FK, IK con ley del coseno) correctamente en el primer intento cuando el prompt era específico
- Sugirió patrones de código que no habríamos pensado de inmediato (máquina de estados para la animación)
- Aceleró significativamente la escritura de código repetitivo (sliders, botones, configuración de ejes)

### Limitaciones importantes:
- **No entiende contexto acumulado:** en prompts largos olvidaba parámetros definidos al inicio
- **Errores numéricos sutiles:** no manejó casos límite en funciones matemáticas (arccos fuera de [-1,1])
- **Estilo visual genérico:** siempre generó interfaces con estética básica; todo el diseño visual fue ajuste manual
- **Sin validación de lógica propia:** Copilot no "sabe" si la cinemática que generó es físicamente correcta; la verificación fue siempre nuestra responsabilidad

### Aprendizaje clave:
> Copilot es un acelerador, no un sustituto. Los mejores resultados se obtuvieron cuando teníamos claro **qué queríamos** matemáticamente y solo necesitábamos traducirlo a código. Cuando el problema no estaba bien definido en nuestra cabeza, las sugerencias de Copilot también eran vagas.

---

## Prompt 6 — Corrección de parámetros para alcance del workspace

**Archivo:** `interfaz.py`

**Problema detectado:**
El brazo no llegaba al contenedor de Plástico (izquierda). La distancia desde la base hasta el contenedor era ~3.44 m pero el brazo solo alcanzaba 3.1 m con L1=1.5.

**Prompt utilizado:**
```
The robot arm cannot reach the left container at x=-2.8. 
The max reach is L1+L2+L3=3.1m but the distance is ~3.44m.
Suggest new link lengths or base position to make all three 
containers reachable while keeping the robot realistic.
```

**Resultado de Copilot:**
Sugirió aumentar L1 a 2.0 m y ajustar la base a (0, 2.8). También recomendó mover los contenedores a ±2.5 para dar margen de alcance cómodo.

**¿Ayudó?** ✅ Sí — el análisis de workspace fue correcto y resolvió el problema.

**¿Dónde falló?** ⚠️ No mencionó que también había que actualizar cinematica_directa.py y cinematica_inversa.py con los mismos parámetros para mantener consistencia entre archivos.

---

## Prompt 7 — Corrección de importación de patheffects

**Archivo:** `interfaz.py`

**Problema detectado:**
Al correr el script en Windows aparecía: `AttributeError: module 'matplotlib' has no attribute 'patheffects'`

**Prompt utilizado:**
```
Fix this error in interfaz.py: 
AttributeError: module matplotlib has no attribute patheffects.
The code uses plt.matplotlib.patheffects.SimpleLineShadow 
and plt.matplotlib.patheffects.Normal
```

**Resultado de Copilot:**
Identificó que el error era porque `plt.matplotlib` no expone `patheffects` como atributo. La corrección fue agregar `import matplotlib.patheffects as pe` al inicio del archivo y reemplazar todas las referencias.

**¿Ayudó?** ✅ Sí — diagnóstico correcto en el primer intento.

**¿Dónde falló?** ⚠️ El código original que Copilot generó en el Prompt 3 usaba la sintaxis incorrecta `plt.matplotlib.patheffects`, lo que causó este bug posteriormente. Es un ejemplo de error que Copilot introdujo y luego tuvo que corregir.

---

## Prompt 8 — Pausa de cinta transportadora

**Archivo:** `interfaz.py`

**Problema detectado:**
Mientras el brazo recogía y transportaba un ítem, los demás ítems de la cinta seguían moviéndose y pasaban la zona de detección sin ser clasificados.

**Prompt utilizado:**
```
In interfaz.py, items on the conveyor keep moving while the robot 
is busy picking and placing. This causes items to escape without 
being classified. Pause the conveyor movement when the robot is 
not in the waiting phase.
```

**Resultado de Copilot:**
Sugirió agregar una variable `cinta_activa = estado["fase"] == "espera"` y condicionar el movimiento de los ítems a esa variable.

**¿Ayudó?** ✅ Sí — solución limpia y mínima, una sola línea de cambio.

**¿Dónde falló?** ⚠️ No consideró que en una planta real la cinta no se detiene — lo correcto sería un buffer de espera. Para efectos de simulación la pausa fue aceptable.

---

## 🔍 Reflexión General Actualizada

### Errores introducidos por Copilot que luego hubo que corregir:
- Generó `plt.matplotlib.patheffects` (inválido) → se corrigió con import directo
- No validó casos límite de `arccos` → se añadió `np.clip()` manualmente
- Posicionó contenedores fuera del workspace del brazo → se recalcularon parámetros

### Conclusión:
Copilot aceleró el desarrollo pero introdujo al menos 3 bugs que requirieron depuración manual. El flujo real fue: Copilot genera estructura → equipo prueba → equipo corrige → Copilot ayuda a corregir. Nunca fue un proceso de aceptar código sin revisión.


