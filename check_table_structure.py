import requests
import json

# Supabase configuration
SUPABASE_URL = "https://yqnhpnpdvughdkdnlcrv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlxbmhwbnBkdnVnaGRrZG5sY3J2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2NTY0MDQsImV4cCI6MjA3MDIzMjQwNH0.g0oN1YrrtmaXGrS67VtMQG8DpA1TGXDydpaMb3D1UNk"

headers = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json'
}

# Get a sample of data to see the structure
sample_url = f"{SUPABASE_URL}/rest/v1/transactions?select=*&limit=3"
sample_response = requests.get(sample_url, headers=headers)

if sample_response.status_code == 200:
    data = sample_response.json()
    print("✅ Successfully connected to database!")
    print(f"📊 Found {len(data)} sample records")
    
    if data:
        print("\n📋 Table structure (first record):")
        first_record = data[0]
        for key, value in first_record.items():
            print(f"  {key}: {type(value).__name__} = {value}")
    else:
        print("⚠️  No data found in table")
else:
    print(f"❌ Error connecting to database: {sample_response.status_code}")
    print(f"Response: {sample_response.text}")

# Also try to get total count
count_url = f"{SUPABASE_URL}/rest/v1/transactions?select=count"
count_response = requests.get(count_url, headers=headers)

if count_response.status_code == 200:
    count_data = count_response.json()
    print(f"\n📈 Total records in table: {count_data}")
else:
    print(f"\n❌ Could not get record count: {count_response.status_code}")
