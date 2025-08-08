from flask import Flask, render_template, request, jsonify
import psycopg2
import os
import pickle
from typing import List, Dict
import time
import json

app = Flask(__name__)

# PostgreSQL connection string
DATABASE_URL = "postgresql://postgres.hwfrwtuqpjbkuywgcvwn:Enoccm_1199@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

class DubaiPropertyLookup:
    def __init__(self):
        self.data_cache = {}
        self.all_properties = []
        self.all_units = {}
        self.load_data()
    
    def load_data(self):
        """Load data from cache or PostgreSQL Database"""
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
        
        print("Loading from PostgreSQL Database...")
        
        try:
            # Connect to PostgreSQL database
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            print("✅ Successfully connected to database!")
            
            # Get all unique properties and their units in one query
            print("Loading properties and units...")
            cursor.execute("""
                SELECT DISTINCT property, unit 
                FROM transactions 
                WHERE property IS NOT NULL AND property != '' 
                AND unit IS NOT NULL AND unit != ''
                ORDER BY property, unit
            """)
            
            results = cursor.fetchall()
            print(f"Found {len(results)} property-unit combinations")
            
            # Process the results
            self.all_properties = []
            self.all_units = {}
            
            for property_name, unit in results:
                if property_name not in self.all_properties:
                    self.all_properties.append(property_name)
                    self.all_units[property_name] = []
                self.all_units[property_name].append(unit)
            
            print(f"Processed {len(self.all_properties)} unique properties")
            print(f"Loaded units for {len(self.all_units)} properties")
            
            cursor.close()
            conn.close()
            
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
        try:
            conn = psycopg2.connect(DATABASE_URL)
            cursor = conn.cursor()
            
            # Get all transaction records for this property and unit
            cursor.execute("""
                SELECT 
                    transaction_date,
                    price_aed,
                    price_per_sqft,
                    developer,
                    community,
                    property,
                    property_type,
                    unit,
                    bedrooms,
                    built_up_area_sqft,
                    land_size_sqft,
                    owner_name,
                    owner_mobile_1,
                    owner_mobile_2,
                    original_mobile,
                    owner_country,
                    transaction_type,
                    source_file
                FROM transactions 
                WHERE property = %s AND unit = %s
                ORDER BY transaction_date DESC
            """, (property_name, unit_number))
            
            records = cursor.fetchall()
            
            # Convert to list of dictionaries
            transactions = []
            for record in records:
                transaction = {
                    'transaction_date': record[0].isoformat() if record[0] else None,
                    'price_aed': record[1],
                    'price_per_sqft': record[2],
                    'developer': record[3],
                    'community': record[4],
                    'property': record[5],
                    'property_type': record[6],
                    'unit': record[7],
                    'bedrooms': record[8],
                    'built_up_area_sqft': record[9],
                    'land_size_sqft': record[10],
                    'owner_name': record[11],
                    'owner_mobile_1': record[12],
                    'owner_mobile_2': record[13],
                    'original_mobile': record[14],
                    'owner_country': record[15],
                    'transaction_type': record[16],
                    'source_file': record[17]
                }
                transactions.append(transaction)
            
            cursor.close()
            conn.close()
            
            return transactions
            
        except Exception as e:
            print(f"Error getting transaction data: {e}")
            return []

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
