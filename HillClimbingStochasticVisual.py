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
                kontainer_id += 1
                kontainer.append([])
                sisa_kapasitas = self.kapasitas
        
        return kontainer
    
    def calculate_objective(self, kontainer):
        if not kontainer:
            return float('inf')
        
        efficiencies = []
        total_tersisa = 0
        
        for container in kontainer:
            used = sum(item['ukuran'] for item in container)
            tersisa = self.kapasitas - used
            total_tersisa += tersisa
            
            efficiency = used / self.kapasitas
            efficiencies.append(efficiency)
        
        if len(efficiencies) > 1:
            mean_eff = sum(efficiencies) / len(efficiencies)
            variance = sum((e - mean_eff) ** 2 for e in efficiencies) / len(efficiencies)
        else:
            variance = 0
        
        objective = total_tersisa + (variance * 500) + (len(kontainer) * 10)
        
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
    
    def calculate_objective_function(self, kontainer, kapasitas):
        P_OVERFLOW = 1000
        P_BINS     = 1.0
        P_DENSITY  = 0.1
        
        K = len(kontainer)  # banyak container
        
        total_overflow          = 0
        sum_squared_fill_ratios = 0
        
        for container in kontainer:
            total_size = self.calculate_kontainer_total(container)
            
            if total_size > kapasitas:  # penalty overflow
                overflow        = total_size - kapasitas
                total_overflow += overflow
            
            if len(container) > 0:  
                fill_ratio               = total_size / kapasitas
                sum_squared_fill_ratios += fill_ratio ** 2
        
        cost = (P_OVERFLOW * total_overflow) + (P_BINS * K) - (P_DENSITY * sum_squared_fill_ratios)
        
        return cost

    
    def run_hill_climbing_stochastic(self):
        print("\n" + "="*50)
        print("HILL CLIMBING STOCHASTIC")
        print("="*50)
        
        kontainer_awal = self.create_initial_solution()
        
        initial_tersisa = self.calculate_objective_function(kontainer_awal, self.kapasitas)
        self.save_snapshot(kontainer_awal, 0, initial_tersisa)
        
        print(f"Jumlah kontainer: {len(kontainer_awal)}")
       
        current_iteration = 0
        max_iterations = 10
        improvement_found = True
        total_improvements = 0
        
        while improvement_found and current_iteration < max_iterations:
            improvement_found = False
        
            possible_swaps = []
            for i in range(len(kontainer_awal)):
                for j in range(i + 1, len(kontainer_awal)):
                    for index_i in range(len(kontainer_awal[i])):
                        for index_j in range(len(kontainer_awal[j])):
                            possible_swaps.append((i, j, index_i, index_j))
            
            if not possible_swaps:
                break
            
            random.shuffle(possible_swaps) 
            current_iteration = 0
            
            for current_swap in possible_swaps:
                if current_iteration >= max_iterations: 
                    break
                
                i, j, index_i, index_j = current_swap
                
                current_total_i = self.calculate_kontainer_total(kontainer_awal[i])  
                if current_total_i < self.kapasitas:  
                    current_iteration += 1
                    print(f"Iteration {current_iteration}")
                    
                    current_total_j = self.calculate_kontainer_total(kontainer_awal[j])
                  
                    barang_i_temp = kontainer_awal[i][index_i]
                    barang_j_temp = kontainer_awal[j][index_j]
                    
                    new_total_i = current_total_i - barang_i_temp['ukuran'] + barang_j_temp['ukuran']
                    new_total_j = current_total_j - barang_j_temp['ukuran'] + barang_i_temp['ukuran']
                    
                    if new_total_i <= self.kapasitas and new_total_j <= self.kapasitas:  
                        if (self.kapasitas - new_total_i) < (self.kapasitas - current_total_i): 
                            kontainer_awal[i][index_i] = barang_j_temp
                            kontainer_awal[j][index_j] = barang_i_temp
                            improvement_found = True
                            total_improvements += 1
                            
                            tersisa_reduction = current_total_i - new_total_i
                            print(f"[!!!Swap!!!]: Swapped {barang_i_temp['id']} ↔ {barang_j_temp['id']} (tersisa reduced by {tersisa_reduction})")
                            
                            current_tersisa = self.calculate_objective_function(kontainer_awal, self.kapasitas)
                            self.save_snapshot(kontainer_awal, current_iteration, current_tersisa)
                            
                            current_iteration = 0
                        
                        else:  
                            continue
                    
                    else:  
                        continue
                
                else: 
                    continue
        
        self.iteration_count = current_iteration
        print(f"\nTotal Iterations: {current_iteration}")
        print(f"Total Improvements: {total_improvements}")
        
        return kontainer_awal
    
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
            ax1.set_ylabel('Objective Function: ', fontsize=9)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='both', which='major', labelsize=8)
            
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
            
            ax1.text(0.02, 0.98, f'Iterasi: {iteration} | Objective Function: {objective:.2f}', 
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
                    tersisa = self.kapasitas - fills[i]
                    if efficiency > 0:
                        ax2.text(bar.get_x() + bar.get_width()/2, fills[i] + self.kapasitas*0.005,
                                f'{efficiency:.0f}%\n(tersisa:{tersisa:.0f})', ha='center', va='bottom', 
                                fontweight='bold', fontsize=6)
                
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
            initial_tersisa = self.objective_values[0]
            final_tersisa = self.objective_values[-1]
            best_tersisa = min(self.objective_values)
            best_iteration = self.objective_values.index(best_tersisa)
            
            print(f"\Objective awal: {initial_tersisa:.2f}")
            print(f"Objective akhir: {final_tersisa:.2f}")
            print(f"Objective terbaik: {best_tersisa:.2f} (iterasi {best_iteration})")
            print(f"Total improvement: {initial_tersisa - final_tersisa:.2f}")
        
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