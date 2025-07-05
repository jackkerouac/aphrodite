#!/usr/bin/env python3
"""
Simple Enhanced Audio Test

Quick test of the enhanced audio extraction without complex dependencies.
"""

import sys
from pathlib import Path

# Add the API directory to the Python path
api_path = str(Path(__file__).parent.parent / "api")
sys.path.insert(0, api_path)

try:
    from app.services.badge_processing.enhanced_audio_metadata_extractor import EnhancedAudioMetadataExtractor
    
    def test_basic_extraction():
        """Test basic audio extraction functionality"""
        print("🧪 Testing Enhanced Audio Metadata Extractor...")
        print("=" * 50)
        
        # Test with AAC audio data (from your script output)
        aac_media = {
            "Id": "test-aac",
            "Name": "Test AAC Media",
            "Type": "Movie",
            "MediaStreams": [
                {
                    "Codec": "aac",
                    "Language": "eng",
                    "DisplayTitle": "Sound Media Handler - English - AAC - Stereo - Default",
                    "ChannelLayout": "stereo",
                    "BitRate": 192000,
                    "Channels": 2,
                    "SampleRate": 48000,
                    "IsDefault": True,
                    "Profile": "LC",
                    "Type": "Audio",
                    "Index": 1
                }
            ]
        }
        
        # Test with DTS audio data (from your script output)
        dts_media = {
            "Id": "test-dts",
            "Name": "Test DTS Media", 
            "Type": "Movie",
            "MediaStreams": [
                {
                    "Codec": "dts",
                    "Language": "eng",
                    "DisplayTitle": "English - DTS - 5.1 - Default",
                    "ChannelLayout": "5.1",
                    "BitRate": 1536000,
                    "Channels": 6,
                    "SampleRate": 48000,
                    "IsDefault": True,
                    "Profile": "DTS",
                    "Type": "Audio",
                    "Index": 2
                }
            ]
        }
        
        extractor = EnhancedAudioMetadataExtractor()
        
        # Test AAC
        print("🎵 Testing AAC extraction...")
        aac_result = extractor.extract_audio_info(aac_media)
        if aac_result:
            print(f"✅ AAC Result: {aac_result.get('display_codec')} → {aac_result.get('badge_image')}")
        else:
            print("❌ AAC extraction failed")
        
        print()
        
        # Test DTS
        print("🎵 Testing DTS extraction...")
        dts_result = extractor.extract_audio_info(dts_media)
        if dts_result:
            print(f"✅ DTS Result: {dts_result.get('display_codec')} → {dts_result.get('badge_image')}")
        else:
            print("❌ DTS extraction failed")
        
        print()
        print("✅ Basic extraction test completed!")
        return True
    
    if __name__ == "__main__":
        test_basic_extraction()
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the correct directory")
