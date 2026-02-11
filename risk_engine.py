import osmnx as ox
import networkx as nx
import random
import pandas as pd

class RiskEngine:
    def __init__(self,map_path):
        self.map_path = map_path
        try:
            self.graph = ox.load_graphml(self.map_path)
            print(f"Map loaded successfully from {self.map_path}")
        except FileNotFoundError:
            print(f"Map file not found at {self.map_path}")
            self.graph = None

    def simulate_risk(self, num_simulations=1000):
        for u, v, data in self.graph.edges(data=True):
            data['accident_count']=0
        
        risk_weights = {
            'motorway': 90,
            'trunk': 80,
            'primary': 70,
            'secondary': 60,
            'tertiary': 50,
            'residential': 40,
            'unclassified': 10,
            'living_street': 1
        }

        all_edges = list(self.graph.edges(keys=True, data=True))
        attempts = num_simulations * 3
        count_events = 0

        for _ in range(attempts):
            if count_events >= num_simulations:
                break
            u, v, key, data = random.choice(all_edges)
            highway_type = data.get('highway', 'unclassified')
            if isinstance(highway_type, list):
                highway_type = highway_type[0]

            probability = risk_weights.get(highway_type, 10)   

            roll = random.randint(1, 100)
            if roll <= probability:
                self.graph.edges[u, v, key]['accident_count'] += 1
                count_events += 1
        
    def calculate_risk(self):
        ## This will rate the edges in range of 0-1 based on accident count and length
        print("Calculating risk scores...")
        
        # Find maximum accidents across all edges
        maximun_accidents = 0
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            acc = data.get('accident_count', 0)
            if acc > maximun_accidents:
                maximun_accidents = acc

        if maximun_accidents == 0:
            maximun_accidents = 1

        # Calculate risk and safety scores for each edge
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            count = data.get('accident_count', 0)
            risk_score = count / maximun_accidents
            self.graph.edges[u, v, key]['risk_score'] = risk_score
            length = data.get('length', 100)
            self.graph.edges[u, v, key]['safety_score'] = length * (1 + (risk_score * 5))
        
        print("Risk calculation completed.")

    def save_scored_map(self):
        output_path = self.map_path.replace('.graphml', '_scored.graphml')
        try:
            ox.save_graphml(self.graph, output_path)
            print(f"Scored map saved successfully to {output_path}.")
            return True, output_path
        except Exception as e:
            print(f"Error saving scored map: {e}")
            return False, f"Error saving scored map: {e}"                 

            
        
if __name__ == "__main__":
     engine = RiskEngine("C:\\Projects\\gig\\Patiala, Punjab, India_map.graphml")
     engine.simulate_risk(num_simulations=1000)
     engine.calculate_risk()
     engine.save_scored_map()