# Import library that's needed
import random
import math
import json
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import time

# Load data from JSON file
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

# Check JSON File
if len(sys.argv) > 1:
    json_filename = sys.argv[1]
else:
    json_filename = 'case6.json'  

json_path = os.path.join(script_dir, json_filename)

try:
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"Using JSON file: {json_filename}")
except FileNotFoundError:
    print(f"Error: {json_filename} not found!")
    print("Usage: python3 SimulatedAnnealing.py [json_filename]")
    print("Example: python3 SimulatedAnnealing.py case2.json")
    sys.exit(1)

# Variable Library
kapasitas_kontainer   = data['kapasitas_kontainer']   # Kapasitas Kontainer di current problem -- Seluruh Kontainer memiliki kapasitas yang sama.
barang                = data['barang'].copy()         # ID Barang -- Kode unik setiap barang  AND  Ukuran --- Ukuran/Berat barang tersebut.  
jumlah_barang         = len(barang)                   # Jumlah Barang di current problem.
kontainer             = []                            # Kontainer untuk menyimpan barang yang ada.
kontainer_id          = 0                             # ID Kontainer untuk keeptrack array.

print(f"Loaded data from JSON file:")
print(f"Kapasitas kontainer: {kapasitas_kontainer} kg/m³")
print(f"Jumlah barang: {jumlah_barang}")
print(f"Barang: {[f"{item['id']}({item['ukuran']})" for item in barang]}")

# Deklarasi Array Kontainer 
kontainer.append([])
kontainer_space_left = kapasitas_kontainer


# Deklarasi Penyebaran Kontainer secara Random
while True:
    if len(barang) == 0:
        break
        
    # 1. Pemilihan first arbitrary variabel dari current_container
    random_index   = random.randint(0, len(barang) - 1)
    random_barang  = barang[random_index]
    
    # 2. IF barang dapat dimasukan (Tidak Overflow)
    if random_barang['ukuran'] <= kontainer_space_left:
        kontainer[kontainer_id].append({
            'barang': random_barang
        })
        
        kontainer_space_left -= random_barang['ukuran']
        barang.pop(random_index)

    # 3. IF overflow, akan membuka kontainer baru
    else:
        kontainer_id += 1
        kontainer.append([])
        kontainer_space_left = kapasitas_kontainer

# Format print kontainer hasil algoritma Hill-Climbing
print("\n" + "="*60)
print("SPAWN BARANG DALAM KONTAINER")
print("="*60)

for idx, container in enumerate(kontainer):
    print(f"\nKontainer {idx + 1}:")
    total_ukuran = 0
    
    for item in container:
        barang_i_tempnfo = item['barang']
        print(f"  - ID: {barang_i_tempnfo['id']}, Ukuran: {barang_i_tempnfo['ukuran']} kg/m³")
        total_ukuran += barang_i_tempnfo['ukuran']
    
    sisa_kapasitas = kapasitas_kontainer - total_ukuran
    print(f"  Total Terisi: {total_ukuran}/{kapasitas_kontainer} kg/m³")
    print(f"  Sisa Kapasitas: {sisa_kapasitas} kg/m³")
    print(f"  Efisiensi: {(total_ukuran/kapasitas_kontainer)*100:.2f}%")

print("\n" + "="*60)
print(f"Total Kontainer Digunakan: {len(kontainer)}")
print("="*60)

# Helper function untuk Hill Climbing Algorithm
def calculate_kontainer_total(kontainer):
    total = 0
    for arr_barang in kontainer:
        total += arr_barang['barang']['ukuran']
    return total

def calculate_unused(kontainer, kapasitas):
    total_unused = 0
    for container in kontainer:
        used          = calculate_kontainer_total(container)
        unused        = kapasitas - used
        total_unused += unused
    return total_unused

def calculate_objective_function(kontainer, kapasitas):
    # Penalty Definitions
    P_OVERFLOW = 1000
    P_BINS     = 1.0
    P_DENSITY  = 0.1
    
    K = len(kontainer)  # Number of containers
    
    total_overflow          = 0
    sum_squared_fill_ratios = 0
    
    for container in kontainer:
        total_size = calculate_kontainer_total(container)
        
        if total_size > kapasitas:  # Overflow penalty
            overflow        = total_size - kapasitas
            total_overflow += overflow
        
        if len(container) > 0:  # Fill ratio
            fill_ratio               = total_size / kapasitas
            sum_squared_fill_ratios += fill_ratio ** 2
    
    cost = (P_OVERFLOW * total_overflow) + (P_BINS * K) - (P_DENSITY * sum_squared_fill_ratios)
    
    return cost, K, total_overflow, sum_squared_fill_ratios

def calculate_initial_temperature(kontainer, kapasitas):
    # ΔEₘₐₓ sebagai T₀ sesuai approach oleh Kirkpatirc et al.

    max_delta_E = 0
    
    # Mencari perbedaan dengan adjacent containers (i and i+1)
    for i in range(len(kontainer) - 1):
        j = i + 1 
        
        for index_i in range(len(kontainer[i])):
            for index_j in range(len(kontainer[j])):
                current_total_i = calculate_kontainer_total(kontainer[i])
                current_total_j = calculate_kontainer_total(kontainer[j])
                
                barang_i_temp = kontainer[i][index_i]['barang']
                barang_j_temp = kontainer[j][index_j]['barang']
                
                new_total_i = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
                new_total_j = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']
                
                current_unused_i = kapasitas - current_total_i
                new_unused_i = kapasitas - new_total_i
                
                delta_E = abs(new_unused_i - current_unused_i)
                
                if delta_E > max_delta_E:
                    max_delta_E = delta_E
    
    return max_delta_E

# Variable for diagram needs
acceptance_probability  = []
iterations              = []
history_POF             = []

# ==> Simulated Annealing Search Algorithm Starting Here <==
start_time        = time.time()
temperature       = calculate_initial_temperature(kontainer, kapasitas_kontainer)
alpha             = 0.985
min_temperature   = 0.01
max_iterations    = 1000
current_iteration = 0

# Variable for local optimum flag
local_stucked       = 0
sideways_counter    = 0
SIDEWAYS_THRESHOLD  = 5
last_changed_POF    = float('-inf')

print(f"\nInitial Temperature (T₀): {temperature:.2f}")
print(f"Alpha (cooling rate): {alpha}")
print(f"Min Temperature: {min_temperature}")
print(f"Max Iterations: {max_iterations}")
print("="*60)

# This Simulated Annealing uses a geometric cooling approach
# ---------------------------- Tₖ₊₁ = α * Tₖ ----------------------------

while temperature > min_temperature and current_iteration < max_iterations:
    # Objective Function Data Logging
    current_POF, _, _, _ = calculate_objective_function(kontainer, kapasitas_kontainer)
    history_POF.append(current_POF)
    
    if last_changed_POF != current_POF:
        last_changed_POF = current_POF
        sideways_counter = 0
    
    else:
        sideways_counter += 1
        
    if sideways_counter >= SIDEWAYS_THRESHOLD:
        local_stucked += 1
        sideways_counter = 0
    
    # karena Simulated Annealing menggunakan Stochastic Hill Climbing, maka perlu ditentukan terlebih dahulu
    possible_swaps = []
    for i in range(len(kontainer)):
        for j in range(i + 1, len(kontainer)):
            for index_i in range(len(kontainer[i])):
                for index_j in range(len(kontainer[j])):
                    possible_swaps.append((i, j, index_i, index_j))
    
    if not possible_swaps: # Break IF there is no swap possible
        print("No possible swaps available. Stopping.")
        break
    
    # Pick one random swap of possible swaps
    i, j, index_i, index_j = random.choice(possible_swaps)
    
    current_total_i = calculate_kontainer_total(kontainer[i])
    current_total_j = calculate_kontainer_total(kontainer[j])
    
    # Barang variable (current)
    barang_i_temp = kontainer[i][index_i]['barang']
    barang_j_temp = kontainer[j][index_j]['barang']
    
    # New total variable IF swaps happens
    new_total_i = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
    new_total_j = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']
    
    # Overflow validation 
    if new_total_i <= kapasitas_kontainer and new_total_j <= kapasitas_kontainer:
        # ΔE calculation --> Current.Value - Neighbor.Value
        current_unused = (kapasitas_kontainer - current_total_i)
        new_unused = (kapasitas_kontainer - new_total_i)
        
        delta_E = new_unused - current_unused
        
        if delta_E >= 0: # ΔE > 0, THEN Accept
            accept = True
            probability = 1.0 # Actually, P will always be >= 1, but to reduce calculations we can consider it to be 1.
            
        else:
            # If ΔE < 0, then calculate P = e^(ΔE/T)
            probability = math.exp(delta_E / temperature)  
            accept      = random.random() < probability
        
        iterations.append(current_iteration)
        acceptance_probability.append(probability)
        
        if accept:
            kontainer[i][index_i]['barang'] = barang_j_temp
            kontainer[j][index_j]['barang'] = barang_i_temp
            
            if delta_E >= 0:
                print(f"Iter {current_iteration+1}: [ACCEPT] {barang_i_temp['id']} ↔ {barang_j_temp['id']} | ΔE={delta_E:.2f} | T={temperature:.2f}")
            else:
                print(f"Iter {current_iteration+1}: [PROB-ACCEPT] {barang_i_temp['id']} ↔ {barang_j_temp['id']} | ΔE={delta_E:.2f} | P={probability:.4f} | T={temperature:.2f}")
        else:
            print(f"Iter {current_iteration+1}: [REJECT] {barang_i_temp['id']} ↔ {barang_j_temp['id']} | ΔE={delta_E:.2f} | P={probability:.4f} | T={temperature:.2f}")
    
    temperature         *= alpha
    current_iteration   += 1

end_time        = time.time()
execution_time  = end_time - start_time

# Format print kontainer hasil algoritma Hill-Climbing
print("\n" + "="*60)
print("HASIL PENYIMPANAN BARANG DALAM KONTAINER")
print("="*60)

for idx, container in enumerate(kontainer):
    print(f"\nKontainer {idx + 1}:")
    total_ukuran = 0
    
    for item in container:
        barang_i_tempnfo = item['barang']
        print(f"  - ID: {barang_i_tempnfo['id']}, Ukuran: {barang_i_tempnfo['ukuran']} kg/m³")
        total_ukuran += barang_i_tempnfo['ukuran']
    
    sisa_kapasitas = kapasitas_kontainer - total_ukuran
    print(f"  Total Terisi: {total_ukuran}/{kapasitas_kontainer} kg/m³")
    print(f"  Sisa Kapasitas: {sisa_kapasitas} kg/m³")
    print(f"  Efisiensi: {(total_ukuran/kapasitas_kontainer)*100:.2f}%")

print("\n" + "="*60)
print(f"Total Kontainer Digunakan: {len(kontainer)}")
print("="*60)

print(f"\nSimulated Annealing completed after {current_iteration} iterations.")
print(f"Final Temperature: {temperature:.2f}")
print(f"Execution Time: {execution_time:.4f} seconds")

print(f"Current case of Simulated Annealing made {local_stucked} times")

# ==> Final plot of Diagram <==

# Plot 1: Scatter Plot of Probability over Iterations
plt.ioff()

plt.figure(figsize=(10, 5))
plt.scatter(iterations, acceptance_probability, c='lightblue', s=20, alpha=0.6, label='Acceptance Probability')

if len(iterations) > 1:
    z = np.polyfit(iterations, acceptance_probability, 3)  # 3rd degree polynomial
    p = np.poly1d(z)
    plt.plot(iterations, p(iterations), 'b-', linewidth=2, label='Trend Line')

plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Probability', fontsize=12)
plt.title('Acceptance Probability over Iterations (ΔE < 0)', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()
plt.ylim(-0.02, 1.02)
plt.tight_layout()
plt.show()


# Plot 2: 
plt.figure(figsize=(10, 5))
plt.plot(range(len(history_POF)), history_POF, 'r-', linewidth=2, label='Objective Function Value')
plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Objective Function Value', fontsize=12)
plt.title('Objective Function (POF) over Iterations', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()