#!/usr/bin/env python3
import sys
import asyncio
sys.path.insert(0, "/app/api")

from app.services.jellyfin_service import get_jellyfin_service

async def debug_libraries():
    jellyfin = get_jellyfin_service()
    libraries = await jellyfin.get_libraries()
    
    print("Library structure:")
    for i, lib in enumerate(libraries):
        print(f"Library {i+1}:")
        for key, value in lib.items():
            print(f"  {key}: {value}")
        print()

if __name__ == "__main__":
    asyncio.run(debug_libraries())