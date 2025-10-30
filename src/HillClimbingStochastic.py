import random
import json
import sys

import os
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
    print("Usage: python3 HillClimbingStochastic.py [json_filename]")
    print("Example: python3 HillClimbingStochastic.py case2.json")
    sys.exit(1)

# Variable Library
kapasitas_kontainer   = data['kapasitas_kontainer']  # kapasitas kontainer
barang                = data['barang'].copy()         # ID Barang 
jumlah_barang         = len(barang)                   # Jumlah Barang 
kontainer             = []                            # Kontainer 
kontainer_id          = 0                             # ID Kontainer 

print(f"Loaded data from JSON file:")
print(f"Kapasitas kontainer: {kapasitas_kontainer} kg/m³")
print(f"Jumlah barang: {jumlah_barang}")
print(f"Barang: {[f"{item['id']}({item['ukuran']})" for item in barang]}")

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

current_iteration = 0
max_iterations    = 10
improvement_found   = True

while improvement_found and current_iteration < max_iterations:
    improvement_found  = False

    possible_swaps = []
    for i in range(len(kontainer)):
        for j in range (i + 1, len(kontainer)):
            for index_i in range(len(kontainer[i])):
                for index_j in range(len(kontainer[j])):
                    possible_swaps.append((i, j, index_i, index_j))
                    
    random.shuffle(possible_swaps) # pemilihan neighbor random
    current_iteration = 0
    
    for current_swap in possible_swaps:
        if current_iteration >= max_iterations: 
            break
        
        i, j, index_i, index_j = current_swap
              
        current_total_i = calculate_kontainer_total(kontainer[i])
        
        if current_total_i < kapasitas_kontainer:
            current_iteration += 1
            print(f"Iteration {current_iteration}")
            
            current_total_j = calculate_kontainer_total(kontainer[j])
            
            barang_i_temp   = kontainer[i][index_i]['barang']
            barang_j_temp   = kontainer[j][index_j]['barang']
                             
            new_total_i     = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
            new_total_j     = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']

            if new_total_i <= kapasitas_kontainer and new_total_j <= kapasitas_kontainer: # Overflow countermeassure
                if (kapasitas_kontainer - new_total_i) < (kapasitas_kontainer - current_total_i): # Change Here untuk Sideways Modifcation, Current Algorithm is Steepest (Neighbor [>]BETTER[>] Current)
                    kontainer[i][index_i]['barang'] = barang_j_temp
                    kontainer[j][index_j]['barang'] = barang_i_temp
                    improvement_found = True
                    print(f"[!!!Swap!!!]: Swapped {barang_i_temp['id']} ↔ {barang_j_temp['id']} (Waste reduced by {new_total_i - current_total_i})")
                    current_iteration = 0
                
                else: # local maxima break
                    continue
                
            else: # overflow break
                continue
            
        else: # full break
            continue

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