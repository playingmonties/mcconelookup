from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import glob
import pickle
from typing import List, Dict

app = Flask(__name__)

class DubaiPropertyLookup:
    def __init__(self):
        self.data_cache = {}
        self.all_properties = []
        self.all_units = {}
        self.load_data()
    
    def load_data(self):
        """Load data from cache or Excel files"""
        cache_file = "property_cache.pkl"
        
        if os.path.exists(cache_file):
            print("Loading from cache...")
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                self.data_cache = cached_data['data_cache']
                self.all_properties = cached_data['all_properties']
                self.all_units = cached_data['all_units']
            print(f"Loaded {len(self.all_properties)} properties from cache")
            return
        
        print("Loading from Excel files...")
        excel_files = glob.glob("data/*_preprocessing.xlsx")
        
        for file_path in excel_files:
            try:
                filename = os.path.basename(file_path)
                community = filename.replace("_preprocessing.xlsx", "").replace("_", " ").title()
                
                df = pd.read_excel(file_path)
                df = df.dropna(subset=['property', 'Unit'])
                df['property'] = df['property'].astype(str).str.strip()
                df['Unit'] = df['Unit'].astype(str).str.strip()
                
                self.data_cache[community] = df
                print(f"Loaded {len(df)} records for {community}")
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        # Build property and unit lists
        for community, df in self.data_cache.items():
            properties = df['property'].unique()
            for prop in properties:
                if prop not in self.all_properties:
                    self.all_properties.append(prop)
                
                property_data = df[df['property'] == prop]
                units = property_data['Unit'].unique()
                self.all_units[prop] = units.tolist()
        
        # Save cache
        cache_data = {
            'data_cache': self.data_cache,
            'all_properties': self.all_properties,
            'all_units': self.all_units
        }
        
        with open(cache_file, 'wb') as f:
            pickle.dump(cache_data, f)
        
        print(f"Loaded {len(self.all_properties)} properties")
    
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
lookup_system = DubaiPropertyLookup()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search_properties')
def search_properties():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    results = lookup_system.search_properties(query)
    return jsonify(results)

@app.route('/api/search_units')
def search_units():
    property_name = request.args.get('property', '').strip()
    query = request.args.get('q', '').strip()
    
    if not property_name or not query:
        return jsonify([])
    
    results = lookup_system.search_units(property_name, query)
    return jsonify(results)

@app.route('/api/get_transactions')
def get_transactions():
    property_name = request.args.get('property', '').strip()
    unit_number = request.args.get('unit', '').strip()
    
    if not property_name or not unit_number:
        return jsonify([])
    
    transactions = lookup_system.get_transaction_data(property_name, unit_number)
    return jsonify(transactions)

@app.route('/api/stats')
def get_stats():
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
