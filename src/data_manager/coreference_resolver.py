from lingua import Language
import os
import subprocess
import tempfile
import json
import sys
import warnings
from typing import Dict, List, Any

# Suppress known warnings from CorPipe dependencies
warnings.filterwarnings("ignore", category=UserWarning, module="tensorflow_addons")
warnings.filterwarnings("ignore", category=FutureWarning, module="huggingface_hub") 
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
warnings.filterwarnings("ignore", category=UserWarning, module="keras")

class CoreferenceResolver():
    '''
    Resolves coreferences using CorPipe with cached model for performance
    '''
    # CorPipe supports multilingual coreference resolution
    available_models = {
        Language.ENGLISH,
        Language.CHINESE,
        # Language.JAPANESE,  # Add when confirmed CorPipe supports it
        # Language.KOREAN,    # Add when confirmed CorPipe supports it
    }

    # CorPipe configuration
    CORPIPE_DIR = "/Users/td/Documents/GitHub/FinetunedMTLBot/crac2024-corpipe"
    CORPIPE_PYTHON_ENV = "/Users/td/Documents/GitHub/FinetunedMTLBot/.venv_corpipe/bin/python"

    @staticmethod
    def model_available(language: Language):
        """Check if coreference resolution is available for the given language."""
        model_path = os.path.join(CoreferenceResolver.CORPIPE_DIR, "corpipe24-corefud1.2-240906/model.h5")
        return language in CoreferenceResolver.available_models and os.path.exists(model_path)
    
    @staticmethod
    def resolve_coreferences_large_text(text: str, language: Language, chunk_size: int = 5000) -> str:
        """
        Resolve coreferences for a large text by processing it in a single batch.
        This automatically splits very large texts into manageable chunks while
        still processing them all in one model loading session.
        
        Args:
            text: Large input text to process
            language: Language of the text
            chunk_size: Maximum characters per chunk (default 5000)
            
        Returns:
            Text with resolved coreferences
        """
        if not text or len(text) <= chunk_size:
            # Small text, use regular method
            return CoreferenceResolver.resolve_coreferences(text, language)
        
        # Split large text into chunks at sentence boundaries
        chunks = []
        # Clean up the text first - remove extra whitespace and normalize
        clean_text = ' '.join(text.split())  # This removes all extra whitespace including newlines
        sentences = clean_text.replace('!', '.').replace('?', '.').split('. ')
        
        current_chunk = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add sentence to current chunk if it fits
            if len(current_chunk) + len(sentence) + 2 <= chunk_size:  # +2 for ". "
                if current_chunk:
                    current_chunk += ". " + sentence
                else:
                    current_chunk = sentence
            else:
                # Current chunk is full, start a new one
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence
        
        # Add the last chunk
        if current_chunk:
            chunks.append(current_chunk)
        
        # Process all chunks in a single batch
        resolved_chunks = CoreferenceResolver.resolve_coreferences_batch(chunks, language)
        
        # Join the resolved chunks back together
        return ". ".join(resolved_chunks)

    @staticmethod
    def resolve_coreferences_batch(texts: List[str], language: Language) -> List[str]:
        """
        Resolve coreferences for multiple texts in a single model loading session.
        This is much more efficient than calling resolve_coreferences multiple times.
        
        Args:
            texts: List of input texts to process
            language: Language of the texts
            
        Returns:
            List of texts with resolved coreferences, same order as input
        """
        if not CoreferenceResolver.model_available(language):
            return texts
        
        if not texts:
            return []
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create a single large CoNLL-U file with all texts
                combined_conllu_lines = []
                text_boundaries = []  # Track where each text starts/ends
                sent_id_counter = 1
                
                for text_idx, text in enumerate(texts):
                    start_sent_id = sent_id_counter
                    
                    # Clean up text - remove extra whitespace and normalize
                    clean_text = ' '.join(text.split())
                    
                    # Convert text to CoNLL-U format
                    sentences = clean_text.replace('!', '.').replace('?', '.').split('. ')
                    
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                            
                        # Add period if missing at end
                        if not sentence.endswith('.'):
                            sentence += '.'
                            
                        combined_conllu_lines.append(f"# sent_id = {sent_id_counter}")
                        combined_conllu_lines.append(f"# text = {sentence}")
                        
                        # Simple tokenization
                        import re
                        words = re.findall(r'\b\w+\b|[^\w\s]', sentence)
                        
                        for word_id, word in enumerate(words, 1):
                            # Guess basic POS tags
                            pos = "NOUN"
                            if word.lower() in ['the', 'a', 'an']:
                                pos = "DET"
                            elif word.lower() in ['he', 'she', 'it', 'they', 'i', 'you', 'we']:
                                pos = "PRON"
                            elif word.lower() in ['is', 'was', 'are', 'were', 'be', 'been']:
                                pos = "AUX"
                            elif word.lower() in ['went', 'go', 'come', 'came', 'said', 'bought']:
                                pos = "VERB"
                            elif word[0].isupper() and word.isalpha():
                                pos = "PROPN"
                            elif word in ['.', ',', '!', '?']:
                                pos = "PUNCT"
                            
                            # Basic dependency structure
                            head = "0" if word_id == 1 or pos == "VERB" else "1"
                            deprel = "root" if head == "0" else "dep"
                            
                            combined_conllu_lines.append(f"{word_id}\t{word}\t{word.lower()}\t{pos}\t_\t_\t{head}\t{deprel}\t_\t_")
                        
                        combined_conllu_lines.append("")  # Empty line between sentences
                        sent_id_counter += 1
                    
                    end_sent_id = sent_id_counter - 1
                    text_boundaries.append((start_sent_id, end_sent_id))
                
                # Write combined CoNLL-U file
                input_file = os.path.join(temp_dir, "batch_input.conllu")
                combined_content = "\n".join(combined_conllu_lines)
                if not combined_content.endswith("\n\n"):
                    if combined_content.endswith("\n"):
                        combined_content += "\n"
                    else:
                        combined_content += "\n\n"
                
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(combined_content)
                
                # Process the batch file
                success, output_data = CoreferenceResolver._run_corpipe(input_file)
                
                if success and output_data:
                    # Parse the results and split back into individual texts
                    results = []
                    for text_idx, (start_sent, end_sent) in enumerate(text_boundaries):
                        original_text = texts[text_idx]
                        # Filter output_data for this text's sentence range
                        filtered_data = CoreferenceResolver._filter_output_for_sentences(
                            output_data, start_sent, end_sent
                        )
                        resolved_text = CoreferenceResolver._resolve_pronouns_from_data(
                            original_text, filtered_data
                        )
                        results.append(resolved_text)
                    
                    return results
                else:
                    print(f"Batch CorPipe processing failed for language {language}, returning original texts")
                    return texts
                    
        except Exception as e:
            print(f"Error in batch coreference resolution: {e}")
            return texts
    
    @staticmethod
    def _filter_output_for_sentences(output_data: Dict[str, Any], start_sent: int, end_sent: int) -> Dict[str, Any]:
        """Filter output data to only include sentences in the specified range."""
        filtered_data = {}
        
        # Filter sentences and mentions based on sentence ID range
        for key, value in output_data.items():
            if key == 'sentences':
                if isinstance(value, list):
                    filtered_data[key] = [sent for sent in value if start_sent <= sent.get('sent_id', 0) <= end_sent]
                else:
                    filtered_data[key] = value
            elif key == 'mentions':
                if isinstance(value, list):
                    filtered_data[key] = [mention for mention in value 
                                        if start_sent <= mention.get('sent_id', 0) <= end_sent]
                else:
                    filtered_data[key] = value
            else:
                filtered_data[key] = value
        
        return filtered_data

    @staticmethod
    def resolve_coreferences(text: str, language: Language) -> str:
        """
        Resolve coreferences in the given text using CorPipe.
        
        Args:
            text: Input text to process
            language: Language of the text
            
        Returns:
            Text with resolved coreferences, or original text if resolution fails
        """
        if not CoreferenceResolver.model_available(language):
            return text
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                # Create input CoNLL-U file
                input_file = os.path.join(temp_dir, "input.conllu")
                
                # Convert text to basic CoNLL-U format
                conllu_content = CoreferenceResolver._text_to_conllu(text)
                
                with open(input_file, 'w', encoding='utf-8') as f:
                    f.write(conllu_content)
                
                # Run CorPipe
                success, output_data = CoreferenceResolver._run_corpipe(input_file)
                
                if success and output_data:
                    # Parse coreference information and resolve pronouns
                    return CoreferenceResolver._resolve_pronouns_from_data(text, output_data)
                else:
                    print(f"CorPipe processing failed for language {language}, returning original text")
                    return text
                    
        except Exception as e:
            print(f"Error in coreference resolution: {e}")
            return text
    
    @staticmethod
    def _text_to_conllu(text: str) -> str:
        """
        Convert plain text to basic CoNLL-U format.
        This is a simplified version since the text will be pre-filtered.
        """
        lines = []
        sentences = text.replace('!', '.').replace('?', '.').split('. ')
        
        for sent_id, sentence in enumerate(sentences, 1):
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Add period if missing at end
            if not sentence.endswith('.'):
                sentence += '.'
                
            lines.append(f"# sent_id = {sent_id}")
            lines.append(f"# text = {sentence}")
            
            # Simple tokenization
            import re
            words = re.findall(r'\b\w+\b|[^\w\s]', sentence)
            
            for word_id, word in enumerate(words, 1):
                # Guess basic POS tags
                pos = "NOUN"
                if word.lower() in ['the', 'a', 'an']:
                    pos = "DET"
                elif word.lower() in ['he', 'she', 'it', 'they', 'i', 'you', 'we']:
                    pos = "PRON"
                elif word.lower() in ['is', 'was', 'are', 'were', 'be', 'been']:
                    pos = "AUX"
                elif word.lower() in ['went', 'go', 'come', 'came', 'said', 'bought']:
                    pos = "VERB"
                elif word[0].isupper() and word.isalpha():
                    pos = "PROPN"
                elif word in ['.', ',', '!', '?']:
                    pos = "PUNCT"
                
                # Basic dependency structure
                head = "0" if word_id == 1 or pos == "VERB" else "1"
                deprel = "root" if head == "0" else "dep"
                
                lines.append(f"{word_id}\t{word}\t{word.lower()}\t{pos}\t_\t_\t{head}\t{deprel}\t_\t_")
            
            lines.append("")  # Empty line between sentences
        
        # Ensure the file ends properly
        result = "\n".join(lines)
        if not result.endswith("\n\n"):
            if result.endswith("\n"):
                result += "\n"
            else:
                result += "\n\n"
        
        return result
    
    @staticmethod
    def _run_corpipe(input_file: str) -> tuple[bool, Dict[str, Any]]:
        """
        Run CorPipe on the input file.
        """
        try:
            cmd = [
                CoreferenceResolver.CORPIPE_PYTHON_ENV,
                "corpipe24.py",
                "--test", input_file
            ]
            
            result = subprocess.run(
                cmd,
                cwd=CoreferenceResolver.CORPIPE_DIR,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout for non-cached
            )
            
            if result.returncode == 0:
                # Look for output in the model directory
                model_dir = os.path.join(CoreferenceResolver.CORPIPE_DIR, "corpipe24-corefud1.2-240906")
                if os.path.exists(model_dir):
                    output_files = [f for f in os.listdir(model_dir) if f.endswith('.conllu')]
                    if output_files:
                        latest_file = max([os.path.join(model_dir, f) for f in output_files], 
                                        key=os.path.getmtime)
                        return True, CoreferenceResolver._parse_corpipe_output(latest_file)
            
            return False, {}
            
        except Exception as e:
            print(f"CorPipe execution failed: {e}")
            return False, {}
    
    @staticmethod
    def _parse_corpipe_output(output_file: str) -> Dict[str, Any]:
        """Parse CorPipe output and extract coreference chains."""
        chains = []
        entities = {}
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse CoNLL-U format for Entity annotations
            for line in content.split('\n'):
                line = line.strip()
                if line and not line.startswith('#') and '\t' in line:
                    parts = line.split('\t')
                    if len(parts) >= 10 and 'Entity=' in parts[9]:
                        # Extract entity information from MISC field
                        misc_field = parts[9]
                        word = parts[1]
                        
                        for item in misc_field.split('|'):
                            if item.startswith('Entity='):
                                entity_id = item.replace('Entity=', '').strip('()')
                                if entity_id not in entities:
                                    entities[entity_id] = []
                                entities[entity_id].append(word)
            
            # Convert to chains format
            chains = list(entities.values())
            
        except Exception as e:
            print(f"Error parsing CorPipe output: {e}")
        
        return {"chains": chains, "entities": entities}
    
    @staticmethod
    def _resolve_pronouns_from_data(text: str, coreference_data: Dict[str, Any]) -> str:
        """
        Resolve pronouns in text based on coreference chains.
        """
        resolved_text = text
        chains = coreference_data.get("chains", [])
        
        for chain in chains:
            if len(chain) > 1:
                # Find the main entity (first proper noun in the chain)
                main_entity = None
                for mention in chain:
                    if mention[0].isupper() and mention.lower() not in ['he', 'she', 'it', 'they', 'him', 'her', 'them']:
                        main_entity = mention
                        break
                
                if main_entity:
                    # Replace pronouns with the main entity
                    pronouns = ['he', 'she', 'it', 'they', 'him', 'her', 'them']
                    for mention in chain:
                        if mention.lower() in pronouns:
                            # Simple replacement
                            resolved_text = resolved_text.replace(mention, main_entity, 1)
        
        return resolved_text