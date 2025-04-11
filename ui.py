import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np
import json
from tkinter import ttk
from shapely.geometry import LineString

DATA_FILE = 'simulation_data.json'

class SimulationUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Car Simulation")

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Create frames for each tab
        self.sensor_tab = ttk.Frame(self.notebook)
        self.avg_fitness_tab = ttk.Frame(self.notebook)
        self.ind_fitness_tab = ttk.Frame(self.notebook)
        self.path_tab = ttk.Frame(self.notebook)
        self.fitness_progression_tab = ttk.Frame(self.notebook)
        self.fitness_distribution_tab = ttk.Frame(self.notebook)
        self.dynamics_tab = ttk.Frame(self.notebook)
        self.crash_stats_tab = ttk.Frame(self.notebook)

        # Add tabs to the notebook
        self.notebook.add(self.sensor_tab, text='Sensor Data')
        self.notebook.add(self.avg_fitness_tab, text='Average Fitness')
        self.notebook.add(self.ind_fitness_tab, text='Individual Fitness')
        self.notebook.add(self.path_tab, text='Path Followed')
        self.notebook.add(self.fitness_progression_tab, text='Fitness Progression')
        self.notebook.add(self.fitness_distribution_tab, text='Fitness Distribution')
        self.notebook.add(self.dynamics_tab, text='Dynamics')
        self.notebook.add(self.crash_stats_tab, text='Crash Stats')

        # Create figures and axes
        self.sensor_figure, self.sensor_ax = plt.subplots(figsize=(5, 4))
        self.avg_fitness_figure, self.avg_fitness_ax = plt.subplots(figsize=(5, 4))
        self.ind_fitness_figure, self.ind_fitness_ax = plt.subplots(figsize=(5, 4))
        self.path_figure, self.path_ax = plt.subplots(figsize=(5, 4))
        self.fitness_progression_figure, self.fitness_progression_ax = plt.subplots(figsize=(5, 4))
        self.fitness_distribution_figure, self.fitness_distribution_ax = plt.subplots(figsize=(5, 4))
        self.dynamics_figure, self.dynamics_ax = plt.subplots(figsize=(5, 4))
        self.crash_stats_figure, self.crash_stats_ax = plt.subplots(figsize=(5, 4))

        # Create canvas for each tab
        self.sensor_canvas = FigureCanvasTkAgg(self.sensor_figure, master=self.sensor_tab)
        self.sensor_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.avg_fitness_canvas = FigureCanvasTkAgg(self.avg_fitness_figure, master=self.avg_fitness_tab)
        self.avg_fitness_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.ind_fitness_canvas = FigureCanvasTkAgg(self.ind_fitness_figure, master=self.ind_fitness_tab)
        self.ind_fitness_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.path_canvas = FigureCanvasTkAgg(self.path_figure, master=self.path_tab)
        self.path_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fitness_progression_canvas = FigureCanvasTkAgg(self.fitness_progression_figure, master=self.fitness_progression_tab)
        self.fitness_progression_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fitness_distribution_canvas = FigureCanvasTkAgg(self.fitness_distribution_figure, master=self.fitness_distribution_tab)
        self.fitness_distribution_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.dynamics_canvas = FigureCanvasTkAgg(self.dynamics_figure, master=self.dynamics_tab)
        self.dynamics_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.crash_stats_canvas = FigureCanvasTkAgg(self.crash_stats_figure, master=self.crash_stats_tab)
        self.crash_stats_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Initialize plots
        self.init_plots()

        # Start the update loop
        self.schedule_update()

        self.best_path = None

    def init_plots(self):
        # Initialize plots with empty data
        self.sensor_ax.set_title("Sensor Data")
        self.sensor_ax.set_xlabel("Sensor Index")
        self.sensor_ax.set_ylabel("Distance")

        self.avg_fitness_ax.set_title("Average Fitness Over Generations")
        self.avg_fitness_ax.set_xlabel("Generation")
        self.avg_fitness_ax.set_ylabel("Average Fitness")

        self.ind_fitness_ax.set_title("Individual Fitness Over Generations")
        self.ind_fitness_ax.set_xlabel("Generation")
        self.ind_fitness_ax.set_ylabel("Fitness")

        self.path_ax.set_title("Path Followed")
        self.path_ax.set_xlabel("X Position")
        self.path_ax.set_ylabel("Y Position")
        self.path_ax.set_aspect('equal')

        self.fitness_progression_ax.set_title("Fitness Progression")
        self.fitness_progression_ax.set_xlabel("Generation")
        self.fitness_progression_ax.set_ylabel("Fitness")

        self.fitness_distribution_ax.set_title("Fitness Distribution")
        self.fitness_distribution_ax.set_xlabel("Fitness")
        self.fitness_distribution_ax.set_ylabel("Count")

        self.dynamics_ax.set_title("Car Dynamics")
        self.dynamics_ax.set_xlabel("Car Index")
        self.dynamics_ax.set_ylabel("Value")

        self.crash_stats_ax.set_title("Crash Statistics")
        self.crash_stats_ax.set_xlabel("Generation")
        self.crash_stats_ax.set_ylabel("Crashes")

    def read_data_file(self):
        try:
            with open(DATA_FILE, 'r') as f:
                try:
                    data = json.load(f)
                    return data
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                    return None
        except FileNotFoundError:
            print(f"File {DATA_FILE} not found")
            return None

    def update_plots(self):
        data = self.read_data_file()
        if not data:
            return

        # Process sensor data
        self.sensor_data = data.get('sensor_data', [[]])
        if self.sensor_data:
            self.sensor_data = self.sensor_data[0]
        else: 
            self.sensor_data = [0]*5

        # Process fitness data
        self.avg_fitness = data.get('avg_fitness_history', [])
        self.ind_fitness = data.get('fitness_history', [])
        self.generation = data.get('generation', 0)

        # Process path data
        self.path_data = []
        self.best_path = None
        max_fitness = -1
        
        for car_data in data.get('detailed_path_data', []):
            if isinstance(car_data, dict):
                path = car_data.get('path', [])
                fitness = car_data.get('fitness', 0)
                if path:
                    self.path_data.append(np.array(path))
                    if fitness > max_fitness:
                        max_fitness = fitness
                        self.best_path = LineString(path)

        # Update sensor plot
        self.sensor_ax.clear()
        self.sensor_ax.bar(range(len(self.sensor_data)), self.sensor_data)
        self.sensor_ax.set_title("Sensor Data")
        self.sensor_canvas.draw()

        # Update average fitness plot
        self.avg_fitness_ax.clear()
        if self.avg_fitness:
            self.avg_fitness_ax.plot(range(len(self.avg_fitness)), self.avg_fitness)
        self.avg_fitness_ax.set_title("Average Fitness Over Generations")
        self.avg_fitness_canvas.draw()

        # Update individual fitness plot
        self.ind_fitness_ax.clear()
        if self.ind_fitness:
            self.ind_fitness_ax.plot(range(len(self.ind_fitness)), self.ind_fitness)
        self.ind_fitness_ax.set_title("Individual Fitness Over Generations")
        self.ind_fitness_canvas.draw()

        # Update path plot
        self.path_ax.clear()
        for path in self.path_data:
            if len(path) > 1:
                x, y = path.T
                self.path_ax.plot(x, y, color='blue', alpha=0.1)
        if self.best_path:
            x, y = self.best_path.xy
            self.path_ax.plot(x, y, color='red', linewidth=2)
        self.path_ax.set_title("Path Followed")
        self.path_canvas.draw()

        # Update fitness progression plot
        self.fitness_progression_ax.clear()
        if self.ind_fitness:
            self.fitness_progression_ax.plot(range(len(self.ind_fitness)), self.ind_fitness, 'r-', label='Max')
        if self.avg_fitness:
            self.fitness_progression_ax.plot(range(len(self.avg_fitness)), self.avg_fitness, 'b--', label='Avg')
        self.fitness_progression_ax.set_title("Fitness Progression")
        self.fitness_progression_ax.legend()
        self.fitness_progression_canvas.draw()

        # Update fitness distribution plot
        self.fitness_distribution_ax.clear()
        if self.ind_fitness:
            bins = min(20, len(self.ind_fitness))
            if bins > 0:
                self.fitness_distribution_ax.hist(self.ind_fitness, bins=bins, color='skyblue', edgecolor='black')
        self.fitness_distribution_ax.set_title(f"Fitness Distribution - Gen {self.generation}")
        self.fitness_distribution_canvas.draw()

        # Update dynamics plot
        self.dynamics_ax.clear()
        velocities = data.get('velocities', [])
        headings = data.get('headings', [])
        if velocities:
            self.dynamics_ax.plot(range(len(velocities)), velocities, 'g-', label='Velocity')
        if headings:
            self.dynamics_ax.plot(range(len(headings)), headings, 'r-', label='Heading')
        self.dynamics_ax.set_title("Car Dynamics")
        if velocities or headings:
            self.dynamics_ax.legend()
        self.dynamics_canvas.draw()

        # Update crash stats plot
        self.crash_stats_ax.clear()
        crash_history = data.get('crash_history', [])
        if crash_history:
            self.crash_stats_ax.bar(range(len(crash_history)), crash_history, color='red')
        self.crash_stats_ax.set_title("Crashes per Generation")
        self.crash_stats_canvas.draw()

    def schedule_update(self):
        try:
            if self.root.winfo_exists():
                self.root.after(1000, self.schedule_update)
                self.update_plots()
        except Exception as e:
            print(f"Error scheduling update: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationUI(root)
    root.mainloop()