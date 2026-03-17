import asyncio
import httpx

BASE_URL = "http://localhost:8000/api"

async def test_pagination():
    async with httpx.AsyncClient() as client:
        # Test interactions pagination
        print("Testing interactions pagination...")
        try:
            resp = await client.get(f"{BASE_URL}/interactions?skip=0&limit=5")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Interactions (limit 5): fetched {len(data)} items")
            else:
                print(f"Interactions fetch failed: {resp.status_code}")
        except Exception as e:
            print(f"Interactions test error (is server running?): {e}")

        # Test users pagination
        print("\nTesting users pagination...")
        try:
            resp = await client.get(f"{BASE_URL}/users?skip=0&limit=2")
            if resp.status_code == 200:
                data = resp.json()
                print(f"Users (limit 2): fetched {len(data)} items")
            else:
                print(f"Users fetch failed: {resp.status_code}")
        except Exception as e:
            print(f"Users test error: {e}")

if __name__ == "__main__":
    asyncio.run(test_pagination())
