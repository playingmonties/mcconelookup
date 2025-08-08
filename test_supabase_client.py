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

print("🔍 Checking available tables in Supabase...")

# Try to access common table names that might exist
possible_tables = [
    'transactions',
    'transaction', 
    'dubai_transactions',
    'property_transactions',
    'properties',
    'units',
    'owners',
    'real_estate',
    'dubai_properties',
    'property_data',
    'transaction_data',
    'excel_data',
    'csv_data'
]

print("\n📋 Testing table access:")
for table_name in possible_tables:
    # Try without schema prefix first
    test_url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=count"
    test_response = requests.get(test_url, headers=headers)
    
    if test_response.status_code == 200:
        print(f"✅ Found table: {table_name}")
        # Try to get a sample record
        sample_url = f"{SUPABASE_URL}/rest/v1/{table_name}?select=*&limit=1"
        sample_response = requests.get(sample_url, headers=headers)
        if sample_response.status_code == 200:
            sample_data = sample_response.json()
            if sample_data:
                print(f"   📊 Sample record keys: {list(sample_data[0].keys())}")
            else:
                print(f"   📊 Table is empty")
    elif test_response.status_code == 404:
        print(f"❌ Not found: {table_name}")
    else:
        print(f"⚠️  Other error for {table_name}: {test_response.status_code}")

# Also try to check if there are any tables in the storage bucket
print("\n📦 Checking storage bucket:")
storage_url = f"{SUPABASE_URL}/storage/v1/bucket/list"
storage_response = requests.get(storage_url, headers=headers)

if storage_response.status_code == 200:
    buckets = storage_response.json()
    print(f"✅ Found {len(buckets)} storage buckets:")
    for bucket in buckets:
        print(f"   📁 {bucket.get('name', 'unknown')}")
else:
    print(f"❌ Could not access storage: {storage_response.status_code}")

# Try to list files in the excel-files bucket
print("\n📄 Checking excel-files bucket:")
files_url = f"{SUPABASE_URL}/storage/v1/object/list/excel-files"
files_response = requests.get(files_url, headers=headers)

if files_response.status_code == 200:
    files = files_response.json()
    print(f"✅ Found {len(files)} files in excel-files bucket:")
    for file in files[:5]:  # Show first 5 files
        print(f"   📄 {file.get('name', 'unknown')}")
    if len(files) > 5:
        print(f"   ... and {len(files) - 5} more files")
else:
    print(f"❌ Could not access excel-files bucket: {files_response.status_code}")
