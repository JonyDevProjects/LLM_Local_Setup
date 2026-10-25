#!/usr/bin/env python3
"""Generate remaining benchmark images (Tasks 5, 7, 8, 10)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, Polygon
import os

IMAGES_DIR = 'benchmark-images'

# Task 5: App UI screenshot mockup
fig, ax = plt.subplots(figsize=(3.5, 6.5))
ax.set_xlim(0, 10); ax.set_ylim(0, 100); ax.axis('off')
ax.add_patch(FancyBboxPatch((0.2, 0.2), 9.6, 99.6, boxstyle='round,pad=0.3', facecolor='#1a1a2e', edgecolor='#333', linewidth=2))
ax.text(1, 96, '9:41 AM', fontsize=5, color='white')
ax.add_patch(FancyBboxPatch((0.5, 88), 9, 6, boxstyle='round,pad=0.3', facecolor='#4CAF50'))
ax.text(5, 91.5, 'MiApp Dashboard', fontsize=7, color='white', ha='center', fontweight='bold')
cards = [('Ventas','$12,580','+15%'), ('Usuarios','1,248','+8%'), ('Pedidos','347','+22%')]
for i, (label, val, pct) in enumerate(cards):
    y = 76 - i*12
    ax.add_patch(FancyBboxPatch((0.7, y), 4, 8, boxstyle='round,pad=0.1', facecolor='#f5f5f5'))
    ax.add_patch(FancyBboxPatch((4.9, y), 4, 8, boxstyle='round,pad=0.1', facecolor='#f5f5f5'))
    ax.text(2.7, y+5, label, fontsize=4, ha='center', color='#666')
    ax.text(2.7, y+2, val, fontsize=6, ha='center', fontweight='bold')
    ax.text(6.9, y+5, 'vs mes anterior', fontsize=3.5, ha='center', color='#aaa')
    ax.text(6.9, y+2, pct, fontsize=5, ha='center', color='#4CAF50', fontweight='bold')
ax.add_patch(FancyBboxPatch((0.7, 38), 8.6, 10, boxstyle='round,pad=0.2', facecolor='white'))
ax.text(1, 46, 'Ultimas transacciones:', fontsize=4.5, color='#333')
for i in range(4):
    clr = '#4CAF50' if i%2==0 else '#f44336'
    ax.add_patch(Rectangle((0.9, 43.5-i*2), 0.8, 1.5, facecolor=clr))
    ax.text(2, 43.5-i*2+0.3, f'Transaccion #{347-i}', fontsize=3.5, color='#333')
plt.tight_layout()
plt.savefig(IMAGES_DIR + '/task05-app-dashboard.png', dpi=150, bbox_inches='tight', facecolor='white')
print('Created: task05-app-dashboard.png')

# Task 7: Before/After
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
for ax, title, heights in [(ax1, 'Antes - Enero 2023', [2,3,4,5]), 
                           (ax2, 'Despues - Enero 2024', [3,4,6,8])]:
    ax.set_xlim(0, 10); ax.set_ylim(0, 8); ax.set_title(title, fontsize=12, fontweight='bold')
    x_pos = [2, 4, 6, 8]
    colors = ['#4A90D9'] if 'Antes' in title else ['#50C878']
    for xp, h in zip(x_pos, heights):
        ax.bar(xp, h, width=1.2, color=colors[0], alpha=0.8)
    ax.axhline(y=4, color='red', linestyle='--', alpha=0.5)
    ax.text(5, 7.5, f'Revenue Q1-Q4: ${sum(heights)*10}K', fontsize=9, ha='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax.set_xticks([]); ax.set_ylabel('Revenue ($K)', fontsize=9)
plt.tight_layout()
plt.savefig(IMAGES_DIR + '/task07-temporal-comparison.png', dpi=150, bbox_inches='tight', facecolor='white')
print('Created: task07-temporal-comparison.png')

# Task 8: Angles
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
pts_data = [
    ('Vista frontal del objeto', [(-1,-1),(1,-1),(1,1),(-1,1)], 'FRENTE', '#4A90D9'),
    ('Vista lateral del mismo objeto', [(0,1.5),(1.5,0),(0,-1.5),(-0.5,0)], 'LATERAL', '#50C878'),
]
for ax, (title, pts, lbl, clr) in zip([ax1, ax2], pts_data):
    ax.set_xlim(-2, 2); ax.set_ylim(-2, 2); ax.set_title(title, fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.add_patch(Polygon(pts, fill=False, edgecolor=clr, linewidth=2))
    ax.text(0, 0, lbl, fontsize=10, ha='center', va='center', color=clr, fontweight='bold')
    ax.set_aspect('equal')
plt.tight_layout()
plt.savefig(IMAGES_DIR + '/task08-angle-variations.png', dpi=150, bbox_inches='tight', facecolor='white')
print('Created: task08-angle-variations.png')

# Task 10: Code photo mockup
fig, ax = plt.subplots(figsize=(6, 8))
ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis('off')
ax.add_patch(Rectangle((0.5, 0.5), 9, 11, facecolor='#FFFACD', edgecolor='#DDD', linewidth=0.5))

code_lines = [
    '# Archivo: inventory_system.py', '',
    'import sqlite3', 'import sys', '',
    'def connect_db(db_path="inventory.db"):',
    '    conn = sqlite3.connect(db_path)',
    '    return conn', '',
    'def get_products(conn):',
    '    cursor = conn.cursor()',
    '    cursor.execute("SELECT * FROM products")',
    '    return cursor.fetchall()', '',
    'def add_product(name, price, qty):',
    r'    cursor.execute(f"INSERT INTO products VALUES',
    r"    (name, price, qty)')",
    '    conn.commit()', '',
    'def calculate_revenue(products):',
    '    total = 0', '    for p in products:',
    '        total += p[1]',
    '    return total', '',
    'if __name__ == "__main__":',
    '    db = connect_db()', '    prods = get_products(db)',
    '    rev = calculate_revenue(prods)',
    '    print(f"Revenue: ${rev}")',
]

y = 11
for line in code_lines:
    ax.text(1, y, line, fontsize=8, family='monospace', color='#2B2B2B')
    y -= 0.35

ax.text(5, 0.3, 'Que hace este codigo? Identifica bugs potenciales.', fontsize=9, style='italic', color='#555')
plt.savefig(IMAGES_DIR + '/task10-code-printed.png', dpi=150, bbox_inches='tight', facecolor='white')
print('Created: task10-code-printed.png')

print('\nAll images generated!')
for f in sorted(os.listdir(IMAGES_DIR)):
    path = os.path.join(IMAGES_DIR, f)
    size = os.path.getsize(path)
    print(f'  {f} ({size:,} bytes)')
