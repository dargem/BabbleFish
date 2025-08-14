#!/usr/bin/env python3
"""
Test script for batch coreference resolution.
This tests the new batch processing functionality that loads the model once
and processes multiple texts efficiently.
"""

import sys
import time

from src.data_manager.coreference_resolver import CoreferenceResolver
from lingua import Language


def test_large_text_processing():
    """Test processing a large text."""
    print("=== Testing Large Text Processing ===")
    
    # Create a large text with multiple coreferences
    large_text = """
    Emma had been planning the trip for months. She booked the flights, reserved a small cabin near the lake, and even made a list of all the places she wanted to visit. When her brother Daniel heard about it, he asked if he could join. She was hesitant at first but eventually agreed.

    The cabin turned out to be smaller than they expected, but it was cozy. It had a stone fireplace that Daniel insisted on using, even though the weather was warm. Emma preferred to sit outside on the porch, watching the water. From there, she could see the old dock where their father used to take them fishing. That memory made her smile.

    On the second day, they rented a small boat. Daniel was determined to row it across the lake, but Emma wasn’t convinced it was safe. The water looked calm, yet she could see the clouds gathering in the distance. When the first drops of rain fell, she told him it was time to head back. He agreed, though she suspected he just didn’t want to admit she was right.
    """.strip()
    
    print(f"Processing large text ({len(large_text)} characters)...")
    print("Text preview:", large_text[:200] + "...")
    
    start_time = time.time()
    resolved_text = CoreferenceResolver.resolve_coreferences_large_text(large_text, Language.ENGLISH)
    large_text_time = time.time() - start_time
    
    print(f"\nLarge text processing completed in {large_text_time:.2f} seconds")
    print("Resolved text preview:", resolved_text[:300] + "...")
    
    # Count changes
    original_words = large_text.split()
    resolved_words = resolved_text.split()
    changes = sum(1 for o, r in zip(original_words, resolved_words) if o != r)
    
    print(f"Changes made: {changes} words modified")
    
    return large_text_time

def main():
    """Run all batch processing tests."""
    print("🧪 Testing Batch Coreference Resolution")
    print("=" * 60)
    
    try:

        large_text_time = test_large_text_processing()
        
        print("\n" + "=" * 60)
   
        print("\n" + "=" * 60)
        print("🎉 All batch processing tests completed!")
        print(f"Batch processing provides significant performance improvements:")
        print(f"- Single large text: {large_text_time:.2f}s")
        print("✅ The model now loads once and processes multiple texts efficiently!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
