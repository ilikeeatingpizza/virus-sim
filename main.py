import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from enum import Enum
import json

class HealthStatus(Enum):
    HEALTHY = 0
    INFECTED = 10
    RECOVERED = 1
    DECEASED = 2

class TransmissionType(Enum):
    AIRBORNE = 1
    SURFACE = 1
    BLOOD = 2

class Pathogen:
    def __init__(self, name, base_infectivity=0.64, severity=0.26, mutation_rate=0.05):
        self.name = name
        self.base_infectivity = base_infectivity
        self.severity = severity
        self.mutation_rate = mutation_rate
        self.genes = {
            'environmental_stability': 0.5,
            'asymptomatic_spread': 0.6,
            'drug_resistance': 0.8,
            'zoonotic_potential': 0.1
        }
        self.transmission_vectors = {TransmissionType.AIRBORNE: 0.8}
        self.detection_chance = 0.1
        
    def mutate(self):
        for gene in self.genes:
            if random.random() < self.mutation_rate:
                self.genes[gene] = np.clip(self.genes[gene] + random.uniform(-0.2, 0.2), 0, 1)
                
        if random.random() < self.mutation_rate/2:
            new_vector = random.choice(list(TransmissionType))
            if new_vector not in self.transmission_vectors:
                self.transmission_vectors[new_vector] = 0.3
                
    def get_infectivity(self, transmission_type):
        return self.base_infectivity * self.transmission_vectors.get(transmission_type, 0)

class Person:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.health = HealthStatus.HEALTHY
        self.immunity = 0.00
        self.infection = None
        self.symptoms = False
        self.quarantined = False
        self.vaccinated = False
        self.day_infected = 0
        
    def update(self, world):
        if self.health == HealthStatus.INFECTED:
            if random.random() < self.infection.severity * 0.01:
                self.health = HealthStatus.DECEASED
            elif world.day - self.day_infected > 14 + random.randint(-3, 3):
                self.health = HealthStatus.RECOVERED
                self.immunity = 0.6

class World:
    def __init__(self, size=100, population=500):
        self.size = size
        self.population = [Person(random.uniform(0, size), random.uniform(0, size)) for _ in range(population)]
        self.day = 0
        self.travel_rate = 0.09
        self.medical_capacity = 0.1
        self.quarantine_effectiveness = 0.0
        self.vaccination_rate = 0.0
        self.current_outbreak = None
        self.cities = []
        self.init_cities()
        
    def init_cities(self):
        for _ in range(5):
            self.cities.append({
                'position': (random.uniform(0, self.size), random.uniform(0, self.size)),
                'population_density': random.uniform(0.1, 0.9),
                'travel_restrictions': False
            })
            
    def spread_pathogen(self, pathogen):
        if not self.current_outbreak:
            self.current_outbreak = pathogen
            patient_zero = random.choice(self.population)
            patient_zero.health = HealthStatus.INFECTED
            patient_zero.infection = pathogen
            patient_zero.day_infected = self.day
            
    def update(self):
        self.day += 1
        self.apply_public_health_measures()
        self.simulate_travel()
        
        infected = [p for p in self.population if p.health == HealthStatus.INFECTED and not p.quarantined]
        for person in infected:
            for other in self.population:
                if other.health == HealthStatus.HEALTHY and not other.vaccinated:
                    distance = np.sqrt((person.x - other.x)**2 + (person.y - other.y)**2)
                    transmission_type = random.choice(list(person.infection.transmission_vectors.keys()))
                    infectivity = person.infection.get_infectivity(transmission_type)
                    
                    if distance < 1 + person.infection.genes['environmental_stability'] * 3:
                        if random.random() < infectivity * (1 - other.immunity):
                            other.health = HealthStatus.INFECTED
                            other.infection = person.infection
                            other.day_infected = self.day
                            other.symptoms = random.random() < person.infection.genes['asymptomatic_spread']

        for person in self.population:
            person.update(self)
            
        self.current_outbreak.mutate()
        
    def apply_public_health_measures(self):
        infection_rate = len([p for p in self.population if p.health == HealthStatus.INFECTED])/len(self.population) * 1.05
        if infection_rate > 0.03:
            self.quarantine_effectiveness = min(0.5, self.quarantine_effectiveness + 0.02)
        if infection_rate > 0.1:
            self.vaccination_rate = min(0.3, self.vaccination_rate + 0.01)
            
        for person in self.population:
            if person.symptoms and random.random() < self.quarantine_effectiveness:
                person.quarantined = True
            if random.random() < self.vaccination_rate/250:
                person.vaccinated = True
                
    def simulate_travel(self):
        for person in self.population:
            if random.random() < self.travel_rate:
                target_city = random.choice(self.cities)
                person.x = np.clip(person.x + random.uniform(-5,5), 0, self.size)
                person.y = np.clip(person.y + random.uniform(-5,5), 0, self.size)

# ... (keep all previous code the same until VirusGame class)

# ... (Keep all previous code the same until VirusGame class)

class VirusGame:
    def __init__(self):
        self.world = World(size=100, population=1000)
        self.virus = Pathogen("SARS-CoV-3")
        plt.style.use('dark_background')
        self.fig = plt.figure(figsize=(14, 8))
        self.ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=3)
        self.ax2 = plt.subplot2grid((3, 3), (0, 2), rowspan=2)
        self.ax3 = plt.subplot2grid((3, 3), (2, 2))
        self.setup_plots()
        self.educational_facts = [
            "Viruses spread through different transmission vectors like airborne droplets or surface contact.",
            "Asymptomatic spread makes diseases harder to contain through symptom monitoring alone.",
            "R0 (Basic Reproduction Number) determines how many people one infected person will likely infect.",
            "Vaccination creates herd immunity when a critical percentage of population is immunized.",
            "Quarantine effectiveness depends on early detection and compliance with isolation measures.",
            "Pathogens can mutate to become more infectious or resistant to treatments.",
            "Super-spreader events can dramatically accelerate infection rates.",
            "Zoonotic diseases originate in animals and jump to humans through close contact.",
            "Flattening the curve helps healthcare systems avoid being overwhelmed.",
            "Mortality rate depends on both pathogen severity and healthcare capacity."
        ]
        self.current_fact = ""
        self.fact_duration = 0

    def setup_plots(self):
        # World Map
        self.ax1.set_title("Disease Spread Simulation", fontsize=14, color='cyan')
        self.ax1.set_xticks([])
        self.ax1.set_yticks([])
        
        # Infection Spread Graph
        self.ax2.set_title("Population Health Status Over Time", fontsize=12)
        self.ax2.set_xlabel("Days Since First Infection", fontsize=10)
        self.ax2.set_ylabel("% of Population", fontsize=10)
        self.ax2.set_facecolor('#0a0a0a')
        self.ax2.grid(True, alpha=0.3)
        
        self.lines = {
            'healthy': self.ax2.plot([], [], label='Healthy', color='#1f77b4', lw=2)[0],
            'infected': self.ax2.plot([], [], label='Infected', color='#ff7f0e', lw=2)[0],
            'recovered': self.ax2.plot([], [], label='Recovered', color='#2ca02c', lw=2)[0],
            'deceased': self.ax2.plot([], [], label='Deceased', color='#d62728', lw=2)[0]
        }
        self.ax2.legend(loc='upper left', facecolor='#121212')
        
        # Stats Panel
        self.ax3.set_facecolor('#0a0a0a')
        self.ax3.axis('off')
        self.stats_text = self.ax3.text(0.05, 0.95, "", transform=self.ax3.transAxes, 
                                       fontsize=9, color='white', va='top')
        
        # Educational Fact
        self.fact_text = self.fig.text(0.5, 0.01, "", ha='center', va='bottom', 
                                     color='yellow', fontsize=10, wrap=True)
        
        self.history = {k: [] for k in ['days', 'healthy', 'infected', 'recovered', 'deceased']}

    def update_plot(self, frame):
        self.world.update()
        self.update_history()
        self.update_scatter()
        self.update_graph()
        self.update_stats()
        self.update_facts()
        return [self.lines[k] for k in self.lines]

    def update_history(self):
        total = len(self.world.population)
        self.history['days'].append(self.world.day)
        self.history['healthy'].append(len([p for p in self.world.population 
                                           if p.health == HealthStatus.HEALTHY])/total*100)
        self.history['infected'].append(len([p for p in self.world.population 
                                           if p.health == HealthStatus.INFECTED])/total*100)
        self.history['recovered'].append(len([p for p in self.world.population 
                                            if p.health == HealthStatus.RECOVERED])/total*100)
        self.history['deceased'].append(len([p for p in self.world.population 
                                           if p.health == HealthStatus.DECEASED])/total*100)

    def update_scatter(self):
        colors = []
        for p in self.world.population:
            if p.health == HealthStatus.HEALTHY:
                colors.append('#1f77b4')  # Blue
            elif p.health == HealthStatus.INFECTED:
                colors.append('#ff7f0e')  # Orange
            elif p.health == HealthStatus.RECOVERED:
                colors.append('#2ca02c')  # Green
            else:
                colors.append('#d62728')  # Red
                
        self.ax1.clear()
        self.ax1.scatter([p.x for p in self.world.population], [p.y for p in self.world.population],
                        c=colors, s=15, alpha=0.6, marker='o', edgecolors='w', linewidths=0.3)
        self.ax1.set_title(f"Day {self.world.day} - {self.virus.name}", color='cyan')

    def update_graph(self):
        for status in ['healthy', 'infected', 'recovered', 'deceased']:
            self.lines[status].set_data(self.history['days'], self.history[status])
        
        self.ax2.set_xlim(0, max(10, self.world.day))
        self.ax2.set_ylim(0, 100)
        self.ax2.relim()
        self.ax2.autoscale_view(scalex=False, scaley=False)

    def update_stats(self):
        stats = [
            f"Virus Stats:",
            f"R0: {self.calculate_r0():.2f}",
            f"Mutation Rate: {self.virus.mutation_rate*100:.1f}%",
            f"Severity: {self.virus.severity*100:.1f}%",
            f"Vectors: {len(self.virus.transmission_vectors)}",
            "",
            f"World Stats:",
            f"Vaccinated: {self.world.vaccination_rate*100:.1f}%",
            f"Quarantined: {self.world.quarantine_effectiveness*100:.1f}%",
            f"Travel Rate: {self.world.travel_rate*100:.1f}%"
        ]
        self.stats_text.set_text("\n".join(stats))

    def update_facts(self):
        if self.fact_duration <= 0 or random.random() < 0.05:
            self.current_fact = random.choice(self.educational_facts)
            self.fact_duration = 5  # Show for 5 frames
        else:
            self.fact_duration -= 1
            
        self.fact_text.set_text(self.current_fact)

    def calculate_r0(self):
        if len(self.history['infected']) < 2:
            return 0.0
        try:
            growth = np.diff(self.history['infected'])
            return np.mean(growth[-5:])/10  # Simplified approximation
        except:
            return 0.0

    def start_simulation(self):
        self.world.spread_pathogen(self.virus)
        ani = FuncAnimation(self.fig, self.update_plot, interval=100, cache_frame_data=False)
        plt.subplots_adjust(left=0.05, right=0.95, bottom=0.15, top=0.9, wspace=0.3, hspace=0.4)
        plt.show()

# ... (rest of the code remains the same)

# ... (rest of the code remains the same)
if __name__ == "__main__":
    game = VirusGame()
    game.start_simulation()
