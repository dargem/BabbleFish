# graph_db.py
from neo4j import GraphDatabase
from typing import List, Dict, Optional

class GraphDB:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def add_entity(self, name: str, description: str, term_type: str):
        """Create or update an Entity node."""
        query = """
        MERGE (e:Entity {name: $name})
        ON CREATE SET e.description = $description, e.term_type = $term_type
        ON MATCH SET e.description = coalesce(e.description, $description),
                      e.term_type = coalesce(e.term_type, $term_type)
        """
        with self.driver.session() as session:
            session.run(query, name=name, description=description, term_type=term_type)

    def add_relationship(self, source: str, target: str, rel_type: str,
                         chapter_start: int, confidence: float,
                         chapter_end: Optional[int] = None):
        """Create or update a relationship between entities."""
        query = """
        MATCH (a:Entity {name: $source})
        MATCH (b:Entity {name: $target})
        MERGE (a)-[r:RELATED_TO {type: $rel_type}]->(b)
        ON CREATE SET r.chapter_start = $chapter_start,
                      r.chapter_end = $chapter_end,
                      r.confidence = $confidence
        ON MATCH SET r.chapter_start = least(r.chapter_start, $chapter_start),
                      r.chapter_end = coalesce(r.chapter_end, $chapter_end),
                      r.confidence = greatest(r.confidence, $confidence)
        """
        with self.driver.session() as session:
            session.run(query, source=source, target=target, rel_type=rel_type,
                        chapter_start=chapter_start, chapter_end=chapter_end,
                        confidence=confidence)

    # ------------------------------
    # Query for LLM Context
    # ------------------------------

    def get_context(self, entities: List[str], chapter: int, min_confidence: float,
                    hops: int = 2) -> List[Dict]:
        """Retrieve relevant entities + relationships for given entities."""
        query = f"""
        MATCH (e:Entity)
        WHERE e.name IN $entities
        WITH e
        MATCH path = (e)-[r:RELATED_TO*1..{hops}]-(related:Entity)
        WHERE ALL(rel IN r WHERE 
            rel.chapter_start <= $chapter
            AND (rel.chapter_end IS NULL OR rel.chapter_end >= $chapter)
            AND rel.confidence >= $min_confidence
        )
        RETURN DISTINCT related.name AS entity_name,
               related.description AS entity_description,
               [rel IN relationships(path) | {{
                   type: rel.type,
                   confidence: rel.confidence,
                   since: rel.chapter_start
               }}] AS relationships
        """
        with self.driver.session() as session:
            result = session.run(query, entities=entities,
                                 chapter=chapter, min_confidence=min_confidence)
            return [dict(record) for record in result]

