from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import glob
from typing import Dict, List, Optional
import json

app = Flask(__name__)

class DubaiPropertyLookup:
    def __init__(self, data_directory: str):
        self.data_directory = data_directory
        self.data_cache = {}
        self.community_mapping = {}
        self.load_all_data()
    
    def load_all_data(self):
        """Load all Excel files and create searchable data structure"""
        excel_files = glob.glob(os.path.join(self.data_directory, "*_preprocessing.xlsx"))
        
        for file_path in excel_files:
            try:
                # Extract community name from filename
                filename = os.path.basename(file_path)
                community = filename.replace("_preprocessing.xlsx", "").replace("_", " ").title()
                
                # Read Excel file
                df = pd.read_excel(file_path)
                
                # Clean and process data
                df = df.dropna(subset=['property', 'Unit'])
                df['property'] = df['property'].astype(str).str.strip()
                df['Unit'] = df['Unit'].astype(str).str.strip()
                
                # Store data by community
                self.data_cache[community] = df
                self.community_mapping[community.lower()] = community
                
                print(f"Loaded {len(df)} records for {community}")
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    def search_communities(self, query: str) -> List[str]:
        """Search for communities that match the query"""
        query = query.lower().strip()
        matches = []
        
        for community in self.community_mapping.keys():
            if query in community:
                matches.append(self.community_mapping[community])
        
        return sorted(matches)
    
    def get_properties_for_community(self, community: str) -> List[str]:
        """Get all properties for a specific community"""
        if community not in self.data_cache:
            return []
        
        df = self.data_cache[community]
        properties = df['property'].unique().tolist()
        return sorted(properties)
    
    def search_properties(self, community: str, query: str) -> List[str]:
        """Search for properties within a community"""
        if community not in self.data_cache:
            return []
        
        df = self.data_cache[community]
        query = query.lower().strip()
        
        properties = df['property'].unique()
        matches = [prop for prop in properties if query in prop.lower()]
        return sorted(matches)
    
    def get_units_for_property(self, community: str, property_name: str) -> List[str]:
        """Get all units for a specific property"""
        if community not in self.data_cache:
            return []
        
        df = self.data_cache[community]
        property_units = df[df['property'] == property_name]['Unit'].unique().tolist()
        return sorted(property_units)
    
    def search_units(self, community: str, property_name: str, query: str) -> List[str]:
        """Search for units within a property"""
        if community not in self.data_cache:
            return []
        
        df = self.data_cache[community]
        property_data = df[df['property'] == property_name]
        
        if property_data.empty:
            return []
        
        query = query.lower().strip()
        units = property_data['Unit'].unique()
        matches = [unit for unit in units if query in unit.lower()]
        return sorted(matches)
    
    def get_transaction_data(self, community: str, property_name: str, unit_number: str) -> List[Dict]:
        """Get transaction data for a specific unit"""
        if community not in self.data_cache:
            return []
        
        df = self.data_cache[community]
        unit_data = df[(df['property'] == property_name) & (df['Unit'] == unit_number)]
        
        if unit_data.empty:
            return []
        
        # Convert to list of dictionaries
        transactions = []
        for _, row in unit_data.iterrows():
            transaction = {
                'transaction_date': str(row.get('transaction_date', '')),
                'price_aed': str(row.get('price aed', '')),
                'developer': str(row.get('developer', '')),
                'property_type': str(row.get('property_type', '')),
                'bedrooms': str(row.get('bedrooms', '')),
                'built_up_area_sqft': str(row.get('built_up_area_sqft', '')),
                'price_per_sqft': str(row.get('price_per_sqft', '')),
                'owner_name': str(row.get('owner_name', '')),
                'owner_mobile_1': str(row.get('owner_mobile_1', '')),
                'owner_mobile_2': str(row.get('owner_mobile_2', '')),
                'original_mobile': str(row.get('original_mobile', '')),
                'owner_country': str(row.get('owner_country', '')),
                'transaction_type': str(row.get('transaction_type', ''))
            }
            transactions.append(transaction)
        
        return transactions

# Initialize the lookup system
lookup_system = DubaiPropertyLookup('.')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search_communities')
def search_communities():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    
    results = lookup_system.search_communities(query)
    return jsonify(results)

@app.route('/api/search_properties')
def search_properties():
    community = request.args.get('community', '').strip()
    query = request.args.get('q', '').strip()
    
    if not community or not query:
        return jsonify([])
    
    results = lookup_system.search_properties(community, query)
    return jsonify(results)

@app.route('/api/search_units')
def search_units():
    community = request.args.get('community', '').strip()
    property_name = request.args.get('property', '').strip()
    query = request.args.get('q', '').strip()
    
    if not community or not property_name or not query:
        return jsonify([])
    
    results = lookup_system.search_units(community, property_name, query)
    return jsonify(results)

@app.route('/api/get_transactions')
def get_transactions():
    community = request.args.get('community', '').strip()
    property_name = request.args.get('property', '').strip()
    unit_number = request.args.get('unit', '').strip()
    
    if not community or not property_name or not unit_number:
        return jsonify([])
    
    transactions = lookup_system.get_transaction_data(community, property_name, unit_number)
    return jsonify(transactions)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=4000)
