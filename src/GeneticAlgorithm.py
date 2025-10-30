import random
import math
import json
import sys
import os
import matplotlib.pyplot as plt
import numpy as np
import time

script_dir = os.path.dirname(os.path.abspath(__file__))

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
    sys.exit(1)

# Variable Library
kapasitas_kontainer   = data['kapasitas_kontainer']  # kapasitas kontainer dalam kg/m³
barang                = data['barang'].copy()         # id barang
jumlah_barang         = len(barang)                   # jumlah barang
kontainer             = []                            # kontainer untuk menyimpan barang
kontainer_id          = 0                             # id kontainer

print(f"Loaded data from JSON file:")
print(f"Kapasitas kontainer: {kapasitas_kontainer} kg/m³")
print(f"Jumlah barang: {jumlah_barang}")
print(f"Barang: {[f"{item['id']}({item['ukuran']})" for item in barang]}")

barang_unrandomized = barang.copy()

# declare kontainer array
kontainer.append([])
kontainer_space_left = kapasitas_kontainer

# declare penyebaran kontainer secara random
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
        barang_i_temp = item['barang']
        print(f"  - ID: {barang_i_temp['id']}, Ukuran: {barang_i_temp['ukuran']} kg/m³")
        total_ukuran += barang_i_temp['ukuran']
    
    sisa_kapasitas = kapasitas_kontainer - total_ukuran
    print(f"  Total Terisi: {total_ukuran}/{kapasitas_kontainer} kg/m³")
    print(f"  Sisa Kapasitas: {sisa_kapasitas} kg/m³")
    print(f"  Efisiensi: {(total_ukuran/kapasitas_kontainer)*100:.2f}%")

print("\n" + "="*60)
print(f"Total Kontainer Digunakan: {len(kontainer)}")
print("="*60)

# variabel untuk GA
main_kromosom           = []  
main_objective_function = 0   # objective function untuk kromosom utama

for item_unrandomized in barang_unrandomized:
    for idx_container, container in enumerate(kontainer):
        for barang_in_container in container:
            if barang_in_container['barang']['id'] == item_unrandomized['id']:
                main_kromosom.append(idx_container + 1)
                break     

print("\n" + "="*60)
print("GENETIC SEQUENCE (KROMOSOM)")
print("="*60)

for i, item_unrandomized in enumerate(barang_unrandomized):
    print(f"{item_unrandomized['id']} (item {i+1}) -> Kontainer {main_kromosom[i]}")

print(f"\nKromosom: {main_kromosom}")
print("="*60)


def calculate_objective_function(kromosom, barang, kapasitas): # objective function untuk fitness test
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
    
    for container in containers: 
        total_size = sum(container)
        
        if total_size > kapasitas: 
            overflow        = total_size - kapasitas
            total_overflow += overflow
            
        if len(container) > 0: 
            fill_ratio               = total_size / kapasitas
            sum_squared_fill_ratios += fill_ratio ** 2
            
    cost = (P_OVERFLOW * total_overflow) + (P_BINS * K) - (P_DENSITY * sum_squared_fill_ratios)
    
    return cost, K, total_overflow, sum_squared_fill_ratios


main_objective_function = calculate_objective_function(main_kromosom, barang_unrandomized, kapasitas_kontainer)

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

def repair_offspring(offspring, barang, kapasitas):
    if not offspring:
        return offspring
    
    K_max = max(offspring) if offspring else 1
    containers = [[] for _ in range(K_max)]
    
    for i, container_num in enumerate(offspring):
        if container_num <= K_max:
            containers[container_num - 1].append((i, barang[i]['ukuran']))
    
    repaired = offspring.copy()
    
    for container_idx, container in enumerate(containers):
        total_size = sum(item[1] for item in container)
        
        if total_size > kapasitas:
            items_sorted = sorted(container, key=lambda x: x[1], reverse=True)
            
            for item_idx, item_size in items_sorted:
                current_total = sum(item[1] for item in container if item[0] != item_idx)
                
                if current_total <= kapasitas:
                    placed = False
                    for target_bin in range(len(containers)):
                        if target_bin != container_idx:
                            target_total = sum(item[1] for item in containers[target_bin])
                            if target_total + item_size <= kapasitas:
                                repaired[item_idx] = target_bin + 1
                                containers[target_bin].append((item_idx, item_size))
                                placed = True
                                break
                    
                    if not placed:
                        K_max += 1
                        repaired[item_idx] = K_max
                        containers.append([(item_idx, item_size)])
                    
                    container = [item for item in container if item[0] != item_idx]
    
    return repaired

# library untuk genetic algorithm
POPULATION_SIZE = 50
MAX_ITERATIONS  = 200
MUTATION_RATE   = 0.05
TOURNAMENT_SIZE = 5

population = []
population.append(main_kromosom.copy())

for _ in range(POPULATION_SIZE - 1):
    random_kromosom = []
    if barang_unrandomized:
        K_max = len(kontainer)
    else:
        K_max = 1
    
    for item in barang_unrandomized:
        random_kromosom.append(random.randint(1, K_max + 2))
    
    population.append(random_kromosom)

def tournament_selection(population, barang, kapasitas, tournament_size):
    tournament = random.sample(population, min(tournament_size, len(population)))
    
    best = tournament[0]
    best_fitness, _, _, _ = calculate_objective_function(best, barang, kapasitas)
    
    for individual in tournament[1:]:
        fitness, _, _, _ = calculate_objective_function(individual, barang, kapasitas)
        if fitness < best_fitness:
            best = individual
            best_fitness = fitness
    
    return best.copy()

best_kromosom = None
best_fitness = float('inf')

iterations  = []
history_POF = []
improvement_count = 0

print("\n" + "="*60)
print("GENETIC ALGORITHM - STARTING")
print("="*60)

start_time = time.time()

for iteration in range(MAX_ITERATIONS):
    fitness_scores = []
    for individual in population:
        fitness, _, _, _ = calculate_objective_function(individual, barang_unrandomized, kapasitas_kontainer)
        fitness_scores.append(fitness)
    
    min_fitness_idx = fitness_scores.index(min(fitness_scores))
    current_best_fitness = fitness_scores[min_fitness_idx]
    
    avg_fitness = sum(fitness_scores) / len(fitness_scores)
    worst_fitness = max(fitness_scores)
    
    if current_best_fitness < best_fitness:
        best_fitness = current_best_fitness
        best_kromosom = population[min_fitness_idx].copy()
        improvement_count += 1
        
        best_cost, best_K, best_overflow, best_density = calculate_objective_function(
            best_kromosom, barang_unrandomized, kapasitas_kontainer
        )
        
        print(f"[IMPROVEMENT #{improvement_count}] Iter {iteration+1}: fitness={best_fitness:.2f}, K={best_K}, overflow={best_overflow}")
    
    iterations.append(iteration + 1)
    history_POF.append(best_fitness)
    
    new_population = []
    
    new_population.append(best_kromosom.copy())
    
    while len(new_population) < POPULATION_SIZE:
        parent1 = tournament_selection(population, barang_unrandomized, kapasitas_kontainer, TOURNAMENT_SIZE)
        parent2 = tournament_selection(population, barang_unrandomized, kapasitas_kontainer, TOURNAMENT_SIZE)
        
        offspring = parent_crossover(parent1, parent2)
        offspring = mutate_offspring(offspring, MUTATION_RATE)
        offspring = repair_offspring(offspring, barang_unrandomized, kapasitas_kontainer)  
        
        new_population.append(offspring)
    
    population = new_population

end_time = time.time()
execution_time = end_time - start_time

print("\n" + "="*60)
print("GENETIC ALGORITHM - COMPLETED")
print(f"Execution Time: {execution_time:.4f} seconds ({execution_time*1000:.2f} ms)")
print(f"Total Improvements: {improvement_count}")
print("="*60)

print("\n" + "="*60)
print("FINAL RESULT")
print("="*60)
print(f"Best Fitness: {best_fitness:.2f}")
print(f"Jumlah iterasi: {MAX_ITERATIONS}")
print(f"Jumlah populasi: {len(population)}")
print(f"Final Kromosom: {best_kromosom}")
print("="*60)

plt.ioff()

# plot 1: objective function over iterations
plt.figure(figsize=(10, 5))
plt.plot(iterations, history_POF, 'b-', linewidth=2, label='Best Fitness')
plt.xlabel('Iteration', fontsize=12)
plt.ylabel('Fitness (Lower is Better)', fontsize=12)
plt.title('Genetic Algorithm - Fitness Evolution', fontsize=14, fontweight='bold')
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()