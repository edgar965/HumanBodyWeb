"""
Compare API responses between Theatre and Dashboard
"""
import requests
import json

# Dashboard typically loads with body_type parameter
dashboard_url = "http://localhost:8081/api/character/mesh/?body_type=Female_Caucasian"

# Theatre loads via preset which might have morphs
theatre_preset_url = "http://localhost:8081/api/character/model/FemaleWithHair"

print("=== Fetching Dashboard API ===")
dash_resp = requests.get(dashboard_url)
print(f"Status: {dash_resp.status_code}")

print("\n=== Fetching Theatre Preset ===")
preset_resp = requests.get(theatre_preset_url)
print(f"Status: {preset_resp.status_code}")
preset_data = preset_resp.json()
print(f"Preset body_type: {preset_data.get('body_type')}")
print(f"Preset morphs: {list(preset_data.get('morphs', {}).keys())[:5]}...")

# Build Theatre mesh URL from preset
params = {"body_type": preset_data.get("body_type", "Female_Caucasian")}
if preset_data.get("morphs"):
    for k, v in preset_data["morphs"].items():
        params[f"morph_{k}"] = v

theatre_url = "http://localhost:8081/api/character/mesh/?" + "&".join(f"{k}={v}" for k, v in params.items())
print(f"\n=== Fetching Theatre Mesh API ===")
print(f"URL: {theatre_url[:100]}...")
theatre_resp = requests.get(theatre_url)
print(f"Status: {theatre_resp.status_code}")

# Compare response sizes
dash_data = dash_resp.json()
theatre_data = theatre_resp.json()

print("\n=== COMPARISON ===")
print(f"Dashboard vertices length: {len(dash_data.get('vertices', ''))}")
print(f"Theatre vertices length: {len(theatre_data.get('vertices', ''))}")
print(f"Dashboard faces length: {len(dash_data.get('faces', ''))}")
print(f"Theatre faces length: {len(theatre_data.get('faces', ''))}")
print(f"Dashboard has normals: {bool(dash_data.get('normals'))}")
print(f"Theatre has normals: {bool(theatre_data.get('normals'))}")
print(f"Dashboard groups: {len(dash_data.get('groups', []))}")
print(f"Theatre groups: {len(theatre_data.get('groups', []))}")

if dash_data.get('vertices') == theatre_data.get('vertices'):
    print("\n✓ Vertices are IDENTICAL")
else:
    print("\n✗ Vertices are DIFFERENT!")

if dash_data.get('normals') == theatre_data.get('normals'):
    print("✓ Normals are IDENTICAL")
else:
    print("✗ Normals are DIFFERENT!")
