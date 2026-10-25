#!/usr/bin/env python3
"""Generate synthetic benchmark test images for MiniCPM-V 4.7 multimodal benchmark."""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np
import os
import base64

IMAGES_DIR = "benchmark-images"
os.makedirs(IMAGES_DIR, exist_ok=True)

def save(path, dpi=150):
    full_path = os.path.join(IMAGES_DIR, path)
    plt.savefig(full_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.clf()
    print(f"Created: {full_path}")

# ============================================================
# Task 2 — Bar Chart + Line Combined
# ============================================================
fig, ax1 = plt.subplots(figsize=(8, 5))
labels = ['Q1', 'Q2', 'Q3', 'Q4']
b2023 = [45, 62, 78, 95]
b2024 = [58, 71, 88, 110]
line = [20, 28, 35, 42]

x = np.arange(len(labels))
width = 0.35
ax1.bar(x - width/2, b2023, width, label='2023', color='#4A90D9', alpha=0.8)
ax1.bar(x + width/2, b2024, width, label='2024', color='#50C878', alpha=0.8)
ax2 = ax1.twinx()
ax2.plot(x, line, color='#E74C3C', marker='o', linewidth=2, label='Growth %')
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.set_ylabel('Revenue ($K)', color='#333')
ax2.set_ylabel('Growth %', color='#E74C3C')
ax1.legend(loc='upper left', fontsize=8)
ax2.legend(loc='upper right', fontsize=8)
ax1.set_title('Annual Revenue & Growth Rate', fontsize=12, fontweight='bold')
plt.tight_layout()
save('task02-combined-chart.png')

# ============================================================
# Task 9 — Microservices Architecture Diagram
# ============================================================
fig, ax = plt.subplots(figsize=(10, 7))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')

# Title
ax.text(5, 7.5, 'Microservices Architecture', ha='center', fontsize=14, fontweight='bold')

# Boxes for services
services = [
    ('API Gateway', 5, 6.5, '#3498DB'),
    ('User Service', 2, 4.5, '#2ECC71'),
    ('Order Service', 5, 4.5, '#2ECC71'),
    ('Payment Service', 8, 4.5, '#2ECC71'),
    ('PostgreSQL', 2, 2.5, '#F39C12'),
    ('Redis Cache', 5, 2.5, '#E74C3C'),
    ('MongoDB', 8, 2.5, '#F39C12'),
    ('Message Queue', 5, 0.8, '#9B59B6'),
]

for name, x, y, color in services:
    rect = FancyBboxPatch((x-0.7, y-0.35), 1.4, 0.7, boxstyle="round,pad=0.05", 
                          edgecolor=color, facecolor=color, alpha=0.2, linewidth=2)
    ax.add_patch(rect)
    ax.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')

# Arrows between services
arrows = [
    (5, 6.15, 2, 4.85), (5, 6.15, 5, 4.85), (5, 6.15, 8, 4.85),
    (2, 4.15, 2, 2.85), (5, 4.15, 5, 2.85), (8, 4.15, 8, 2.85),
    (5, 2.15, 5, 1.15),
]
for x1, y1, x2, y2 in arrows:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', lw=1.5, color='#555'))

save('task09-microservices-diagram.svg')

# ============================================================
# Task 6 — Math Problem Image
# ============================================================
fig, ax = plt.subplots(figsize=(6, 4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')
ax.text(5, 5, 'Problema de Cálculo', ha='center', fontsize=13, fontweight='bold')
ax.text(1, 4, r'$\int_0^{\infty} x \cdot e^{-x^2} dx$', fontsize=20, ha='left')
ax.text(1, 2.5, 'Hallar el área bajo la curva de:', fontsize=12)
ax.text(1, 1.5, r'$f(x) = x \cdot e^{-x^2}$  para $x \geq 0$', fontsize=14, ha='left')
ax.text(1, 0.5, 'Mostrar todo el procedimiento paso a paso.', fontsize=11)
save('task06-math-problem.png')

# ============================================================
# Task 4 — Visual Logic Puzzle (flow sequence)
# ============================================================
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 3)
ax.axis('off')
ax.text(5, 2.7, '¿Cuál es la siguiente figura en la secuencia?', ha='center', fontsize=13, fontweight='bold')

shapes_x = [1.5, 3, 4.5, 6]
colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']
sizes = [200, 150, 100, 50]
y_center = 1.0
for i, (x, c, s) in enumerate(zip(shapes_x, colors, sizes)):
    if i % 3 == 0:
        circle = plt.Circle((x, y_center), s/1000*3, color=c, zorder=2)
        ax.add_patch(circle)
    elif i % 3 == 1:
        rect = mpatches.Rectangle((x-s/500, y_center-s/1000*3), s/500*2, s/1000*6,
                                  color=c, zorder=2)
        ax.add_patch(rect)
    else:
        triangle = mpatches.RegularPolygon((x, y_center), 3, radius=s/1000*3, color=c, zorder=2)
        ax.add_patch(triangle)
    ax.annotate(str(i+1), (x, y_center), ha='center', va='center', fontsize=10, 
                color='white', fontweight='bold', zorder=3)

# Question mark
circle = mpatches.Circle((7.5, y_center), s/1000*3, color='#95A5A6', zorder=2)
ax.add_patch(circle)
ax.text(7.5, y_center, '?', ha='center', va='center', fontsize=20, color='white', fontweight='bold', zorder=3)
ax.annotate('???', (7.5, 0.2), ha='center', fontsize=10, color='#95A5A6')
save('task04-logic-puzzle.svg')

# ============================================================
# Task 1 — Table (simulated document scan)
# ============================================================
fig, ax = plt.subplots(figsize=(8, 5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')
ax.text(5, 7.5, 'Factura #INV-2024-0892', ha='center', fontsize=14, fontweight='bold')
ax.text(5, 7, 'Empresa XYZ S.A.', ha='center', fontsize=10, color='#666')
ax.text(5, 6.6, f'Fecha: 15/10/2024', ha='center', fontsize=9, color='#666')

table_data = [
    ['Concepto', 'Cantidad', 'Precio Unit.', 'Total'],
    ['Desarrollo Web Frontend', '40h', '$85.00', '$3,400.00'],
    ['API REST Backend', '60h', '$95.00', '$5,700.00'],
    ['Testing Automatizado', '25h', '$75.00', '$1,875.00'],
    ['Deploy & CI/CD Setup', '10h', '$110.00', '$1,100.00'],
    ['Soporte Post-Lanzamiento', 'mes', '$500.00', '$500.00'],
]

y_start = 6.0
row_height = 0.45
for row_idx, row in enumerate(table_data):
    y = y_start - row_idx * row_height
    for col_idx, cell in enumerate(row):
        x = 1 + col_idx * 2.2
        if row_idx == 0:
            ax.text(x, y, cell, ha='left', fontsize=9, fontweight='bold')
        else:
            align = 'right' if col_idx > 0 else 'left'
            ax.text(x, y, cell, ha=align, fontsize=9)
    if row_idx == len(table_data)-1:
        ax.plot([0.5, 9.5], [y-row_height/2, y-row_height/2], 'k-', linewidth=1.5)

total_y = y_start - len(table_data)*row_height + 0.1
ax.text(6.5, total_y, 'TOTAL:', ha='right', fontsize=11, fontweight='bold')
ax.text(7.5, total_y, '$12,575.00', ha='left', fontsize=11, fontweight='bold')
save('task01-document-table.png')

# ============================================================
# Task 11 — Handwritten-style note (using monospace font to simulate)
# ============================================================
fig, ax = plt.subplots(figsize=(6, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 10)
ax.axis('off')
# Add lined paper effect
for y_pos in np.arange(1, 10, 0.5):
    ax.plot([0.5, 9.5], [y_pos, y_pos], 'lightblue', linewidth=0.3, alpha=0.5)
ax.text(1, 9.2, 'Notas reunión — Proyecto Alpha', fontsize=12, fontweight='bold', family='cursive')
notes = [
    '• Revisar documentación técnica pendiente',
    '  - API v2 debe incluir versionado URL',
    '  - Endpoint /api/v2/users necesita auth OAuth2',
    '',
    '• Deadline sprint actual: viernes 25/Oct',
    '• Testing: cubrir casos borde de pagos',
    '• Deploy staging → jueves PM',
    '',
    '• Meeting semanal lunes 10am con equipo QA',
    '  - Reportar bugs críticos del ciclo anterior',
]
for i, note in enumerate(notes):
    ax.text(1, 8.5 - i*0.5, note, fontsize=10, family='monospace', color='#333')
save('task11-handwritten-notes.png')

# ============================================================
# Task 12 — Counting scene (simple geometric composition)
# ============================================================
np.random.seed(42)
fig, ax = plt.subplots(figsize=(8, 6))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8)
ax.axis('off')
ax.text(5, 7.5, 'Escena con objetos variadas', ha='center', fontsize=13, fontweight='bold')

objects = []
for _ in range(8):
    objects.append({'type': 'circle', 'cx': np.random.uniform(1, 9), 'cy': np.random.uniform(1, 7),
                    'r': 0.3, 'color': np.random.choice(['red','blue','green','orange'])})
for _ in range(5):
    objects.append({'type': 'rect', 'x': np.random.uniform(1, 8), 'y': np.random.uniform(1, 6),
                    'w': 0.6, 'h': 0.6, 'color': np.random.choice(['purple','cyan','magenta'])})
for _ in range(4):
    objects.append({'type': 'triangle', 'cx': np.random.uniform(1, 9), 'cy': np.random.uniform(1, 7),
                    'r': 0.3, 'color': np.random.choice(['yellow','brown','pink'])})

for obj in objects:
    if obj['type'] == 'circle':
        ax.add_patch(plt.Circle((obj['cx'], obj['cy']), obj['r'], color=obj['color']))
    elif obj['type'] == 'rect':
        ax.add_patch(mpatches.Rectangle((obj['x'], obj['y']), obj['w'], obj['h'],
                                       facecolor=obj['color'], edgecolor='black', linewidth=0.5))
    elif obj['type'] == 'triangle':
        ax.add_patch(mpatches.RegularPolygon((obj['cx'], obj['cy']), numVertices=3, radius=obj['r'],
                                            facecolor=obj['color'], edgecolor='black', linewidth=0.5))

ax.text(5, 0.3, '¿Cuántos círculos rojos hay? ¿Cuántos triángulos verdes?', 
        ha='center', fontsize=9, style='italic')
save('task12-counting-scene.png')

print("\nAll benchmark images generated!")
print(f"Directory: {IMAGES_DIR}/")
for f in sorted(os.listdir(IMAGES_DIR)):
    path = os.path.join(IMAGES_DIR, f)
    size = os.path.getsize(path)
    print(f"  {f} ({size:,} bytes)")
