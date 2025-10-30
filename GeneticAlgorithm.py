# Import library that's needed
import random
import math
import json
import sys

# Load data from JSON file
import os
script_dir = os.path.dirname(os.path.abspath(__file__))

# Check JSON File
if len(sys.argv) > 1:
    json_filename = sys.argv[1]
else:
    json_filename = 'case1.json'  # Default 

json_path = os.path.join(script_dir, json_filename)

try:
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"Using JSON file: {json_filename}")
except FileNotFoundError:
    print(f"Error: {json_filename} not found!")
    print("Usage: python3 GeneticAlgorithm.py [json_filename]")
    print("Example: python3 GeneticAlgorithm.py case2.json")
    sys.exit(1)

# Variable Library
kapasitas_kontainer   = data['kapasitas_kontainer']  # Kapasitas Kontainer di current problem -- Seluruh Kontainer memiliki kapasitas yang sama.
barang                = data['barang'].copy()         # ID Barang -- Kode unik setiap barang  AND  Ukuran --- Ukuran/Berat barang tersebut.  
jumlah_barang         = len(barang)                   # Jumlah Barang di current problem.
kontainer             = []                            # Kontainer untuk menyimpan barang yang ada.
kontainer_id          = 0                             # ID Kontainer untuk keeptrack array.

# Min & Max varibel untuk menentukan ΔEₘₐₓ sebagai T₀ sesuai approach oleh Kirkpatirc et al.
min_ukuran = min(item['ukuran'] for item in barang)
max_ukuran = max(item['ukuran'] for item in barang)

print(f"Loaded data from JSON file:")
print(f"Kapasitas kontainer: {kapasitas_kontainer} kg/m³")
print(f"Jumlah barang: {jumlah_barang}")
print(f"Barang: {[f"{item['id']}({item['ukuran']})" for item in barang]}")

barang_unrandomized = barang.copy()

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

# Variable Library for Genetic Algorithm
main_kromosom           = []  # Array untuk sequence genetic yang utama (Keep Track)
main_objective_function = 0   # Objective function dari sequence utama  (Keep Track)

for item_unrandomized in barang_unrandomized:
    for idx_container, container in enumerate(kontainer):
        for barang_in_container in container:
            if barang_in_container['barang']['id'] == item_unrandomized['id']:
                main_kromosom.append(idx_container + 1)
                break     

# Print genetic sequence
print("\n" + "="*60)
print("GENETIC SEQUENCE (KROMOSOM)")
print("="*60)

for i, item_unrandomized in enumerate(barang_unrandomized):
    print(f"{item_unrandomized['id']} (item {i+1}) -> Kontainer {main_kromosom[i]}")

print(f"\nKromosom: {main_kromosom}")
print("="*60)


def calculate_objective_function(kromosom, barang, kapasitas): # Objective function untuk fitness test
    # Penalty Definitions
    P_OVERFLOW = 1000
    P_BINS     = 1.0
    P_DENSITY  = 0.1
    
    if kromosom:
        K = max(kromosom)
    else:
        K = 0
        
    containers = [[] for _ in range (K)]
    
    for i, container_num in enumerate(kromosom):
        containers[container_num - 1].append(barang[i]['ukuran'])
        
    total_overflow          = 0
    sum_squared_fill_ratios = 0
    
    for container in containers: # Check every container yang ada!
        total_size = sum(container)
        
        if total_size > kapasitas: # Overflow penalty!
            overflow        = total_size - kapasitas
            total_overflow += overflow
            
        if len(container) > 0: # Persentase filled kontainer
            fill_ratio               = total_size / kapasitas
            sum_squared_fill_ratios += fill_ratio ** 2
            
    cost = (P_OVERFLOW * total_overflow) + (P_BINS * K) - (P_DENSITY * sum_squared_fill_ratios)
    
    return cost, K, total_overflow, sum_squared_fill_ratios


main_objective_function = calculate_objective_function(main_kromosom, barang_unrandomized, kapasitas_kontainer)


def generate_candidate_partner(main_kromosom): # Membuat sequence dari candidate partner yang didapatkan dengan memanipulasi main kromosom.
    if not main_kromosom:
        return []
    
    if main_kromosom:
        K_max     = max(main_kromosom)
    else:
        K_max     = 1
        
    partner       = main_kromosom.copy()
    mutation_type = random.choice(['swap', 'move', 'shuffle'])
    
    if mutation_type == 'swap':
        if len(partner) >= 2:
            idx_1, idx_2 = random.sample(range(len(partner)), 2)
            partner[idx_1], partner[idx_2] = partner[idx_2], partner[idx_1]
            
            
    elif mutation_type == 'move':
        idx           = random.randint(0, len(partner) - 1)
        new_container = random.randint(1, K_max + 1)
        partner[idx]  = new_container
        
        
    elif mutation_type == 'shuffle':
        if len(partner) >= 2:
            start   = random.randint(0, len(partner) - 2)
            end     = random.randint(start + 1, len(partner))
            segment = partner[start:end]
            
            random.shuffle(segment)
            partner[start:end] = segment
    
    return partner

def parent_crossover(parent_a, parent_b):
    if len(parent_a) != len(parent_b):
        raise ValueError("Parents must have the same length for crossover.")
    n = len(parent_a)
    if n < 2:
        return parent_a.copy()
    
    point = random.randint(1, n - 1)
    child = parent_a[:point] + parent_b[point:]
    return child

def mutate_offspring(offspring, mutation_rate):
    if not offspring:
        return offspring
    
    mutated = offspring.copy()
    if mutated:
        K_max = max(mutated)
    else:
        K_max = 1
    
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[i] = random.randint(1, K_max + 1)
    
    return mutated

MAX_ITERATIONS = 10
MUTATION_RATE  = 0.1

best_POF, _, _, _ = main_objective_function

for i in range (MAX_ITERATIONS):
    candidate_partner = [] # Array of Candidate Partners
    candidate_POF     = [] # Array of Objective Function each Candidate Partners
    
    for _ in range (3):
        partner         = generate_candidate_partner(main_kromosom)
        if not partner:
            continue
        POF, _, _, _    = calculate_objective_function(partner, barang_unrandomized, kapasitas_kontainer)
        candidate_partner.append(partner)     
        candidate_POF.append(POF)
    
    if not candidate_partner:
        print("No candidates generated! Stopping Algorithm!")
        break
    
    candidate_idx = int(min(range(len(candidate_POF)), key=lambda x: candidate_POF[x]))
    
    choosen_partner = candidate_partner[candidate_idx]
    
    offspring       = parent_crossover(main_kromosom, choosen_partner)
    offspring       = mutate_offspring(offspring, MUTATION_RATE)
    
    offspring_POF, offspring_K, offspring_overflow, offspring_density = calculate_objective_function(offspring, barang_unrandomized, kapasitas_kontainer)
    
    main_kromosom_POF, _, _, _ = main_objective_function
    
    print(f"Iter {i+1}: parent_cost={main_kromosom_POF:.2f}, candidate_cost={candidate_POF[candidate_idx]:.2f}, offspring_cost={offspring_POF:.2f}, K={offspring_K}, overflow={offspring_overflow}")
    
    if offspring_POF < main_kromosom_POF:
        main_kromosom           = offspring
        main_objective_function = (offspring_POF, offspring_K, offspring_overflow, offspring_density)
        best_POF                = offspring_POF
        
        
print("\n" + "="*60)
print("FINAL RESULT")
print("="*60)
print(f"Best Cost: {best_POF:.2f}")
print(f"Final Kromosom: {main_kromosom}")
print("="*60)

# Reconstruct containers from final kromosom
final_K = max(main_kromosom) if main_kromosom else 0
final_containers = [[] for _ in range(final_K)]

for i, container_num in enumerate(main_kromosom):
    final_containers[container_num - 1].append({
        'barang': barang_unrandomized[i]
    })

# Print final container arrangement
print("\n" + "="*60)
print("FINAL CONTAINER ARRANGEMENT (AFTER GENETIC ALGORITHM)")
print("="*60)

for idx, container in enumerate(final_containers):
    print(f"\nKontainer {idx + 1}:")
    total_ukuran = 0
    
    for item in container:
        barang_info = item['barang']
        print(f"  - ID: {barang_info['id']}, Ukuran: {barang_info['ukuran']} kg/m³")
        total_ukuran += barang_info['ukuran']
    
    sisa_kapasitas = kapasitas_kontainer - total_ukuran
    overflow = max(0, total_ukuran - kapasitas_kontainer)
    
    print(f"  Total Terisi: {total_ukuran}/{kapasitas_kontainer} kg/m³")
    print(f"  Sisa Kapasitas: {sisa_kapasitas} kg/m³")
    
    if overflow > 0:
        print(f"  ⚠️ OVERFLOW: {overflow} kg/m³")
    
    print(f"  Efisiensi: {(total_ukuran/kapasitas_kontainer)*100:.2f}%")

print("\n" + "="*60)
print(f"Total Kontainer Digunakan: {len(final_containers)}")
final_cost, final_K_check, final_overflow, final_density = main_objective_function
print(f"Final Cost: {final_cost:.2f}")
print(f"Total Overflow: {final_overflow}")
print(f"Density Score: {final_density:.4f}")
print("="*60)