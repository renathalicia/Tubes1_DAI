# ==========================================
# Visualisasi Hill Climbing Stochastic
# ==========================================

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import json
import random
import sys
import os
import time

class HillClimbingStochasticVisualizer:
    def __init__(self, json_filename='case1.json'):
        self.json_filename = json_filename
        self.snapshots = []
        self.objective_values = []
        self.iteration_count = 0
        
        self.load_data()
        self.run_hill_climbing_stochastic()
        
    def load_data(self):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, self.json_filename)
        
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            self.kapasitas = data['kapasitas_kontainer']
            self.barang = data['barang'].copy()
            
            print(f"Loaded: {self.json_filename}")
            print(f"Path: {json_path}")
            print(f"Kapasitas kontainer: {self.kapasitas}")
            print(f"Jumlah barang: {len(self.barang)}")
            
        except FileNotFoundError:
            print(f"Error: File {self.json_filename} tidak ditemukan!")
            print(f"Looking for: {json_path}")
            print(f"Script directory: {script_dir}")
            sys.exit(1)
    
    def create_initial_solution(self):
        kontainer = []
        kontainer_id = 0
        barang_copy = self.barang.copy()
        
        kontainer.append([])
        sisa_kapasitas = self.kapasitas
        
        while barang_copy:
            random_index = random.randint(0, len(barang_copy) - 1)
            barang_terpilih = barang_copy[random_index]
            
            if barang_terpilih['ukuran'] <= sisa_kapasitas:
                kontainer[kontainer_id].append(barang_terpilih)
                sisa_kapasitas -= barang_terpilih['ukuran']
                barang_copy.pop(random_index)
            else:
                # Buat kontainer baru
                kontainer_id += 1
                kontainer.append([])
                sisa_kapasitas = self.kapasitas
        
        return kontainer
    
    def calculate_objective(self, kontainer):
        if not kontainer:
            return float('inf')
        
        efficiencies = []
        total_waste = 0
        
        for container in kontainer:
            used = sum(item['ukuran'] for item in container)
            waste = self.kapasitas - used
            total_waste += waste
            
            efficiency = used / self.kapasitas
            efficiencies.append(efficiency)
        
        if len(efficiencies) > 1:
            mean_eff = sum(efficiencies) / len(efficiencies)
            variance = sum((e - mean_eff) ** 2 for e in efficiencies) / len(efficiencies)
        else:
            variance = 0
        
        objective = total_waste + (variance * 500) + (len(kontainer) * 10)
        
        return objective
    
    def get_neighbors(self, kontainer):
        neighbors = []
        
        for i in range(len(kontainer)):
            for j in range(i + 1, len(kontainer)):
                for idx_i in range(len(kontainer[i])):
                    for idx_j in range(len(kontainer[j])):
                        neighbor = [container.copy() for container in kontainer]
                        
                        item_i = neighbor[i][idx_i]
                        item_j = neighbor[j][idx_j]
                        
                        used_i = sum(item['ukuran'] for item in neighbor[i])
                        used_j = sum(item['ukuran'] for item in neighbor[j])
                        
                        new_used_i = used_i - item_i['ukuran'] + item_j['ukuran']
                        new_used_j = used_j - item_j['ukuran'] + item_i['ukuran']
                        
                        if new_used_i <= self.kapasitas and new_used_j <= self.kapasitas:
                            neighbor[i][idx_i] = item_j
                            neighbor[j][idx_j] = item_i
                            neighbors.append(neighbor)
        
        return neighbors
    
    def save_snapshot(self, kontainer, iteration, objective):
        snapshot = {
            'iteration': iteration,
            'kontainer': [container.copy() for container in kontainer],
            'objective': objective
        }
        self.snapshots.append(snapshot)
        self.objective_values.append(objective)
    
    def calculate_kontainer_total(self, kontainer):
        total = 0
        for item in kontainer:
            total += item['ukuran']
        return total
    
    def calculate_unused(self, kontainer, kapasitas):
        total_unused = 0
        for container in kontainer:
            used = self.calculate_kontainer_total(container)
            unused = kapasitas - used
            total_unused += unused
        return total_unused
    
    def run_hill_climbing_stochastic(self):
        print("\n" + "="*50)
        print("HILL CLIMBING STOCHASTIC")
        print("="*50)
        
        current_solution = self.create_initial_solution()
        
        initial_waste = self.calculate_unused(current_solution, self.kapasitas)
        self.save_snapshot(current_solution, 0, initial_waste)
        
        print(f"Solusi awal - Total waste: {initial_waste}")
        print(f"Jumlah kontainer: {len(current_solution)}")
        
        # Variables untuk algoritma
        current_iteration = 0
        max_iterations = 1000
        improvement_found = True
        total_improvements = 0
        
        while improvement_found and current_iteration < max_iterations:
            improvement_found = False
            
            # Generate semua possible swaps
            possible_swaps = []
            for i in range(len(current_solution)):
                for j in range(i + 1, len(current_solution)):
                    for index_i in range(len(current_solution[i])):
                        for index_j in range(len(current_solution[j])):
                            possible_swaps.append((i, j, index_i, index_j))
            
            if not possible_swaps:
                break
            
            random.shuffle(possible_swaps)  # Untuk pemilihan neighbor random
            
            for i, j, index_i, index_j in possible_swaps:
                current_iteration += 1
                
                if current_iteration >= max_iterations:  # Max iterations edge case
                    break
                
                current_total_i = self.calculate_kontainer_total(current_solution[i])
                current_total_j = self.calculate_kontainer_total(current_solution[j])
                
                if current_total_i >= self.kapasitas:  # IF sudah 100% capacity, THEN continue
                    continue
                
                # Barang variable (current)
                barang_i_temp = current_solution[i][index_i]
                barang_j_temp = current_solution[j][index_j]
                
                # New total variable IF swaps happens
                new_total_i = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
                new_total_j = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']
                
                if new_total_i > self.kapasitas or new_total_j > self.kapasitas:  # Overflow countermeassure
                    continue
                
                if (self.kapasitas - new_total_i) < (self.kapasitas - current_total_i):
                    
                    current_solution[i][index_i] = barang_j_temp
                    current_solution[j][index_j] = barang_i_temp
                    
                    improvement_found = True
                    total_improvements += 1
                    
                    waste_reduction = (self.kapasitas - current_total_i) - (self.kapasitas - new_total_i)
                    print(f"Iter {current_iteration}: Swapped {barang_i_temp['id']} ↔ {barang_j_temp['id']}")
                    print(f"  Waste reduced by {waste_reduction}")
                    
                    current_waste = self.calculate_unused(current_solution, self.kapasitas)
                    self.save_snapshot(current_solution, current_iteration, current_waste)
                    
                    break
            
            if not improvement_found:
                print(f"\nNo more improvements found with {current_iteration} iterations")
                print("Local maximum has been reached!")
        
        self.iteration_count = current_iteration
        print(f"\nTotal Iterations: {current_iteration}")
        print(f"Total Improvements: {total_improvements}")
        
        return current_solution
    
    def create_visualization(self):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), num=f'Hill Climbing Stochastic - {self.json_filename}')
        
        fig.canvas.manager.set_window_title(f'Visualisasi Hill Climbing Stochastic')
        
        def animate(frame):
            if frame >= len(self.snapshots):
                return
            
            snapshot = self.snapshots[frame]
            kontainer = snapshot['kontainer']
            objective = snapshot['objective']
            iteration = snapshot['iteration']
            
            ax1.clear()
            ax2.clear()
            
            ax1.plot(range(frame + 1), self.objective_values[:frame + 1], 'b-', linewidth=2, marker='o')
            ax1.set_title(f'Hill Climbing Stochastic - {self.json_filename}', fontsize=10)
            ax1.set_xlabel('Iterasi', fontsize=9)
            ax1.set_ylabel('Total Waste', fontsize=9)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='both', which='major', labelsize=8)
            
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
            
            ax1.text(0.02, 0.98, f'Iterasi: {iteration} | Total Waste: {objective:.2f}', 
                    transform=ax1.transAxes, fontsize=9, va='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            if frame > 0:
                for i in range(1, frame + 1):
                    if self.objective_values[i] < self.objective_values[i-1]:
                        ax1.scatter(i, self.objective_values[i], color='green', s=60, zorder=5)
            
            if kontainer:
                fills = []
                labels = []
                colors = []
                
                for i, container in enumerate(kontainer):
                    used = self.calculate_kontainer_total(container)
                    fills.append(used)
                    
                    item_ids = [item['id'] for item in container]
                    labels.append('\n'.join(item_ids) if len(item_ids) <= 3 else f'{len(item_ids)} items')
                    
                    efficiency = used / self.kapasitas
                    if efficiency >= 0.9:
                        colors.append('#2ecc71') 
                    elif efficiency >= 0.7:
                        colors.append('#f39c12') 
                    elif efficiency >= 0.5:
                        colors.append('#e67e22')  
                    else:
                        colors.append('#e74c3c')  
                
                bars = ax2.bar(range(1, len(fills) + 1), fills, color=colors, alpha=0.8)
                ax2.axhline(y=self.kapasitas, color='red', linestyle='--', linewidth=2, 
                           label=f'Kapasitas ({self.kapasitas})')
                
                for i, bar in enumerate(bars):
                    efficiency = (fills[i] / self.kapasitas) * 100
                    waste = self.kapasitas - fills[i]
                    if efficiency > 0:
                        ax2.text(bar.get_x() + bar.get_width()/2, fills[i] + self.kapasitas*0.005,
                                f'{efficiency:.0f}%\n(waste:{waste:.0f})', ha='center', va='bottom', 
                                fontweight='bold', fontsize=6)
                    
                    # Add item labels inside bars
                    if fills[i] > self.kapasitas * 0.15:
                        ax2.text(bar.get_x() + bar.get_width()/2, fills[i]/2,
                                labels[i], ha='center', va='center', fontsize=6, 
                                color='white', fontweight='bold')
            
            ax2.set_title(f'Status Kontainer (Total: {len(kontainer)})', fontsize=10)
            ax2.set_xlabel('ID Kontainer', fontsize=9)
            ax2.set_ylabel('Kapasitas Terpakai', fontsize=9)
            ax2.set_ylim(0, self.kapasitas * 1.10)
            ax2.legend(fontsize=8)
            ax2.grid(True, alpha=0.3)
            ax2.tick_params(axis='both', which='major', labelsize=8)
        
        ani = animation.FuncAnimation(fig, animate, frames=len(self.snapshots), 
                                     interval=800, repeat=True, blit=False)
        
        plt.tight_layout(pad=1.5)
        plt.subplots_adjust(hspace=0.4)
        plt.show()
        
        return ani
    
    def print_summary(self):
        print("\n" + "="*60)
        print("SUMMARY HILL CLIMBING STOCHASTIC")
        print("="*60)
        print(f"File: {self.json_filename}")
        print(f"Kapasitas kontainer: {self.kapasitas}")
        print(f"Total iterasi: {self.iteration_count}")
        print(f"Total snapshots: {len(self.snapshots)}")
        
        if self.objective_values:
            initial_waste = self.objective_values[0]
            final_waste = self.objective_values[-1]
            best_waste = min(self.objective_values)
            best_iteration = self.objective_values.index(best_waste)
            
            print(f"\nWaste awal: {initial_waste:.2f}")
            print(f"Waste akhir: {final_waste:.2f}")
            print(f"Waste terbaik: {best_waste:.2f} (iterasi {best_iteration})")
            print(f"Total improvement: {initial_waste - final_waste:.2f}")
        
        final_solution = self.snapshots[-1]['kontainer']
        efficiencies = []
        for container in final_solution:
            used = self.calculate_kontainer_total(container)
            efficiency = (used / self.kapasitas) * 100
            efficiencies.append(efficiency)
        
        print(f"\nJumlah kontainer: {len(final_solution)}")
        print(f"Efisiensi rata-rata: {np.mean(efficiencies):.1f}%")
        print(f"Efisiensi tertinggi: {max(efficiencies):.1f}%")
        print(f"Efisiensi terendah: {min(efficiencies):.1f}%")
        print("="*60)

def main():
    if len(sys.argv) > 1:
        json_filename = sys.argv[1]
    else:
        json_filename = 'case1.json'
    
    visualizer = HillClimbingStochasticVisualizer(json_filename)
    visualizer.print_summary()  
    ani = visualizer.create_visualization()

if __name__ == "__main__":
    main()