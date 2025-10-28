# Import library that's needed
import random
import math

# Variable Library
kapasitas_kontainer   = 0   # Kapasitas Kontainer di current problem -- Seluruh Kontainer memiliki kapasitas yang sama.
jumlah_barang         = 0   # Jumlah Barang di current problem.
barang                = []  # ID Barang -- Kode unik setiap barang  AND  Ukuran --- Ukuran/Berat barang tersebut.  
kontainer             = []  # Kontainer untuk menyimpan barang yang ada.
kontainer_id          = 0   # ID Kontainer untuk keeptrack array.

# Menerima input untuk variabel kapasitas_kontainer
kapasitas_kontainer = int(input("kapasitas_kontainer: "))

# Menerima input untuk variabel total jumlah barang (declare jumlah array)
jumlah_barang       = int(input("jumlah barang yang disimpan: "))

# Min & Max varibel untuk menentukan ΔEₘₐₓ sebagai T₀ sesuai approach oleh Kirkpatirc et al.
min_ukuran          = float('-inf')
max_ukuran          = float('-inf')

# Menerima input untuk array barang
for i in range(jumlah_barang):
    print(f"\n Barang ke-{i+1}: ")
    
    # Loop validation for unique id_barang
    while True:
        id_barang = input("  id barang(e.g. BRG011): ")
        
        id_barang_sudah_ada = False
        for item in barang:  # Mengecek tiap item di barang apakah ID ada yang duplicate O(n)
            if item['id'] == id_barang:
                id_barang_sudah_ada = True
                break
            
        if id_barang_sudah_ada:
            print(f"  barang dengan id {id_barang} sudah ada pada list barang!")
            
        else:
            break
            
    ukuran_barang = int(input("  ukuran barang(kg/m³): "))
    
    if i == 0:
        min_ukuran = ukuran_barang
        max_ukuran = ukuran_barang
    
    else:
        if ukuran_barang < min_ukuran:
            min_ukuran = ukuran_barang
        
        if ukuran_barang > max_ukuran:
            max_ukuran = ukuran_barang
    
    barang.append({
        'id': id_barang,
        'ukuran': ukuran_barang
    })

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


main_objective_function = calculate_objective_function(main_kromosom, barang, kapasitas_kontainer)


def generate_candidate_partner(main_kromosom): # Membuat sequence dari candidate partner yang didapatkan dengan memanipulasi main kromosom.
    K_max         = max(main_kromosom)
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
    K_max = max(mutated)
    
    for i in range(len(mutated)):
        if random.random() < mutation_rate:
            mutated[i] = random.randint(1, K_max + 1)
    
    return mutated

MAX_ITERATIONS = 10
MUTATION_RATE  = 0.1

for i in range (MAX_ITERATIONS):
    candidate_partner = [] # Array of Candidate Partners
    candidate_POF     = [] # Array of Objective Function each Candidate Partners
    
    for _ in range (3):
        partner = generate_candidate_partner(main_kromosom)
        POF, _, _, _         = calculate_objective_function(partner, barang, kapasitas_kontainer)
        candidate_partner.append(partner)     
        candidate_POF.append(POF)
    
    candidate_idx = int(min(range(len(candidate_POF)), key=lambda x: candidate_POF[x]))
    
    choosen_partner = candidate_partner[candidate_idx]
    offspring       = parent_crossover(main_kromosom, choosen_partner)
    
    offspring       = mutate_offspring(offspring, MUTATION_RATE)
    
    offspring_POF, offspring_K, offspring_overflow, offspring_density = calculate_objective_function(offspring, barang, kapasitas_kontainer)
    
    main_kromosom_POF, _, _, _ = main_objective_function
    
    if offspring_POF < main_kromosom_POF:
        main_kromosom = offspring
        main_objective_function = (offspring_POF, offspring_K, offspring_overflow, offspring_density)
    
    
            
        
    
    
    
        
    
    
    
    
    
    