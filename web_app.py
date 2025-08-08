from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import pickle
from typing import List, Dict
import time
import tempfile
import requests

app = Flask(__name__)

# Supabase configuration
SUPABASE_URL = "https://yqnhpnpdvughdkdnlcrv.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InlxbmhwbnBkdnVnaGRrZG5sY3J2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2NTY0MDQsImV4cCI6MjA3MDIzMjQwNH0.g0oN1YrrtmaXGrS67VtMQG8DpA1TGXDydpaMb3D1UNk"

class DubaiPropertyLookup:
    def __init__(self):
        self.data_cache = {}
        self.all_properties = []
        self.all_units = {}
        self.load_data()
    
    def load_data(self):
        """Load data from cache or Supabase Storage"""
        cache_file = "property_cache.pkl"
        
        try:
            if os.path.exists(cache_file):
                print("Loading from cache...")
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.data_cache = cached_data['data_cache']
                    self.all_properties = cached_data['all_properties']
                    self.all_units = cached_data['all_units']
                print(f"Loaded {len(self.all_properties)} properties from cache")
                return
        except Exception as e:
            print(f"Cache loading failed: {e}")
        
        print("Loading from Supabase Storage...")
        
        try:
            # Use hardcoded list of files since the list API has issues
            excel_files = [
                "downtown_preprocessing.xlsx",
                "victory_heights_preprocessing.xlsx",
                "al_barari_preprocessing.xlsx",
                "jvt_preprocessing.xlsx",
                "emaar_south_preprocessing.xlsx",
                "motor_city_preprocessing.xlsx",
                "mjl_preprocessing.xlsx",
                "jvc_preprocessing.xlsx",
                "arjan_preprocessing.xlsx",
                "dubai_marina_preprocessing.xlsx",
                "city_walk_preprocessing.xlsx",
                "jbr_preprocessing.xlsx",
                "dubai_hills_preprocessing.xlsx",
                "palm_jumeirah_preprocessing.xlsx",
                "jlt_preprocessing.xlsx",
                "business_bay_preprocessing.xlsx",
                "impz_preprocessing.xlsx",
                "jge_preprocessing.xlsx",
                "emaar_beachfront_preprocessing.xlsx",
                "nad_al_shiba_preprocessing.xlsx",
                "arabian_ranches_preprocessing.xlsx",
                "mudon_preprocessing.xlsx",
                "mira_preprocessing.xlsx",
                "town_square_preprocessing.xlsx",
                "bluewaters_preprocessing.xlsx",
                "damac_hills_1_preprocessing.xlsx",
                "greens_preprocessing.xlsx",
                "la_mer_preprocessing.xlsx",
                "damac_hills_2_preprocessing.xlsx",
                "serena_preprocessing.xlsx",
                "furjan_preprocessing.xlsx",
                "jumeirah_bay_preprocessing.xlsx",
                "jumeirah_park_preprocessing.xlsx",
                "emirates_living_preprocessing.xlsx",
                "tilal_al_ghaf_preprocessing.xlsx",
                "villanova_preprocessing.xlsx",
                "meydan_preprocessing.xlsx",
                "lakes_preprocessing.xlsx",
                "damac_lagoons_preprocessing.xlsx",
                "dubai_south_preprocessing.xlsx"
            ]
            
            print(f"Loading {len(excel_files)} files from Supabase Storage")
            
            loaded_files = 0
            for filename in excel_files:
                try:
                    print(f"Loading {filename} from Supabase...")
                    
                    # Download file from Supabase using REST API
                    download_url = f"{SUPABASE_URL}/storage/v1/object/public/excel-files/{filename}"
                    file_response = requests.get(download_url)
                    
                    if file_response.status_code != 200:
                        print(f"Error downloading {filename}: {file_response.status_code}")
                        continue
                    
                    # Save to temporary file
                    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_file:
                        tmp_file.write(file_response.content)
                        tmp_file_path = tmp_file.name
                    
                    # Read Excel file
                    df = pd.read_excel(tmp_file_path)
                    df = df.dropna(subset=['property', 'Unit'])
                    df['property'] = df['property'].astype(str).str.strip()
                    df['Unit'] = df['Unit'].astype(str).str.strip()
                    
                    # Clean up temporary file
                    os.unlink(tmp_file_path)
                    
                    # Extract community name from filename
                    community = filename.replace("_preprocessing.xlsx", "").replace("_", " ").title()
                    
                    self.data_cache[community] = df
                    loaded_files += 1
                    print(f"Loaded {len(df)} records for {community}")
                    
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
                    continue
            
            print(f"Successfully loaded {loaded_files} files from Supabase")
            
            # Build property and unit lists
            for community, df in self.data_cache.items():
                try:
                    properties = df['property'].unique()
                    for prop in properties:
                        if prop not in self.all_properties:
                            self.all_properties.append(prop)
                        
                        property_data = df[df['property'] == prop]
                        units = property_data['Unit'].unique()
                        self.all_units[prop] = units.tolist()
                except Exception as e:
                    print(f"Error processing {community}: {e}")
                    continue
            
            # Save cache
            try:
                cache_data = {
                    'data_cache': self.data_cache,
                    'all_properties': self.all_properties,
                    'all_units': self.all_units
                }
                
                with open(cache_file, 'wb') as f:
                    pickle.dump(cache_data, f)
                print("Cache saved successfully")
            except Exception as e:
                print(f"Failed to save cache: {e}")
            
            print(f"Loaded {len(self.all_properties)} properties")
            
        except Exception as e:
            print(f"Error connecting to Supabase: {e}")
            # Create empty system as fallback
            self.data_cache = {}
            self.all_properties = []
            self.all_units = {}
    
    def search_properties(self, query: str) -> List[str]:
        """Search for properties that match the query"""
        query = query.lower().strip()
        if not query:
            return []
        
        matches = [prop for prop in self.all_properties if query in prop.lower()]
        return sorted(matches)
    
    def search_units(self, property_name: str, query: str) -> List[str]:
        """Search for units within a property"""
        if property_name not in self.all_units:
            return []
        
        query = query.lower().strip()
        units = self.all_units[property_name]
        matches = [unit for unit in units if query in unit.lower()]
        return sorted(matches)
    
    def get_transaction_data(self, property_name: str, unit_number: str) -> List[Dict]:
        """Get transaction data for a specific unit"""
        all_transactions = []
        
        for community, df in self.data_cache.items():
            unit_data = df[(df['property'] == property_name) & (df['Unit'] == unit_number)]
            
            if not unit_data.empty:
                for _, row in unit_data.iterrows():
                    transaction = {
                        'community': community,
                        'transaction_date': str(row.get('transaction_date', '')),
                        'price_aed': str(row.get('price aed', '')),
                        'price_per_sqft': str(row.get('price_per_sqft', '')),
                        'developer': str(row.get('developer', '')),
                        'property_type': str(row.get('property_type', '')),
                        'bedrooms': str(row.get('bedrooms', '')),
                        'built_up_area_sqft': str(row.get('built_up_area_sqft', '')),
                        'owner_name': str(row.get('owner_name', '')),
                        'owner_mobile_1': str(row.get('owner_mobile_1', '')),
                        'owner_mobile_2': str(row.get('owner_mobile_2', '')),
                        'original_mobile': str(row.get('original_mobile', '')),
                        'owner_country': str(row.get('owner_country', '')),
                        'transaction_type': str(row.get('transaction_type', ''))
                    }
                    all_transactions.append(transaction)
        
        return all_transactions

# Initialize the lookup system
print("Initializing Dubai Property Lookup System with Supabase...")
lookup_system = None

def initialize_lookup():
    global lookup_system
    try:
        lookup_system = DubaiPropertyLookup()
        print("Lookup system initialized successfully!")
    except Exception as e:
        print(f"Failed to initialize lookup system: {e}")
        # Create empty system as fallback
        lookup_system = DubaiPropertyLookup()
        lookup_system.data_cache = {}
        lookup_system.all_properties = []
        lookup_system.all_units = {}

# Start initialization in background
import threading
init_thread = threading.Thread(target=initialize_lookup)
init_thread.daemon = True
init_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search_properties')
def search_properties():
    if lookup_system is None:
        return jsonify({'error': 'System still loading'})
    
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    results = lookup_system.search_properties(query)
    return jsonify(results)

@app.route('/api/search_units')
def search_units():
    if lookup_system is None:
        return jsonify({'error': 'System still loading'})
    
    property_name = request.args.get('property', '').strip()
    query = request.args.get('q', '').strip()
    
    if not property_name or not query:
        return jsonify([])
    
    results = lookup_system.search_units(property_name, query)
    return jsonify(results)

@app.route('/api/get_transactions')
def get_transactions():
    if lookup_system is None:
        return jsonify({'error': 'System still loading'})
    
    property_name = request.args.get('property', '').strip()
    unit_number = request.args.get('unit', '').strip()
    
    if not property_name or not unit_number:
        return jsonify([])
    
    transactions = lookup_system.get_transaction_data(property_name, unit_number)
    return jsonify(transactions)

@app.route('/api/stats')
def get_stats():
    if lookup_system is None:
        return jsonify({'error': 'System still loading'})
    
    property_count = len(lookup_system.all_properties)
    community_count = len(lookup_system.data_cache)
    
    # Calculate total transactions
    transaction_count = 0
    for df in lookup_system.data_cache.values():
        transaction_count += len(df)
    
    return jsonify({
        'property_count': property_count,
        'community_count': community_count,
        'transaction_count': transaction_count
    })

@app.route('/health')
def health_check():
    if lookup_system is None:
        return jsonify({'status': 'loading'})
    return jsonify({'status': 'healthy', 'properties_loaded': len(lookup_system.all_properties)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting Flask app on port {port}")
    app.run(debug=True, host='0.0.0.0', port=port)
