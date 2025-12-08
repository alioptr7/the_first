import asyncio
import aiohttp
import sys

async def verify():
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        # 1. Login
        print("Logging in...")
        try:
            async with session.post(f"{base_url}/auth/login", data={
                "username": "admin",
                "password": "admin123"
            }) as resp:
                if resp.status != 200:
                    print(f"Login failed: {resp.status}")
                    print(await resp.text())
                    sys.exit(1)
                data = await resp.json()
                token = data["access_token"]
                print("Login successful.")
        except Exception as e:
            print(f"Login error: {e}")
            sys.exit(1)

        # 2. Get Users
        print("Fetching users...")
        headers = {"Authorization": f"Bearer {token}"}
        try:
            async with session.get(f"{base_url}/users", headers=headers) as resp:
                if resp.status != 200:
                    print(f"Get Users failed: {resp.status}")
                    print(await resp.text())
                    sys.exit(1)
                
                users = await resp.json()
                print(f"Got {len(users)} users.")
                
                if not isinstance(users, list):
                    print("Error: Response is not a list")
                    sys.exit(1)
                
                if len(users) > 0:
                    user = users[0]
                    print("First user keys:", user.keys())
                    
                    if "_sa_instance_state" in user:
                        print("FAIL: _sa_instance_state found in response!")
                        sys.exit(1)
                    
                    if "profile_type" not in user:
                        print("FAIL: profile_type not found in response!")
                        sys.exit(1)
                        
                    print("SUCCESS: Response structure is correct.")
                else:
                    print("Warning: No users returned.")
                    
        except Exception as e:
            print(f"Get Users error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(verify())
