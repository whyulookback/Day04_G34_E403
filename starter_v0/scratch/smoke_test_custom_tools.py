import sys
from pathlib import Path

starter_v0_dir = Path.cwd() / "starter_v0" if (Path.cwd() / "starter_v0").exists() else Path.cwd()
if str(starter_v0_dir) not in sys.path:
    sys.path.insert(0, str(starter_v0_dir))

from env_loader import load_lab_env
load_lab_env(starter_v0_dir)

from tools import TOOL_FUNCTIONS as T

print("=== SMOKE TESTING 3 NEW CUSTOM TOOLS ===")

# Test 1: weather_forecast
print("\n1. Testing 'weather_forecast'...")
r1 = T['weather_forecast'](location="Hanoi", days=1)
print(f"   Result: error={r1.get('error')}, message={r1.get('message')}")
if r1.get('items'):
    print(f"   Summary: {r1['items'][0].get('summary')}")

# Test 2: currency_convert
print("\n2. Testing 'currency_convert'...")
r2 = T['currency_convert'](from_currency="USD", to_currency="VND", amount=100)
print(f"   Result: error={r2.get('error')}, message={r2.get('message')}")
if r2.get('items'):
    print(f"   Summary: {r2['items'][0].get('summary')}")

# Test 3: crypto_price
print("\n3. Testing 'crypto_price'...")
r3 = T['crypto_price'](symbol="bitcoin", currency="usd")
print(f"   Result: error={r3.get('error')}, message={r3.get('message')}")
if r3.get('items'):
    print(f"   Summary: {r3['items'][0].get('summary')}")

print("\n=== SMOKE TEST COMPLETE ===")
