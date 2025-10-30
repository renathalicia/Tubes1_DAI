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
        
        # Load data and run algorithm
        self.load_data()
        self.run_hill_climbing_stochastic()
        
    def load_data(self):
        """Load data dari file JSON"""
        try:
            with open(self.json_filename, 'r') as f:
                data = json.load(f)
            
            self.kapasitas = data['kapasitas_kontainer']
            self.barang = data['barang'].copy()
            
            print(f"Loaded: {self.json_filename}")
            print(f"Kapasitas kontainer: {self.kapasitas}")
            print(f"Jumlah barang: {len(self.barang)}")
            
        except FileNotFoundError:
            print(f"Error: File {self.json_filename} tidak ditemukan!")
            sys.exit(1)
    
    def create_initial_solution(self):
        """Membuat solusi awal secara random"""
        random.seed(42)  # Untuk konsistensi
        
        kontainer = []
        kontainer_id = 0
        barang_copy = self.barang.copy()
        
        # Mulai dengan kontainer pertama
        kontainer.append([])
        sisa_kapasitas = self.kapasitas
        
        while barang_copy:
            # Pilih barang secara random
            random_index = random.randint(0, len(barang_copy) - 1)
            barang_terpilih = barang_copy[random_index]
            
            # Cek apakah muat di kontainer saat ini
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
        """
        Menghitung nilai objektif
        Objective: Minimasi waste + variance efisiensi
        """
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
        
        # Hitung variance efisiensi
        if len(efficiencies) > 1:
            mean_eff = sum(efficiencies) / len(efficiencies)
            variance = sum((e - mean_eff) ** 2 for e in efficiencies) / len(efficiencies)
        else:
            variance = 0
        
        # Objective function: kombinasi waste dan variance
        objective = total_waste + (variance * 500) + (len(kontainer) * 10)
        
        return objective
    
    def get_neighbors(self, kontainer):
        """Generate semua kemungkinan swap neighbors"""
        neighbors = []
        
        for i in range(len(kontainer)):
            for j in range(i + 1, len(kontainer)):
                for idx_i in range(len(kontainer[i])):
                    for idx_j in range(len(kontainer[j])):
                        # Coba swap item antara container i dan j
                        neighbor = [container.copy() for container in kontainer]
                        
                        item_i = neighbor[i][idx_i]
                        item_j = neighbor[j][idx_j]
                        
                        # Cek apakah swap valid (tidak melebihi kapasitas)
                        used_i = sum(item['ukuran'] for item in neighbor[i])
                        used_j = sum(item['ukuran'] for item in neighbor[j])
                        
                        new_used_i = used_i - item_i['ukuran'] + item_j['ukuran']
                        new_used_j = used_j - item_j['ukuran'] + item_i['ukuran']
                        
                        if new_used_i <= self.kapasitas and new_used_j <= self.kapasitas:
                            # Lakukan swap
                            neighbor[i][idx_i] = item_j
                            neighbor[j][idx_j] = item_i
                            neighbors.append(neighbor)
        
        return neighbors
    
    def save_snapshot(self, kontainer, iteration, objective):
        """Simpan snapshot untuk visualisasi"""
        snapshot = {
            'iteration': iteration,
            'kontainer': [container.copy() for container in kontainer],
            'objective': objective
        }
        self.snapshots.append(snapshot)
        self.objective_values.append(objective)
    
    def run_hill_climbing_stochastic(self):
        """Menjalankan algoritma Hill Climbing Stochastic"""
        print("\n" + "="*50)
        print("HILL CLIMBING STOCHASTIC")
        print("="*50)
        
        # Inisialisasi solusi awal
        current_solution = self.create_initial_solution()
        current_objective = self.calculate_objective(current_solution)
        
        print(f"Solusi awal - Objektif: {current_objective:.2f}")
        print(f"Jumlah kontainer: {len(current_solution)}")
        
        # Simpan snapshot awal
        self.save_snapshot(current_solution, 0, current_objective)
        
        max_iterations = 100
        iteration = 0
        improvement_found = True
        
        while improvement_found and iteration < max_iterations:
            improvement_found = False
            iteration += 1
            
            # Generate all possible neighbors
            neighbors = self.get_neighbors(current_solution)
            
            if not neighbors:
                break
            
            # Pilih neighbor secara stochastic
            random.shuffle(neighbors)
            
            for neighbor in neighbors:
                neighbor_objective = self.calculate_objective(neighbor)
                
                # Hill climbing: terima jika lebih baik
                if neighbor_objective < current_objective:
                    current_solution = neighbor
                    current_objective = neighbor_objective
                    improvement_found = True
                    
                    print(f"Iterasi {iteration}: Objektif baru = {current_objective:.2f}")
                    self.save_snapshot(current_solution, iteration, current_objective)
                    break
        
        self.iteration_count = iteration
        print(f"\nSelesai setelah {iteration} iterasi")
        print(f"Objektif akhir: {current_objective:.2f}")
        
        return current_solution
    
    def create_visualization(self):
        """Membuat visualisasi animasi"""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6), num=f'Hill Climbing Stochastic - {self.json_filename}')
        
        # Set window title
        fig.canvas.manager.set_window_title(f'Visualisasi Hill Climbing Stochastic')
        
        def animate(frame):
            if frame >= len(self.snapshots):
                return
            
            snapshot = self.snapshots[frame]
            kontainer = snapshot['kontainer']
            objective = snapshot['objective']
            iteration = snapshot['iteration']
            
            # Clear axes
            ax1.clear()
            ax2.clear()
            
            # Plot 1: Objective Function Progress
            ax1.plot(range(frame + 1), self.objective_values[:frame + 1], 'b-', linewidth=2, marker='o')
            ax1.set_title(f'Hill Climbing Stochastic - {self.json_filename}', fontsize=10)
            ax1.set_xlabel('Iterasi', fontsize=9)
            ax1.set_ylabel('Nilai Objektif', fontsize=9)
            ax1.grid(True, alpha=0.3)
            ax1.tick_params(axis='both', which='major', labelsize=8)
            
            # Format y-axis to show integers only (no decimals)
            ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x)}'))
            
            # Add iteration info as text annotation instead of title
            ax1.text(0.02, 0.98, f'Iterasi: {iteration} | Objektif: {objective:.2f}', 
                    transform=ax1.transAxes, fontsize=9, va='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.7))
            
            # Highlight improvements
            if frame > 0:
                for i in range(1, frame + 1):
                    if self.objective_values[i] < self.objective_values[i-1]:
                        ax1.scatter(i, self.objective_values[i], color='green', s=60, zorder=5)
            
            # Plot 2: Container Visualization
            if kontainer:
                fills = []
                labels = []
                colors = []
                
                for i, container in enumerate(kontainer):
                    used = sum(item['ukuran'] for item in container)
                    fills.append(used)
                    
                    # Labels dengan ID barang
                    item_ids = [item['id'] for item in container]
                    labels.append('\n'.join(item_ids) if len(item_ids) <= 3 else f'{len(item_ids)} items')
                    
                    # Color coding berdasarkan efisiensi
                    efficiency = used / self.kapasitas
                    if efficiency >= 0.9:
                        colors.append('#2ecc71')  # Hijau
                    elif efficiency >= 0.7:
                        colors.append('#f39c12')  # Orange
                    elif efficiency >= 0.5:
                        colors.append('#e67e22')  # Dark orange
                    else:
                        colors.append('#e74c3c')  # Merah
                
                bars = ax2.bar(range(1, len(fills) + 1), fills, color=colors, alpha=0.8)
                ax2.axhline(y=self.kapasitas, color='red', linestyle='--', linewidth=2, 
                           label=f'Kapasitas ({self.kapasitas})')
                
                # Add efficiency labels (reduced spacing)
                for i, bar in enumerate(bars):
                    efficiency = (fills[i] / self.kapasitas) * 100
                    if efficiency > 0:  # Only show if there's content
                        ax2.text(bar.get_x() + bar.get_width()/2, fills[i] + self.kapasitas*0.005,
                                f'{efficiency:.0f}%', ha='center', va='bottom', fontweight='bold', fontsize=7)
                    
                    # Add item labels inside bars (smaller font and better positioning)
                    if fills[i] > self.kapasitas * 0.15:  # Only show if bar is tall enough
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
        
        # Buat animasi
        ani = animation.FuncAnimation(fig, animate, frames=len(self.snapshots), 
                                     interval=800, repeat=True, blit=False)
        
        plt.tight_layout(pad=1.5)  # Increased padding
        plt.subplots_adjust(hspace=0.4)  # Add space between subplots
        plt.show()
        
        return ani
    
    def print_summary(self):
        """Print summary hasil optimasi"""
        print("\n" + "="*60)
        print("SUMMARY HILL CLIMBING STOCHASTIC")
        print("="*60)
        print(f"File: {self.json_filename}")
        print(f"Kapasitas kontainer: {self.kapasitas}")
        print(f"Total iterasi: {self.iteration_count}")
        print(f"Total snapshots: {len(self.snapshots)}")
        
        if self.objective_values:
            initial_obj = self.objective_values[0]
            final_obj = self.objective_values[-1]
            best_obj = min(self.objective_values)
            best_iteration = self.objective_values.index(best_obj)
            
            print(f"\nObjektif awal: {initial_obj:.2f}")
            print(f"Objektif akhir: {final_obj:.2f}")
            print(f"Objektif terbaik: {best_obj:.2f} (iterasi {best_iteration})")
            print(f"Total improvement: {initial_obj - final_obj:.2f}")
        
        # Container statistics
        final_solution = self.snapshots[-1]['kontainer']
        efficiencies = []
        for container in final_solution:
            used = sum(item['ukuran'] for item in container)
            efficiency = (used / self.kapasitas) * 100
            efficiencies.append(efficiency)
        
        print(f"\nJumlah kontainer: {len(final_solution)}")
        print(f"Efisiensi rata-rata: {np.mean(efficiencies):.1f}%")
        print(f"Efisiensi tertinggi: {max(efficiencies):.1f}%")
        print(f"Efisiensi terendah: {min(efficiencies):.1f}%")
        print("="*60)

def main():
    # Ambil nama file dari command line atau gunakan default
    if len(sys.argv) > 1:
        json_filename = sys.argv[1]
    else:
        json_filename = 'case1.json'
    
    # Buat visualizer dan jalankan
    visualizer = HillClimbingStochasticVisualizer(json_filename)
    
    # Print summary
    visualizer.print_summary()
    
    # Tampilkan visualisasi
    ani = visualizer.create_visualization()

if __name__ == "__main__":
    main()