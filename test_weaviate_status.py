#!/usr/bin/env python3

from app.services.ai_service import ai_service
import asyncio

async def test_weaviate():
    print('Initializing services...')
    init_result = await ai_service.initialize()
    print(f'Init result: {init_result}')
    
    print('Getting status...')
    status = await ai_service.get_vector_database_status()
    print(f'Status: {status}')
    
    if status['connected']:
        print('Weaviate is connected!')
        if status['collections']:
            print(f'Found {len(status["collections"])} collections:')
            for col in status['collections']:
                print(f'  - {col["name"]}: {col["object_count"]} objects')
        else:
            print('No collections found')
    else:
        print('Weaviate is not connected')
    
    await ai_service.weaviate.disconnect()

if __name__ == "__main__":
    asyncio.run(test_weaviate())
