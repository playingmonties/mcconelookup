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

# Try to get information about available tables
# First, let's try the standard PostgreSQL information_schema approach
info_url = f"{SUPABASE_URL}/rest/v1/rpc/pg_tables"
info_response = requests.get(info_url, headers=headers)

print(f"Info response status: {info_response.status_code}")
print(f"Info response: {info_response.text[:500]}")

# Try a different approach - let's see what schemas are available
schemas_url = f"{SUPABASE_URL}/rest/v1/rpc/pg_namespace"
schemas_response = requests.get(schemas_url, headers=headers)

print(f"\nSchemas response status: {schemas_response.status_code}")
print(f"Schemas response: {schemas_response.text[:500]}")

# Let's also try to access the table with different schema names
possible_schemas = ['public', 'auth', 'storage', 'graphql_public']
possible_table_names = ['transactions', 'transaction', 'dubai_transactions', 'property_transactions']

for schema in possible_schemas:
    for table_name in possible_table_names:
        test_url = f"{SUPABASE_URL}/rest/v1/{schema}.{table_name}?select=count"
        test_response = requests.get(test_url, headers=headers)
        if test_response.status_code == 200:
            print(f"✅ Found table: {schema}.{table_name}")
        elif test_response.status_code == 404:
            print(f"❌ Not found: {schema}.{table_name}")
        else:
            print(f"⚠️  Other error for {schema}.{table_name}: {test_response.status_code}")
