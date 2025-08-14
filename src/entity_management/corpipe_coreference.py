#!/usr/bin/env python3
"""
CorPipe Coreference Resolution Integration
Wrapper for using CorPipe coreference resolution in the translation pipeline.
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Any


class CorPipeCoreference:
    """Wrapper for CorPipe coreference resolution."""
    # Example usage
if __name__ == "__main__":
    import argparse
    import json
    
    parser = argparse.ArgumentParser(description='CorPipe Coreference Resolution Wrapper')
    parser.add_argument('--text', type=str, help='Text to process')
    parser.add_argument('--file', type=str, help='File containing text to process')
    parser.add_argument('--output', type=str, help='Output file for results (JSON)')
    parser.add_argument('--model', type=str, help='Path to CorPipe model')
    parser.add_argument('--language', type=str, default='en', help='Language code')
    
    args = parser.parse_args()
    
    if len(sys.argv) == 1:
        # Default test if no args provided
        resolver = CorPipeCoreference()
        
        test_text = "Maria went to visit her grandmother because she had baked a fresh apple pie. When Maria arrived, she noticed that the pie was still warm, and it reminded her of the ones she used to eat as a child. Later, they decided to invite John over, but he said he couldn't come because his car had broken down."
        result = resolver.resolve_coreferences(test_text)
        print(f"Coreference result: {json.dumps(result, indent=2)}")
    else:
        # Command line usage
        resolver = CorPipeCoreference(args.model) if args.model else CorPipeCoreference()
        
        if args.text:
            text = args.text
        elif args.file:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            print("Error: Must provide either --text or --file")
            sys.exit(1)
        
        result = resolver.resolve_coreferences(text, args.language)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print(json.dumps(result, indent=2))f __init__(self, model_path: str = None):
        """
        Initialize CorPipe coreference resolver.
        
        Args:
            model_path: Path to the CorPipe model (default uses the downloaded model)
        """
        # Default to the model you downloaded
        if model_path is None:
            self.model_path = "/Users/td/Documents/GitHub/FinetunedMTLBot/crac2024-corpipe/corpipe24-corefud1.2-240906/model.h5"
        else:
            self.model_path = model_path
            
        self.corpipe_dir = "/Users/td/Documents/GitHub/FinetunedMTLBot/crac2024-corpipe"
        self.python_env = "/Users/td/Documents/GitHub/FinetunedMTLBot/.venv_corpipe/bin/python"
        
        # Verify model exists
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"CorPipe model not found at: {self.model_path}")
    
    def resolve_coreferences(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Resolve coreferences in the given text.
        
        Args:
            text: Input text to process
            language: Language code (en, cs, etc.)
            
        Returns:
            Dictionary containing coreference information
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create input file
            input_file = os.path.join(temp_dir, "input.conllu")
            output_file = os.path.join(temp_dir, "output.conllu")
            
            # Convert text to CoNLL-U format
            conllu_content = self._text_to_conllu(text, language)
            
            with open(input_file, 'w', encoding='utf-8') as f:
                f.write(conllu_content)
            
            # Run CorPipe
            success = self.run_corpipe_command(input_file, output_file)
            
            if success and os.path.exists(output_file):
                # Parse the output
                return self._parse_corpipe_output(output_file, text)
            else:
                print("CorPipe processing failed, returning basic analysis")
                return self._basic_coreference_analysis(text)
    
    def _text_to_conllu(self, text: str, language: str = "en") -> str:
        """
        Convert plain text to CoNLL-U format for CorPipe processing.
        Simplified version for subprocess usage with pre-filtered input.
        """
        return self._basic_text_to_conllu(text, language)
    
    def _basic_text_to_conllu(self, text: str, language: str = "en") -> str:
        """
        Basic text to CoNLL-U conversion.
        """
        lines = []
        sentences = text.replace('!', '.').replace('?', '.').split('. ')
        
        for sent_id, sentence in enumerate(sentences, 1):
            sentence = sentence.strip()
            if not sentence:
                continue
                
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
                
                # Basic dependency structure (just attach everything to root or previous word)
                head = "0" if word_id == 1 or pos == "VERB" else "1"
                deprel = "root" if head == "0" else "dep"
                
                lines.append(f"{word_id}\t{word}\t{word.lower()}\t{pos}\t_\t_\t{head}\t{deprel}\t_\t_")
            
            lines.append("")  # Empty line between sentences
        
        return "\n".join(lines)
    
    def run_corpipe_command(self, input_file: str, output_file: str) -> bool:
        """
        Run CorPipe on a CoNLL-U file.
        
        Args:
            input_file: Path to input CoNLL-U file
            output_file: Path to output file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cmd = [
                self.python_env,
                "corpipe24.py",
                "--load", self.model_path,
                "--test", input_file
            ]
            
            result = subprocess.run(
                cmd,
                cwd=self.corpipe_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                # CorPipe outputs to a specific location, we need to find it
                # Check for output files in the logs directory
                log_dir = os.path.join(self.corpipe_dir, "logs")
                if os.path.exists(log_dir):
                    # Look for the most recent output file
                    output_files = [f for f in os.listdir(log_dir) if f.endswith('.conllu')]
                    if output_files:
                        latest_file = max([os.path.join(log_dir, f) for f in output_files], 
                                        key=os.path.getmtime)
                        # Copy to our expected output location
                        import shutil
                        shutil.copy2(latest_file, output_file)
                        return True
            
            print(f"CorPipe stderr: {result.stderr}")
            print(f"CorPipe stdout: {result.stdout}")
            return False
            
        except (subprocess.TimeoutExpired, subprocess.SubprocessError) as e:
            print(f"CorPipe execution failed: {e}")
            return False
    
    def _parse_corpipe_output(self, output_file: str, original_text: str) -> Dict[str, Any]:
        """
        Parse CorPipe output and extract coreference information.
        
        Args:
            output_file: Path to CorPipe output file
            original_text: Original input text
            
        Returns:
            Dictionary containing coreference information
        """
        entities = []
        mentions = []
        chains = {}
        
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse CoNLL-U format with coreference annotations
            current_sentence = []
            sentence_offset = 0
            
            for line in content.split('\n'):
                line = line.strip()
                
                if line.startswith('#'):
                    continue
                elif not line:  # Empty line = end of sentence
                    if current_sentence:
                        sentence_offset += len(' '.join([token['form'] for token in current_sentence])) + 1
                        current_sentence = []
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 10:
                    token_info = {
                        'id': parts[0],
                        'form': parts[1],
                        'lemma': parts[2],
                        'misc': parts[9] if len(parts) > 9 else ''
                    }
                    
                    # Look for Entity annotations in MISC field
                    if 'Entity=' in token_info['misc']:
                        entity_info = self._extract_entity_info(token_info['misc'])
                        if entity_info:
                            mentions.append({
                                'text': token_info['form'],
                                'start': sentence_offset + len(' '.join([t['form'] for t in current_sentence])),
                                'end': sentence_offset + len(' '.join([t['form'] for t in current_sentence])) + len(token_info['form']),
                                'entity_id': entity_info['entity_id'],
                                'mention_id': entity_info.get('mention_id')
                            })
                    
                    current_sentence.append(token_info)
            
            # Group mentions into coreference chains
            entity_groups = {}
            for mention in mentions:
                eid = mention['entity_id']
                if eid not in entity_groups:
                    entity_groups[eid] = []
                entity_groups[eid].append(mention)
            
            # Create chains
            chains = list(entity_groups.values())
            
            # Create entity list
            entities = [{'id': eid, 'mentions': group} for eid, group in entity_groups.items()]
            
        except Exception as e:
            print(f"Error parsing CorPipe output: {e}")
            return self._basic_coreference_analysis(original_text)
        
        return {
            "entities": entities,
            "mentions": mentions,
            "chains": chains,
            "resolved_text": self._resolve_pronouns(original_text, chains)
        }
    
    def _extract_entity_info(self, misc_field: str) -> Dict[str, Any]:
        """Extract entity information from MISC field."""
        entity_info = {}
        
        for item in misc_field.split('|'):
            if item.startswith('Entity='):
                # Format might be like Entity=(1-Maria-1) or Entity=1
                entity_part = item.replace('Entity=', '')
                if '(' in entity_part and ')' in entity_part:
                    # Parse (mention_id-entity_id-span_id) format
                    parts = entity_part.strip('()').split('-')
                    if len(parts) >= 2:
                        entity_info['mention_id'] = parts[0]
                        entity_info['entity_id'] = parts[1]
                else:
                    entity_info['entity_id'] = entity_part
        
        return entity_info
    
    def _basic_coreference_analysis(self, text: str) -> Dict[str, Any]:
        """
        Provide basic coreference analysis using simple heuristics.
        This is a fallback when CorPipe fails.
        """
        import re
        
        # Simple pronoun detection
        pronouns = ['he', 'she', 'it', 'they', 'him', 'her', 'them', 'his', 'hers', 'its', 'their']
        proper_nouns = re.findall(r'\b[A-Z][a-z]+\b', text)
        
        mentions = []
        entities = []
        
        # Find pronouns
        for pronoun in pronouns:
            for match in re.finditer(r'\b' + re.escape(pronoun) + r'\b', text, re.IGNORECASE):
                mentions.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'pronoun',
                    'entity_id': f'unknown_{len(mentions)}'
                })
        
        # Find proper nouns (potential entities)
        for i, noun in enumerate(proper_nouns):
            for match in re.finditer(r'\b' + re.escape(noun) + r'\b', text):
                mentions.append({
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'type': 'proper_noun',
                    'entity_id': f'entity_{i}'
                })
                
                entities.append({
                    'id': f'entity_{i}',
                    'name': noun,
                    'type': 'PERSON'  # Assumption
                })
        
        # Simple chains (just group by similar text for now)
        chains = []
        for entity in entities:
            entity_mentions = [m for m in mentions if m.get('entity_id') == entity['id']]
            if entity_mentions:
                chains.append(entity_mentions)
        
        return {
            "entities": entities,
            "mentions": mentions,
            "chains": chains,
            "resolved_text": text,
            "note": "Basic analysis used - CorPipe processing failed"
        }
    
    def _resolve_pronouns(self, text: str, chains: List[List[Dict]]) -> str:
        """
        Simple pronoun resolution based on coreference chains.
        """
        resolved_text = text
        
        for chain in chains:
            if len(chain) > 1:
                # Find the first proper noun or specific reference in the chain
                main_entity = None
                for mention in chain:
                    if mention['text'][0].isupper() and mention['text'].lower() not in ['he', 'she', 'it', 'they', 'him', 'her', 'them']:
                        main_entity = mention['text']
                        break
                
                if main_entity:
                    # Replace pronouns with the main entity name
                    for mention in chain:
                        if mention['text'].lower() in ['he', 'she', 'it', 'they', 'him', 'her', 'them']:
                            # Simple replacement (this could be more sophisticated)
                            resolved_text = resolved_text.replace(mention['text'], main_entity, 1)
        
        return resolved_text


# Example usage
if __name__ == "__main__":
    resolver = CorPipeCoreference()
    
    test_text = "Maria went to visit her grandmother because she had baked a fresh apple pie. When Maria arrived, she noticed that the pie was still warm, and it reminded her of the ones she used to eat as a child. Later, they decided to invite John over, but he said he couldn’t come because his car had broken down."
    result = resolver.resolve_coreferences(test_text)
    print(f"Coreference result: {result}")
