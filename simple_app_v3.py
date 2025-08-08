import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import glob
import pickle
from typing import List, Dict

class DubaiPropertyLookupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dubai Property Transaction Lookup")
        self.root.geometry("800x600")
        
        # Data storage
        self.data_cache = {}
        self.all_properties = []
        self.all_units = {}
        
        # Show loading screen
        self.show_loading_screen()
        
        # Load data in background
        self.root.after(100, self.load_data_and_create_ui)
        
    def show_loading_screen(self):
        """Show loading screen while data loads"""
        self.loading_frame = ttk.Frame(self.root, padding="20")
        self.loading_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(self.loading_frame, text="Loading Dubai Property Data...", 
                 font=("Arial", 16, "bold")).grid(row=0, column=0, pady=20)
        
        self.progress = ttk.Progressbar(self.loading_frame, mode='indeterminate')
        self.progress.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        self.progress.start()
        
        self.status_label = ttk.Label(self.loading_frame, text="Initializing...")
        self.status_label.grid(row=2, column=0, pady=10)
        
        # Configure grid weights
        self.loading_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
    def load_data_and_create_ui(self):
        """Load data and create UI"""
        try:
            # Check if cache exists
            cache_file = "property_cache.pkl"
            if os.path.exists(cache_file):
                self.status_label.config(text="Loading cached data...")
                self.root.update()
                
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                    self.data_cache = cached_data['data_cache']
                    self.all_properties = cached_data['all_properties']
                    self.all_units = cached_data['all_units']
                
                self.status_label.config(text="Creating interface...")
                self.root.update()
                
                # Remove loading screen and create main UI
                self.loading_frame.destroy()
                self.create_widgets()
                return
            
            # Load from Excel files if no cache
            self.status_label.config(text="Scanning Excel files...")
            self.root.update()
            
            excel_files = glob.glob("*_preprocessing.xlsx")
            total_files = len(excel_files)
            
            for i, file_path in enumerate(excel_files):
                try:
                    # Extract community name from filename
                    filename = os.path.basename(file_path)
                    community = filename.replace("_preprocessing.xlsx", "").replace("_", " ").title()
                    
                    self.status_label.config(text=f"Loading {community}... ({i+1}/{total_files})")
                    self.root.update()
                    
                    # Read Excel file
                    df = pd.read_excel(file_path)
                    
                    # Clean and process data
                    df = df.dropna(subset=['property', 'Unit'])
                    df['property'] = df['property'].astype(str).str.strip()
                    df['Unit'] = df['Unit'].astype(str).str.strip()
                    
                    # Store data by community
                    self.data_cache[community] = df
                    
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
            
            # Build property and unit lists
            self.status_label.config(text="Building search indexes...")
            self.root.update()
            
            for community, df in self.data_cache.items():
                properties = df['property'].unique()
                for prop in properties:
                    if prop not in self.all_properties:
                        self.all_properties.append(prop)
                    
                    # Get units for this property
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
            
            self.status_label.config(text="Creating interface...")
            self.root.update()
            
            # Remove loading screen and create main UI
            self.loading_frame.destroy()
            self.create_widgets()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading data: {str(e)}")
            self.root.quit()
    
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Dubai Property Transaction Lookup", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Property search
        ttk.Label(main_frame, text="Property:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.property_var = tk.StringVar()
        self.property_entry = ttk.Entry(main_frame, textvariable=self.property_var, width=50)
        self.property_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.property_entry.bind('<KeyRelease>', self.on_property_search)
        
        # Property listbox
        self.property_listbox = tk.Listbox(main_frame, height=8)
        self.property_listbox.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        self.property_listbox.bind('<<ListboxSelect>>', self.on_property_select)
        
        # Unit search
        ttk.Label(main_frame, text="Unit Number:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar()
        self.unit_entry = ttk.Entry(main_frame, textvariable=self.unit_var, width=50, state='disabled')
        self.unit_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.unit_entry.bind('<KeyRelease>', self.on_unit_search)
        
        # Unit listbox
        self.unit_listbox = tk.Listbox(main_frame, height=8)
        self.unit_listbox.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        self.unit_listbox.bind('<<ListboxSelect>>', self.on_unit_select)
        
        # Search button
        self.search_button = ttk.Button(main_frame, text="Search Transactions", 
                                       command=self.search_transactions, state='disabled')
        self.search_button.grid(row=5, column=1, pady=20, padx=(10, 0))
        
        # Results text area
        ttk.Label(main_frame, text="Transaction Results:").grid(row=6, column=0, sticky=tk.W, pady=(20, 5))
        self.results_text = tk.Text(main_frame, height=15, width=80, wrap=tk.WORD)
        self.results_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=7, column=2, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Current selections
        self.selected_property = ""
        self.selected_unit = ""
        
        # Show loaded properties count
        ttk.Label(main_frame, text=f"Loaded {len(self.all_properties)} properties", 
                 font=("Arial", 10)).grid(row=8, column=0, columnspan=2, pady=(10, 0))
    
    def on_property_search(self, event):
        query = self.property_var.get().lower().strip()
        self.property_listbox.delete(0, tk.END)
        
        if query:
            matches = [prop for prop in self.all_properties if query in prop.lower()]
            
            for match in sorted(matches):
                self.property_listbox.insert(tk.END, match)
    
    def on_property_select(self, event):
        if self.property_listbox.curselection():
            selection = self.property_listbox.get(self.property_listbox.curselection())
            self.selected_property = selection
            self.property_var.set(selection)
            self.unit_entry.config(state='normal')
            self.unit_var.set("")
            self.selected_unit = ""
            self.update_search_button()
    
    def on_unit_search(self, event):
        if not self.selected_property:
            return
            
        query = self.unit_var.get().lower().strip()
        self.unit_listbox.delete(0, tk.END)
        
        if query and self.selected_property in self.all_units:
            units = self.all_units[self.selected_property]
            matches = [unit for unit in units if query in unit.lower()]
            
            for match in sorted(matches):
                self.unit_listbox.insert(tk.END, match)
    
    def on_unit_select(self, event):
        if self.unit_listbox.curselection():
            selection = self.unit_listbox.get(self.unit_listbox.curselection())
            self.selected_unit = selection
            self.unit_var.set(selection)
            self.update_search_button()
    
    def update_search_button(self):
        if self.selected_property and self.selected_unit:
            self.search_button.config(state='normal')
        else:
            self.search_button.config(state='disabled')
    
    def search_transactions(self):
        if not all([self.selected_property, self.selected_unit]):
            messagebox.showwarning("Warning", "Please select property and unit first.")
            return
        
        try:
            # Search through all communities for this property and unit
            all_transactions = []
            
            for community, df in self.data_cache.items():
                unit_data = df[(df['property'] == self.selected_property) & (df['Unit'] == self.selected_unit)]
                if not unit_data.empty:
                    for _, row in unit_data.iterrows():
                        transaction = {
                            'community': community,
                            'transaction_date': row.get('transaction_date', 'N/A'),
                            'price_aed': row.get('price aed', 'N/A'),
                            'price_per_sqft': row.get('price_per_sqft', 'N/A'),
                            'developer': row.get('developer', 'N/A'),
                            'property_type': row.get('property_type', 'N/A'),
                            'bedrooms': row.get('bedrooms', 'N/A'),
                            'built_up_area_sqft': row.get('built_up_area_sqft', 'N/A'),
                            'owner_name': row.get('owner_name', 'N/A'),
                            'owner_mobile_1': row.get('owner_mobile_1', 'N/A'),
                            'owner_mobile_2': row.get('owner_mobile_2', 'N/A'),
                            'original_mobile': row.get('original_mobile', 'N/A'),
                            'owner_country': row.get('owner_country', 'N/A'),
                            'transaction_type': row.get('transaction_type', 'N/A')
                        }
                        all_transactions.append(transaction)
            
            if not all_transactions:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "No transaction data found for the selected unit.")
                return
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            
            for idx, transaction in enumerate(all_transactions):
                result_text = f"""
Transaction {idx + 1}:
{'='*50}
Community: {transaction['community']}
Transaction Date: {transaction['transaction_date']}
Price (AED): {transaction['price_aed']}
Price per Sq Ft: {transaction['price_per_sqft']}
Developer: {transaction['developer']}
Property Type: {transaction['property_type']}
Bedrooms: {transaction['bedrooms']}
Built-up Area (Sq Ft): {transaction['built_up_area_sqft']}

OWNER DETAILS:
Owner Name: {transaction['owner_name']}
Mobile 1: {transaction['owner_mobile_1']}
Mobile 2: {transaction['owner_mobile_2']}
Original Mobile: {transaction['original_mobile']}
Owner Country: {transaction['owner_country']}
Transaction Type: {transaction['transaction_type']}

{'-'*50}

"""
                self.results_text.insert(tk.END, result_text)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching transactions: {str(e)}")

def main():
    root = tk.Tk()
    app = DubaiPropertyLookupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
