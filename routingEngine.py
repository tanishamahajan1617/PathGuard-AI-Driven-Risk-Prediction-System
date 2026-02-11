import osmnx as ox
import networkx as nx



class RoutingEngine:
    def __init__(self, map_path):
        try:
            self.graph = ox.load_graphml(map_path)
            print(f"Map loaded successfully from {map_path}")
            # Normalize numeric edge attributes (GraphML may store them as strings)
            self._coerce_edge_types()
        except FileNotFoundError:
            print(f"Map file not found at {map_path}")
            self.graph = None

    def _coerce_edge_types(self):
        for u, v, key, data in self.graph.edges(keys=True, data=True):
            # length
            try:
                if 'length' in data:
                    data['length'] = float(data.get('length', 0))
            except (TypeError, ValueError):
                data['length'] = 0.0

            # risk_score
            try:
                if 'risk_score' in data:
                    data['risk_score'] = float(data.get('risk_score', 0))
            except (TypeError, ValueError):
                data['risk_score'] = 0.0

            # travel_time
            try:
                if 'travel_time' in data:
                    data['travel_time'] = float(data.get('travel_time', 0))
            except (TypeError, ValueError):
                data['travel_time'] = None

            # accident_count
            try:
                if 'accident_count' in data:
                    data['accident_count'] = int(float(data.get('accident_count', 0)))
            except (TypeError, ValueError):
                data['accident_count'] = 0 
    def find_route(self, start_coords, end_coords, route_type='fastest'):
        orig_node = ox.distance.nearest_nodes(self.graph, start_coords[1], start_coords[0])
        dest_node = ox.distance.nearest_nodes(self.graph, end_coords[1], end_coords[0]) 
        if route_type == 'safest':
            weight = 'risk_score'
            print("Finding safest route...")
        else:
            weight = 'travel_time' if 'travel_time' in self.graph.edges[next(iter(self.graph.edges))] else 'length'
            print("Finding fastest route...")
        try:
            route = nx.shortest_path(self.graph, orig_node, dest_node, weight=weight)

            stats = self.calculate_route_stats(route)
            return route, stats
        except nx.NetworkXNoPath:
            print("No path found between the specified points.")
            return None, None
        
    def calculate_route_stats(self, route):
            total_length = 0.0
            total_risk = 0.0

            for i in range(len(route) - 1):
                u, v = route[i], route[i + 1]
                edge_data = self.graph.get_edge_data(u, v)
                if not edge_data:
                    continue

                # If edge_data is a dict (MultiGraph), take the first edge's attributes
                if isinstance(edge_data, dict):
                    edge_info = next(iter(edge_data.values()))
                else:
                    edge_info = edge_data

                # Coerce numeric fields to proper types (GraphML may store them as strings)
                try:
                    length_val = float(edge_info.get('length', 0))
                except (TypeError, ValueError):
                    length_val = 0.0

                try:
                    risk_val = float(edge_info.get('risk_score', 0))
                except (TypeError, ValueError):
                    risk_val = 0.0

                total_length += length_val
                total_risk += risk_val

            return {
                'total_length': total_length,
                'total_risk': total_risk
            }
        