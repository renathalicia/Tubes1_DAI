import random
import json
import sys
import os
import time
import copy
import matplotlib.pyplot as plt

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
    print("Usage: python3 HillClimbingSteepest.py [json_filename]")
    print("Example: python3 HillClimbingSteepest.py case2.json")
    sys.exit(1)

# variabel global
kapasitas_kontainer   = data['kapasitas_kontainer']  # kapasitas kontainer
barang                = data['barang'].copy()         # id barang 
jumlah_barang         = len(barang)                   # jumlah barang
kontainer             = []                            # kontainer
kontainer_id          = 0                             # id kontainer

print(f"Loaded data from JSON file:")
print(f"Kapasitas kontainer: {kapasitas_kontainer} kg/m³")
print(f"Jumlah barang: {jumlah_barang}")
items_str = [f"{item['id']}({item['ukuran']})" for item in barang]
print(f"Barang: {items_str}")

kontainer.append([])
kontainer_space_left = kapasitas_kontainer

while True:
    if len(barang) == 0:
        break
        
    random_index   = random.randint(0, len(barang) - 1)
    random_barang  = barang[random_index]
    
    if random_barang['ukuran'] <= kontainer_space_left:
        kontainer[kontainer_id].append({
            'barang': random_barang
        })
        
        kontainer_space_left -= random_barang['ukuran']
        barang.pop(random_index)

    else:
        kontainer_id += 1
        kontainer.append([])
        kontainer_space_left = kapasitas_kontainer

print("\n" + "="*60)
print("SPAWN BARANG DALAM KONTAINER (STATE AWAL)")
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

def calculate_waste_squared(kontainer_list, kapasitas):
    """Objective: jumlah kuadrat sisa kapasitas per kontainer (sensitif terhadap redistribusi)."""
    total = 0
    for c in kontainer_list:
        used = calculate_kontainer_total(c)
        unused = kapasitas - used
        total += unused * unused
    return total

initial_state = copy.deepcopy(kontainer)

# inisialisasi variabel
obj_history = [calculate_waste_squared(kontainer, kapasitas_kontainer)]
total_attempts = 0         # jumlah percobaan swap (evaluasi)
total_accepted_swaps = 0   # jumlah swap yang diterima (perbaikan)
start_time = time.time()

initial_objective = obj_history[0]

current_iteration = 0
max_iterations    = 3
best_case_unused  = calculate_unused(kontainer, kapasitas_kontainer)
improvement_found = True

while improvement_found and current_iteration < max_iterations:
    improvement_found  = False

    for i in range(len(kontainer)):
        current_iteration = 0 
        
        for j in range (i + 1, len(kontainer)):
            
            for index_i in range(len(kontainer[i])):
                for index_j in range(len(kontainer[j])):
                    current_total_i = calculate_kontainer_total(kontainer[i]) 
                    
                    if current_total_i < kapasitas_kontainer and current_iteration < max_iterations:
                        current_iteration += 1
                        total_attempts += 1
                        print(f"Iteration {current_iteration}")
                        
                        current_total_j = calculate_kontainer_total(kontainer[j])
                        
                        barang_i_temp   = kontainer[i][index_i]['barang']
                        barang_j_temp   = kontainer[j][index_j]['barang']
                                        
                        new_total_i     = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
                        new_total_j     = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']
                                            
                        if new_total_i <= kapasitas_kontainer and new_total_j <= kapasitas_kontainer:
                            # hitung objective sebelum dan setelah swap, terima hanya jika after < before
                            before_obj = calculate_waste_squared(kontainer, kapasitas_kontainer)

                            # lakukan swap sementara
                            kontainer[i][index_i]['barang'] = barang_j_temp
                            kontainer[j][index_j]['barang'] = barang_i_temp

                            after_obj = calculate_waste_squared(kontainer, kapasitas_kontainer)

                            if after_obj < before_obj:
                                # terima swap secara permanen 
                                improvement_found = True
                                total_accepted_swaps += 1
                                obj_history.append(after_obj)
                                print(f"[!!!Swap Accepted!!!]: Swapped {barang_i_temp['id']} ↔ {barang_j_temp['id']} (Obj {before_obj} → {after_obj})")
                                current_iteration = 0
                            else:
                                # revert swap karena objektif global tidak membaik
                                kontainer[i][index_i]['barang'] = barang_i_temp
                                kontainer[j][index_j]['barang'] = barang_j_temp
                        else:
                            break
                    else:
                        break

#hitung waktu
end_time = time.time()
duration_seconds = end_time - start_time

final_state = copy.deepcopy(kontainer)
final_objective = obj_history[-1] if len(obj_history) > 0 else calculate_waste_squared(final_state, kapasitas_kontainer)
iterations_until_stop = total_attempts  # jumlah percobaan evaluasi dilakukan
swaps_accepted = total_accepted_swaps

print("\n" + "="*60)
print("HASIL PENYIMPANAN BARANG DALAM KONTAINER (STATE AKHIR)")
print("="*60)

for idx, container in enumerate(final_state):
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
print(f"Total Kontainer Digunakan: {len(final_state)}")
print("="*60)

# summary
print(f"Durasi proses pencarian: {duration_seconds:.4f} detik")
print(f"Jumlah percobaan swap (evaluasi): {iterations_until_stop}")
print(f"Jumlah swap diterima (perbaikan): {swaps_accepted}")
print(f"Nilai objective awal (sum unused^2): {initial_objective}")
print(f"Nilai objective akhir (sum unused^2): {final_objective}")
print(f"Jumlah langkah perbaikan yang tercatat (history length - 1): {len(obj_history)-1}")

# plot obj value terhadap langkah swap/perbaikan
plt.figure(figsize=(8,4))
steps = list(range(len(obj_history)))
plt.plot(steps, obj_history, marker='o')
plt.title("Objective (sum of squared unused capacity) per improvement step")
plt.xlabel("Improvement step (0 = awal)")
plt.ylabel("Objective = sum(unused^2)")
plt.grid(True)

plt.tight_layout()
plt.show()
plt.close()

# visual obj func
def plot_state(kontainer_state, kapas, title):
    fig = plt.figure(figsize=(10,5))
    ax = fig.add_subplot(1,1,1)

    x_positions = range(len(kontainer_state))
    bar_width = 0.6

    for idx, container in enumerate(kontainer_state):
        bottoms = 0
        for seg in container:
            size = seg['barang']['ukuran']
            ax.bar(idx, size, bottom=bottoms, width=bar_width)
            if size >= max(3, kapas * 0.05):
                ax.text(idx, bottoms + size/2, f"{seg['barang']['id']} ({size})", ha='center', va='center', fontsize=8)
            bottoms += size

        ax.hlines(kapas, idx - bar_width/2 - 0.2, idx + bar_width/2 + 0.2, linestyles='dashed', linewidth=0.8)

        used = calculate_kontainer_total(container)
        if used < kapas:
            ax.bar(idx, kapas - used, bottom=used, width=bar_width, alpha=0.05)

        ax.text(idx, -kapas*0.05, f"{used}/{kapas}", ha='center', va='top', fontsize=9)

    ax.set_xticks(list(x_positions))
    ax.set_xticklabels([f"K{idx+1}" for idx in x_positions])
    ax.set_ylim(-kapas*0.15, kapas*1.05)
    ax.set_ylabel("Ukuran (kg/m³)")
    ax.set_title(title)
    ax.grid(axis='y', linestyle=':', linewidth=0.6)
    plt.tight_layout()
    plt.show()
    plt.close()

plot_state(initial_state, kapasitas_kontainer, "State Awal: Penyebaran Barang per Kontainer (Random Spawn)")
plot_state(final_state, kapasitas_kontainer, "State Akhir: Setelah Hill-Climbing (Final)")
