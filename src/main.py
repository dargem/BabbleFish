import logging
import sys
import os
import json
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Optional, Any

logging.basicConfig(
    stream=sys.stdout,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from src.data_manager.file_manager import FileManager
from src.entity_management.find_entities import OccurrenceFinder
from src.rag_database.base_rag import RAGDatabase
from src.entity_management.entity_manager import EntityManager


@dataclass
class PipelineConfig:
    """Configuration for the translation pipeline."""
    source_folder: str
    start_idx: int = 0
    end_idx: int = 1
    chapter_idx: int = 10
    use_extra_gemini_ner: bool = True
    
    @classmethod
    def create_default(cls, project_root: str) -> 'PipelineConfig':
        """Create default configuration with project-relative paths."""
        return cls(
            source_folder=os.path.join(project_root, "data", "raw", "lotm_files")
        )


class TranslationPipeline:
    """
    A well-structured translation pipeline that processes text files through
    entity extraction, glossary building, and text processing stages.
    """
    
    def __init__(self, config: PipelineConfig):
        self.config = config
        self.file_manager: Optional[FileManager] = None
        self.rag_database: Optional[RAGDatabase] = None
        self.entity_finder: Optional[OccurrenceFinder] = None
        self.entity_matcher: Optional[EntityManager] = None
        
        # Pipeline state
        self.file_paths: List[str] = []
        self.entities: List[str] = []
        self.glossary: Optional[Dict[str, Any]] = None
        self.chapter_keyed_chunks: Optional[Dict[int, List[str]]] = None
        
        logger.info(f"TranslationPipeline initialized with config: {config}")
    
    async def run(self) -> Dict[int, List[str]]:
        """
        Execute the complete translation pipeline.
        
        Returns:
            Processed text chunks keyed by chapter index
        """
        try:
            logger.info("Starting translation pipeline execution")
            
            # Execute pipeline stages in order
            await self._stage_1_manage_files()
            await self._stage_2_initialize_rag()
            await self._stage_3_extract_entities()
            await self._stage_4_build_glossary()
            await self._stage_5_create_entity_matches()
            
            logger.info("Translation pipeline completed successfully")
            return self.chapter_keyed_chunks
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            raise
    
    async def _stage_1_manage_files(self) -> None:
        """
        Requires:
        - source_folder (directory contains input files)
        Produces: 
        - chapter_dic (chapters hashed by chapter index)
        - lemmatised_chapter_dic (lemmatised chapters hashed by chapter index)
        - language (lingua language enum for detected language)
        """
        logger.info("Stage 1: Discovering files, indexing and lemmatising text")
        
        file_manager = FileManager(self.config.source_folder)

        self.chapter_dic = file_manager.chapter_dic
        self.lemmatized_chapter_dic = file_manager.lemmatized_chapter_dic
        self.language = file_manager.language

        if not self.chapter_dic:
            raise RuntimeError("chapter_dic non existent, likely no chapters inputted")
        
        logger.info(f"Discovered and lemmatised files")
    
    async def _stage_2_extract_entities(self) -> None:
        #TODO add loading entities
        '''
        Requires:
        - chapter_dic (chapters hashed by chapter index)
        - lemmatised_chapter_dic (lemmatised chapters hashed by chapter index)
        - language (lingua language enum for detected language)
        Outputs:
        - entities (list of unified entity objects)
        '''
        entity_manager = EntityManager(self.chapter_dic, self.lemmatized_chapter_dic, self.language, self.config.use_extra_gemini_ner)




    async def _stage_2_initialize_rag(self) -> None:
        """
        Stage 2: Create and initialize RAG database.
        Requires: 
        - 
        """
        logger.info("Stage 2: Initializing RAG database")
        
        if not self.file_paths:
            raise RuntimeError("Files must be discovered before initializing RAG")
        
        self.rag_database = await RAGDatabase.create(
            self.file_paths, 
            start_idx=self.config.start_idx
        )
        
        # Retrieve initial chunks for later processing
        self.chapter_keyed_chunks = self.rag_database.retrieve_chunks()
        logger.info("RAG database initialized successfully")
    
    async def _stage_3_extract_entities(self) -> None:
        """Stage 3: Extract named entities from text."""
        logger.info("Stage 3: Extracting entities")
        
        if not self.file_paths:
            raise RuntimeError("Files must be discovered before extracting entities")
        

        '''
        self.entity_finder = Entity_Finder(self.file_paths)
        self.entities = self.entity_finder.find_entities(
            use_extra_gemini_ner=self.config.use_extra_gemini_ner
        )
        '''
        logger.info(f"Extracted {len(self.entities)} entities")
    
    async def _stage_4_build_glossary(self) -> None:
        """Stage 4: Build glossary from extracted entities."""
        logger.info("Stage 4: Building glossary")
        
        if not self.entities or not self.rag_database:
            raise RuntimeError("Entities and RAG database must be available before building glossary")
        
        # Build term entries using RAG
        glossary_data = self.rag_database.build_JSON_term_entries(
            self.entities, 
            chapter_idx=self.config.chapter_idx
        )
        
        # Save glossary to file
        self.file_manager.build_glossary(glossary_data)
        
        # Load glossary for further processing
        self.glossary = self.file_manager.get_glossary()
        logger.info("Glossary built and saved successfully")
    
    async def _stage_5_create_entity_matches(self) -> None:
        """Stage 5: Create entity matches and process text."""
        logger.info("Stage 5: Creating entity matches")
        
        if not self.glossary or not self.chapter_keyed_chunks:
            raise RuntimeError("Glossary and chunks must be available before matching entities")
        
        # Initialize entity matcher
        self.entity_matcher = Entity_Matcher(self.glossary, self.chapter_keyed_chunks)
        
        # Get processed chunks with entity matches
        self.chapter_keyed_chunks = self.entity_matcher.get_matches()
        
        logger.info("Entity matching completed")
    
    def get_pipeline_state(self) -> Dict[str, Any]:
        """Get current pipeline state for debugging/monitoring."""
        return {
            "config": self.config,
            "files_discovered": len(self.file_paths) if self.file_paths else 0,
            "entities_extracted": len(self.entities) if self.entities else 0,
            "glossary_entries": len(self.glossary) if self.glossary else 0,
            "chapters_processed": len(self.chapter_keyed_chunks) if self.chapter_keyed_chunks else 0,
            "rag_initialized": self.rag_database is not None,
            "entity_matcher_ready": self.entity_matcher is not None
        }
    
    def save_results(self, output_path: Optional[str] = None) -> None:
        """Save pipeline results to file."""
        if not self.chapter_keyed_chunks:
            logger.warning("No results to save")
            return
        
        if output_path is None:
            output_path = os.path.join(
                os.path.dirname(self.config.source_folder),
                "processed",
                "pipeline_results.json"
            )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.chapter_keyed_chunks, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Results saved to {output_path}")
    





async def main():
    """
    Main entry point using the new TranslationPipeline architecture.
    """
    try:
        # Get project root dynamically
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..'))
        
        # Create configuration
        config = PipelineConfig.create_default(project_root)
        logger.info(f"Initialized with config: {config}")
        
        # Create and run pipeline
        pipeline = TranslationPipeline(config)
        
        # Execute pipeline
        results = await pipeline.run()
        
        # Display results
        logger.info("Pipeline execution completed. Processing results...")
        for chapter_idx, paragraphs in results.items():
            print(f"\n=== Chapter {chapter_idx} ===")
            for i, paragraph in enumerate(paragraphs[:3]):  # Show first 3 paragraphs
                print(f"Paragraph {i+1}: {paragraph[:100]}...")
            if len(paragraphs) > 3:
                print(f"... and {len(paragraphs) - 3} more paragraphs")
        
        # Save results
        pipeline.save_results()
        
        # Display pipeline state
        state = pipeline.get_pipeline_state()
        print(f"\n=== Pipeline Summary ===")
        print(f"Files processed: {state['files_discovered']}")
        print(f"Entities extracted: {state['entities_extracted']}")
        print(f"Glossary entries: {state['glossary_entries']}")
        print(f"Chapters processed: {state['chapters_processed']}")
        
        return results
        
    except Exception as e:
        logger.error(f"Main execution failed: {e}", exc_info=True)
        raise


# Legacy main function preserved for reference (commented out)
async def legacy_main():
    """
    Original main function preserved for reference.
    This shows the old monolithic approach that has been refactored.
    """
    # Get project root dynamically
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    FOLDER_SOURCE = os.path.join(project_root, "data", "raw", "lotm_files")

    print("finding file paths")

    # First stage gets files
    file_manager = FileManager(FOLDER_SOURCE)
    start_idx = 0
    end_idx = 1
    file_paths = file_manager.get_files(start_idx=start_idx, end_idx=end_idx)
    
    # Second stage construct RAG database (await async create)
    print("creating database")
    rag_database = await RAGDatabase.create(file_paths, start_idx=start_idx)
    chapter_keyed_list = rag_database.retrieve_chunks()
    
    # Third stage get entities
    print("finding entities")
    entity_finder = OccurrenceFinder(file_paths)
    entities = entity_finder.find_occurrence(use_extra_gemini_ner=True)
    print(entities)
    
    # engage in entity reunification

    # Fourth stage use RAG to find good localisations for entry
    print("building entity entries")
    data = rag_database.build_JSON_term_entries(entities, chapter_idx=10)

    # Fifth stage build database
    print("create glossary")
    file_manager.build_glossary(data)
    
    # Retrieve semantically split input, indexed by chapter_idx and paragraph
    
    # Sixth stage replace/put markers in OG text with translated names
    
    print("inserting markers")
    glossary = file_manager.get_glossary()
    chapter_keyed_list = rag_database.retrieve_chunks() # this keys chapter_idx to a list of ordered chunks

    entity_matcher = Entity_Matcher(glossary, chapter_keyed_list)
    chapter_keyed_list = entity_matcher.get_matches()
    for key in chapter_keyed_list:
        for para in chapter_keyed_list[key]:
            print(para)

    
    '''
    entities = [entry["entity"] for entry in glossary]
    tupled_entities = [(entry["entity"],entry["description"]) for entry in glossary]

    entity_chapter_presence = { entity: [] for entity in entities } # marks chapters an entity has been found in

    # 6.1 Do an exact match through the files
    entity_chapter_presence_temp = file_manager.get_entity_chapter_presence(entities, start_idx, end_idx)
    for entity in entity_chapter_presence_temp:
        entity_chapter_presence[entity] = entity_chapter_presence_temp[entity] # merges lists together
    # 6.2 Do a lemmatised match through the files, can use Spacy


    # 6.3 Do a semantic match through the files using RAG
    rag_database.check_tupled_term_relevance(tupled_entities, start_idx = start_idx, end_idx = end_idx)
    '''
    # Seventh stage, llm to create structured out original in form of semantics

    # Eighth stage, translate using llm 

    # Further stages here...


if __name__ == "__main__":
    asyncio.run(main())
