# ================================
# Simulated Annealing Algorithm for Bin Packing Problem
# With Real-Time Visualization of Acceptance Probability
# (Only records acceptance probability when ΔE < 0)
# ================================

import random
import math
import json
import sys
import os
import matplotlib.pyplot as plt
import numpy as np

# ======================
# Load JSON File
# ======================
script_dir = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) > 1:
    json_filename = sys.argv[1]
else:
    json_filename = 'case1.json'

json_path = os.path.join(script_dir, json_filename)

try:
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"Using JSON file: {json_filename}")
except FileNotFoundError:
    print(f"Error: {json_filename} not found!")
    sys.exit(1)

kapasitas_kontainer = data['kapasitas_kontainer']
barang = data['barang'].copy()
jumlah_barang = len(barang)

# ======================
# Inisialisasi
# ======================
kontainer = [[]]
kontainer_space_left = kapasitas_kontainer
kontainer_id = 0

while barang:
    random_index = random.randint(0, len(barang) - 1)
    random_barang = barang[random_index]

    if random_barang['ukuran'] <= kontainer_space_left:
        kontainer[kontainer_id].append({'barang': random_barang})
        kontainer_space_left -= random_barang['ukuran']
        barang.pop(random_index)
    else:
        kontainer_id += 1
        kontainer.append([])
        kontainer_space_left = kapasitas_kontainer

# ======================
# Helper Functions
# ======================
def calculate_kontainer_total(k):
    return sum(item['barang']['ukuran'] for item in k)

def calculate_unused(kontainer, kapasitas):
    total_unused = 0
    for container in kontainer:
        used = calculate_kontainer_total(container)
        total_unused += (kapasitas - used)
    return total_unused

# ======================
# Simulated Annealing Setup
# ======================
min_ukuran = min(item['barang']['ukuran'] for sublist in kontainer for item in sublist)
max_ukuran = max(item['barang']['ukuran'] for sublist in kontainer for item in sublist)

temperature = max_ukuran - min_ukuran
alpha = 0.925
min_temperature = 0.1
best_case_unused = calculate_unused(kontainer, kapasitas_kontainer)

acceptance_probs = []
iterations = []

# ======================
# Matplotlib Setup (Real-time)
# ======================
plt.ion()
fig, ax = plt.subplots(figsize=(10, 5))
line, = ax.plot([], [], 'b-', linewidth=2, label='Acceptance Probability (ΔE < 0 only)')
ax.set_xlim(0, 50)
ax.set_ylim(0, 1.05)
ax.set_xlabel('Iteration', fontsize=12)
ax.set_ylabel('Probability', fontsize=12)
ax.set_title('Acceptance Probability over Iterations (ΔE < 0)', fontsize=14, fontweight='bold')
ax.grid(True)
ax.legend()

# ======================
# Main Simulated Annealing Loop
# ======================
iteration = 0
while temperature > min_temperature:
    improved = False

    for i in range(len(kontainer)):
        for j in range(i + 1, len(kontainer)):
            for index_i in range(len(kontainer[i])):
                for index_j in range(len(kontainer[j])):
                    current_total_i = calculate_kontainer_total(kontainer[i])
                    if current_total_i >= kapasitas_kontainer:
                        continue

                    current_total_j = calculate_kontainer_total(kontainer[j])
                    barang_i = kontainer[i][index_i]['barang']
                    barang_j = kontainer[j][index_j]['barang']

                    new_total_i = current_total_i - barang_i['ukuran'] + barang_j['ukuran']
                    new_total_j = current_total_j - barang_j['ukuran'] + barang_i['ukuran']

                    current_unused = (kapasitas_kontainer - current_total_i)
                    new_unused = (kapasitas_kontainer - new_total_i)
                    delta_E = new_unused - current_unused
                    probability = math.exp(delta_E / temperature) if temperature != 0 else 0

                    # -------------------------
                    # Save probability only if ΔE < 0 (worse solution)
                    # -------------------------
                    if delta_E < 0:
                        iterations.append(iteration)
                        acceptance_probs.append(min(probability, 1.0))

                        # Update real-time plot
                        line.set_xdata(range(len(acceptance_probs)))
                        line.set_ydata(acceptance_probs)
                        if len(acceptance_probs) > ax.get_xlim()[1]:
                            ax.set_xlim(0, len(acceptance_probs))
                        ax.relim()
                        ax.autoscale_view(True, True, True)
                        fig.canvas.draw_idle()
                        plt.pause(0.001)

                    # -------------------------
                    # SA Acceptance Decision
                    # -------------------------
                    if delta_E > 0:
                        # Better solution → accept automatically
                        kontainer[i][index_i]['barang'] = barang_j
                        kontainer[j][index_j]['barang'] = barang_i
                        improved = True
                    else:
                        # Worse solution → accept with probability
                        if random.random() < probability:
                            kontainer[i][index_i]['barang'] = barang_j
                            kontainer[j][index_j]['barang'] = barang_i
                            improved = True

                    iteration += 1

    temperature *= alpha
    if not improved:
        break

# ======================
# Print Result
# ======================
print("\n=== FINAL CONTAINER ARRANGEMENT ===")
for idx, container in enumerate(kontainer):
    total_ukuran = sum(item['barang']['ukuran'] for item in container)
    print(f"\nKontainer {idx+1}:")
    for item in container:
        b = item['barang']
        print(f"  - {b['id']} ({b['ukuran']} kg/m³)")
    print(f"Total Terisi: {total_ukuran}/{kapasitas_kontainer}")
    print(f"Efisiensi: {(total_ukuran / kapasitas_kontainer) * 100:.2f}%")

# ======================
# Final Plot (for report)
# ======================
plt.ioff()
plt.figure(figsize=(10, 5))
plt.plot(iterations, acceptance_probs, 'b-', linewidth=2, label='Acceptance Probability (ΔE < 0)')
plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Probability', fontsize=12)
plt.title('Acceptance Probability over Iterations (ΔE < 0)', fontsize=14, fontweight='bold')
plt.grid(True)
plt.legend()
plt.show()

# ======================
# Smoothed Curve
# ======================
def smooth_series(values, window_frac=0.05, min_window=3):
    vals = np.asarray(values, dtype=float)
    N = vals.size
    if N == 0:
        return vals
    win = max(min_window, int(round(N * window_frac)))
    if win % 2 == 0:
        win += 1
    win = min(win, N if N >= 1 else 1)
    if win <= 1:
        return vals.copy()
    kernel = np.ones(win) / win
    smoothed = np.convolve(vals, kernel, mode='same')
    return smoothed

window_frac = 0.5  # 50% smoothing
smoothed_probs = smooth_series(acceptance_probs, window_frac=window_frac, min_window=3)

plt.figure(figsize=(10,5))
plt.plot(iterations, acceptance_probs, color='lightblue', linewidth=0.8, alpha=0.6, label='Raw Acceptance Probability')
plt.plot(iterations, smoothed_probs, color='blue', linewidth=2.0, label=f'Smoothed (frac={window_frac:.2f})')
plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Probability', fontsize=12)
plt.title('Acceptance Probability over Iterations (ΔE < 0, raw + smoothed)', fontsize=14, fontweight='bold')
plt.ylim(-0.02, 1.02)
plt.grid(alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
