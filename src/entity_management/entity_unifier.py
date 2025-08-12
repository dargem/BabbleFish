from .entity_types.unified_entity import UnifiedEntity
import networkx as nx
from itertools import combinations

class EntityUnifier():

    @staticmethod
    def process_entities(self, entities_dic):
        
        unified_entity_dic = {}

        graph = nx.graph()
        for entity in entities_dic:
            graph.add_node(entity)

        for name1, name2 in combinations(graph.nodes(), 2):
            if self._are_related(name1,name2):
                graph.add_edge(name1,name2)


        for entity_name in entities_dic:
            if entity_name not in unified_entity_dic:
                unified_entity_dic[entity_name] = UnifiedEntity(entity_name)
            pass

    def _are_related(name1, name2):
        if name1 == "" or name2 == "": 
            return False
        
        return (
            name1.lower() == name2.lower()
            or name1.lower() in name2.lower()
        )


        



