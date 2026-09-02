import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.providers.api_football import APIFootballProvider

async def main():
    api_key = "18884ff8db1570c2454d730ef111e03d"
    provider = APIFootballProvider(api_key=api_key)
    
    print(f"Testing connection with {provider.name}...")
    try:
        fixtures = await provider.get_fixtures()
        print(f"Success! Retrieved {len(fixtures)} live fixtures.")
        if len(fixtures) > 0:
            f = fixtures[0]
            print(f"Sample Fixture ID {f.id}: {f.home_team_id} vs {f.away_team_id} | Status: {f.status} | Time: {f.start_time}")
    except Exception as e:
        print(f"API Error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
