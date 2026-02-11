import osmnx as ox
import networkx as nx
import json
class map_engine:
    def __init__(self):
        self.graph = None
        self.place_name = None

    def build_map(self, place_name):
        try:
            self.place_name = place_name
            print(f"Building map for {place_name}...")
            self.graph = ox.graph_from_place(place_name, network_type='drive')
            self.graph = ox.add_edge_speeds(self.graph)
            self.graph = ox.add_edge_travel_times(self.graph)
            print("Map built successfully.")
            return True, "Map built successfully."
        except Exception as e:
            print(f"Error building map: {e}")
            return False, f"Error building map: {e}"
        
    def get_coordinates(self, location_name):
        try:
            print(f"Getting coordinates for {location_name},{self.place_name}...")
            lat, lon = ox.geocode(f"{location_name}, {self.place_name}")
            print(f"Coordinates for {location_name}: ({lat}, {lon})")
            try:
                nearest_node = ox.nearest_nodes(self.graph, lon, lat)
                print(f"Nearest node for {location_name}: {nearest_node}")
                return lat, lon, nearest_node
            except Exception as e:
                msg = str(e)
                print(f"Warning finding nearest node: {msg}")
                if "scikit-learn" in msg or "scikit_learn" in msg:
                    return lat, lon, None
                return None
        except Exception as e:
            print(f"Error getting coordinates: {e}")
            return None

    def sav_map(self):
        file_path = f"{self.place_name}_map.graphml"
        try:
            ox.save_graphml(self.graph, file_path)
            print(f"Map saved successfully to {file_path}.")
            return True, file_path
        except Exception as e:
            print(f"Error saving map: {e}")
            return False, f"Error saving map: {e}"

    def get_frontend_geojson(self, graph_path=None, edges_only=True):
        """Return GeoJSON dict suitable for a frontend map viewer.

        If `graph_path` is provided, load the graph from that GraphML file;
        otherwise use the engine's loaded `self.graph`.
        When `edges_only` is True, returns only the edges FeatureCollection.
        Returns (True, geojson_dict) on success or (False, error_message) on failure.
        """
        try:
            G = self.graph if graph_path is None else ox.load_graphml(graph_path)
            if G is None:
                return False, "No graph available to export"
            nodes_gdf, edges_gdf = ox.graph_to_gdfs(G)
            if edges_only:
                geojson_str = edges_gdf.to_json()
                return True, json.loads(geojson_str)
            nodes_json = json.loads(nodes_gdf.to_json())
            edges_json = json.loads(edges_gdf.to_json())
            features = nodes_json.get("features", []) + edges_json.get("features", [])
            collection = {"type": "FeatureCollection", "features": features}
            return True, collection
        except Exception as e:
            return False, f"Error exporting frontend geojson: {e}"


