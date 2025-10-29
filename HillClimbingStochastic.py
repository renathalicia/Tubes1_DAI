# Import library that's needed
import random
import json

# Load data from JSON file
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'test_case.json')
with open(json_path, 'r') as f:
    data = json.load(f)

# Variable Library
kapasitas_kontainer   = data['kapasitas_kontainer']  # Kapasitas Kontainer di current problem -- Seluruh Kontainer memiliki kapasitas yang sama.
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


# ==> Hill Climbing Search Algorithm Starting Here <==
current_iteration = 0
max_iterations    = 4
improvement_found   = True

# THIS CAN BE REMOVED(?), MAKE SURE FIRST!
while improvement_found and current_iteration < max_iterations:
    improvement_found  = False
# THIS CAN BE REMOVED(?), MAKE SURE FIRST!

    possible_swaps = []
    for i in range(len(kontainer)):
        for j in range (i + 1, len(kontainer)):
            for index_i in range(len(kontainer[i])):
                for index_j in range(len(kontainer[j])):
                    possible_swaps.append((i, j, index_i, index_j))
                    
    random.shuffle(possible_swaps) # Untuk pemilihan neighbor random
    current_iteration = 0
    
    for current_swap in possible_swaps:
        if current_iteration >= max_iterations: # Max Iterations break
            break
        
        i, j, index_i, index_j = current_swap
              
        current_total_i = calculate_kontainer_total(kontainer[i]) # Hanya berfokus pada peningkatan value dari barang I.
        
        if current_total_i < kapasitas_kontainer: # IF sudah 100% capacity, THEN continue to new variable.
            current_iteration += 1
            print(f"Iteration {current_iteration}")
            
            current_total_j = calculate_kontainer_total(kontainer[j])
            
            # Barang variable (current & new)
            barang_i_temp   = kontainer[i][index_i]['barang']
            barang_j_temp   = kontainer[j][index_j]['barang']
            
            # New total variable IF swaps happens                 
            new_total_i     = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
            new_total_j     = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']
                                
            if new_total_i <= kapasitas_kontainer and new_total_j <= kapasitas_kontainer: # Overflow countermeassure
                                        
                if (kapasitas_kontainer - new_total_i) < (kapasitas_kontainer - current_total_i): # Change Here untuk Sideways Modifcation, Current Algorithm is Steepest (Neighbor [>]BETTER[>] Current)
                    kontainer[i][index_i]['barang'] = barang_j_temp
                    kontainer[j][index_j]['barang'] = barang_i_temp
                    improvement_found = True
                    print(f"[!!!Swap!!!]: Swapped {barang_i_temp['id']} ↔ {barang_j_temp['id']} (Waste reduced by {new_total_i - current_total_i})")
                    current_iteration = 0
                
                else: # Local Maxima break
                    break
                
            else: # Overflow break
                break
            
        else: # 100% Capacity break
            break

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