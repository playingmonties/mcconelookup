from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import pickle
from typing import List, Dict
import time
import requests
import json

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
        """Load data from cache or Supabase Database"""
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
        
        print("Loading from Supabase Database...")
        
        try:
            # Query all data from the database table
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': f'Bearer {SUPABASE_KEY}',
                'Content-Type': 'application/json'
            }
            
            # First, let's get a sample to see the table structure
            sample_url = f"{SUPABASE_URL}/rest/v1/transactions?select=*&limit=5"
            sample_response = requests.get(sample_url, headers=headers)
            
            if sample_response.status_code != 200:
                print(f"Error connecting to database: {sample_response.status_code}")
                print(f"Response: {sample_response.text}")
                return
            
            print("Successfully connected to database!")
            
            # Get all data from the table
            all_data_url = f"{SUPABASE_URL}/rest/v1/transactions?select=*"
            all_data_response = requests.get(all_data_url, headers=headers)
            
            if all_data_response.status_code != 200:
                print(f"Error fetching data: {all_data_response.status_code}")
                return
            
            # Parse the JSON response
            all_data = all_data_response.json()
            print(f"Loaded {len(all_data)} records from database")
            
            # Process the data similar to Excel files
            self.process_database_data(all_data)
            
            # Save to cache
            cache_data = {
                'data_cache': self.data_cache,
                'all_properties': self.all_properties,
                'all_units': self.all_units
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            print("Data cached successfully")
            
        except Exception as e:
            print(f"Error loading from database: {e}")
    
    def process_database_data(self, data):
        """Process data from database into the same format as Excel files"""
        print("Processing database data...")
        
        # Group data by property
        property_groups = {}
        
        for record in data:
            # Assuming the database has columns like 'property', 'unit', etc.
            # We'll need to adapt based on your actual column names
            property_name = record.get('property', '')
            unit_number = record.get('unit', '')
            
            if property_name and unit_number:
                if property_name not in property_groups:
                    property_groups[property_name] = []
                property_groups[property_name].append(record)
        
        # Convert to the same format as Excel processing
        for property_name, records in property_groups.items():
            self.data_cache[property_name] = records
            
            # Add to properties list
            if property_name not in self.all_properties:
                self.all_properties.append(property_name)
            
            # Add units for this property
            units = [record.get('unit', '') for record in records if record.get('unit', '')]
            self.all_units[property_name] = list(set(units))
        
        print(f"Processed {len(self.data_cache)} properties")
        print(f"Total properties: {len(self.all_properties)}")
    
    def search_properties(self, query: str) -> List[str]:
        """Search properties by name"""
        query = query.lower()
        return [prop for prop in self.all_properties if query in prop.lower()]
    
    def search_units(self, property_name: str, query: str) -> List[str]:
        """Search units within a property"""
        if property_name not in self.all_units:
            return []
        
        query = query.lower()
        units = self.all_units[property_name]
        return [unit for unit in units if query in unit.lower()]
    
    def get_transaction_data(self, property_name: str, unit_number: str) -> List[Dict]:
        """Get transaction data for a specific property and unit"""
        if property_name not in self.data_cache:
            return []
        
        # Find records that match both property and unit
        matching_records = []
        for record in self.data_cache[property_name]:
            if record.get('unit', '') == unit_number:
                matching_records.append(record)
        
        return matching_records

# Initialize the lookup system
lookup_system = None

def initialize_lookup():
    global lookup_system
    print("Initializing Dubai Property Lookup System...")
    lookup_system = DubaiPropertyLookup()
    print("Initialization complete!")

# Initialize in background
import threading
init_thread = threading.Thread(target=initialize_lookup)
init_thread.daemon = True
init_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search_properties')
def search_properties():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    if lookup_system is None:
        return jsonify([])
    
    results = lookup_system.search_properties(query)
    return jsonify(results[:10])  # Limit to 10 results

@app.route('/api/search_units')
def search_units():
    property_name = request.args.get('property', '').strip()
    query = request.args.get('q', '').strip()
    
    if not property_name or not query:
        return jsonify([])
    
    if lookup_system is None:
        return jsonify([])
    
    results = lookup_system.search_units(property_name, query)
    return jsonify(results[:10])  # Limit to 10 results

@app.route('/api/get_transactions')
def get_transactions():
    property_name = request.args.get('property', '').strip()
    unit_number = request.args.get('unit', '').strip()
    
    if not property_name or not unit_number:
        return jsonify([])
    
    if lookup_system is None:
        return jsonify([])
    
    transactions = lookup_system.get_transaction_data(property_name, unit_number)
    return jsonify(transactions)

@app.route('/api/stats')
def get_stats():
    if lookup_system is None:
        return jsonify({
            'total_properties': 0,
            'total_units': 0,
            'status': 'loading'
        })
    
    total_units = sum(len(units) for units in lookup_system.all_units.values())
    
    return jsonify({
        'total_properties': len(lookup_system.all_properties),
        'total_units': total_units,
        'status': 'ready'
    })

@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
