import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
import glob
from typing import List, Dict

class DubaiPropertyLookupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dubai Property Transaction Lookup")
        self.root.geometry("800x600")
        
        # Data storage
        self.data_cache = {}
        self.community_mapping = {}
        
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
                    
                    # Clean and process data - only keep essential columns
                    df = df.dropna(subset=['property', 'Unit'])
                    df['property'] = df['property'].astype(str).str.strip()
                    df['Unit'] = df['Unit'].astype(str).str.strip()
                    
                    # Store data by community
                    self.data_cache[community] = df
                    self.community_mapping[community.lower()] = community
                    
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    continue
            
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
        
        # Community search
        ttk.Label(main_frame, text="Master Community:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.community_var = tk.StringVar()
        self.community_entry = ttk.Entry(main_frame, textvariable=self.community_var, width=40)
        self.community_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.community_entry.bind('<KeyRelease>', self.on_community_search)
        
        # Community listbox
        self.community_listbox = tk.Listbox(main_frame, height=6)
        self.community_listbox.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        self.community_listbox.bind('<<ListboxSelect>>', self.on_community_select)
        
        # Property search
        ttk.Label(main_frame, text="Property:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.property_var = tk.StringVar()
        self.property_entry = ttk.Entry(main_frame, textvariable=self.property_var, width=40, state='disabled')
        self.property_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.property_entry.bind('<KeyRelease>', self.on_property_search)
        
        # Property listbox
        self.property_listbox = tk.Listbox(main_frame, height=6)
        self.property_listbox.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        self.property_listbox.bind('<<ListboxSelect>>', self.on_property_select)
        
        # Unit search
        ttk.Label(main_frame, text="Unit Number:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.unit_var = tk.StringVar()
        self.unit_entry = ttk.Entry(main_frame, textvariable=self.unit_var, width=40, state='disabled')
        self.unit_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        self.unit_entry.bind('<KeyRelease>', self.on_unit_search)
        
        # Unit listbox
        self.unit_listbox = tk.Listbox(main_frame, height=6)
        self.unit_listbox.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        self.unit_listbox.bind('<<ListboxSelect>>', self.on_unit_select)
        
        # Search button
        self.search_button = ttk.Button(main_frame, text="Search Transactions", 
                                       command=self.search_transactions, state='disabled')
        self.search_button.grid(row=7, column=1, pady=20, padx=(10, 0))
        
        # Results text area
        ttk.Label(main_frame, text="Transaction Results:").grid(row=8, column=0, sticky=tk.W, pady=(20, 5))
        self.results_text = tk.Text(main_frame, height=15, width=80, wrap=tk.WORD)
        self.results_text.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Scrollbar for results
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.results_text.yview)
        scrollbar.grid(row=9, column=2, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=scrollbar.set)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(9, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Current selections
        self.selected_community = ""
        self.selected_property = ""
        self.selected_unit = ""
        
        # Show loaded communities count
        ttk.Label(main_frame, text=f"Loaded {len(self.data_cache)} communities", 
                 font=("Arial", 10)).grid(row=10, column=0, columnspan=2, pady=(10, 0))
    
    def on_community_search(self, event):
        query = self.community_var.get().lower().strip()
        self.community_listbox.delete(0, tk.END)
        
        if query:
            matches = []
            for community in self.community_mapping.keys():
                if query in community:
                    matches.append(self.community_mapping[community])
            
            for match in sorted(matches):
                self.community_listbox.insert(tk.END, match)
    
    def on_community_select(self, event):
        if self.community_listbox.curselection():
            selection = self.community_listbox.get(self.community_listbox.curselection())
            self.selected_community = selection
            self.community_var.set(selection)
            self.property_entry.config(state='normal')
            self.property_var.set("")
            self.selected_property = ""
            self.selected_unit = ""
            self.unit_entry.config(state='disabled')
            self.unit_var.set("")
            self.update_search_button()
    
    def on_property_search(self, event):
        if not self.selected_community:
            return
            
        query = self.property_var.get().lower().strip()
        self.property_listbox.delete(0, tk.END)
        
        if query and self.selected_community in self.data_cache:
            df = self.data_cache[self.selected_community]
            properties = df['property'].unique()
            matches = [prop for prop in properties if query in prop.lower()]
            
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
        
        if query and self.selected_community in self.data_cache:
            df = self.data_cache[self.selected_community]
            property_data = df[df['property'] == self.selected_property]
            units = property_data['Unit'].unique()
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
        if self.selected_community and self.selected_property and self.selected_unit:
            self.search_button.config(state='normal')
        else:
            self.search_button.config(state='disabled')
    
    def search_transactions(self):
        if not all([self.selected_community, self.selected_property, self.selected_unit]):
            messagebox.showwarning("Warning", "Please select community, property, and unit first.")
            return
        
        try:
            df = self.data_cache[self.selected_community]
            unit_data = df[(df['property'] == self.selected_property) & (df['Unit'] == self.selected_unit)]
            
            if unit_data.empty:
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(tk.END, "No transaction data found for the selected unit.")
                return
            
            # Display results
            self.results_text.delete(1.0, tk.END)
            
            for idx, row in unit_data.iterrows():
                result_text = f"""
Transaction {idx + 1}:
{'='*50}
Transaction Date: {row.get('transaction_date', 'N/A')}
Price (AED): {row.get('price aed', 'N/A')}
Price per Sq Ft: {row.get('price_per_sqft', 'N/A')}
Developer: {row.get('developer', 'N/A')}
Property Type: {row.get('property_type', 'N/A')}
Bedrooms: {row.get('bedrooms', 'N/A')}
Built-up Area (Sq Ft): {row.get('built_up_area_sqft', 'N/A')}

OWNER DETAILS:
Owner Name: {row.get('owner_name', 'N/A')}
Mobile 1: {row.get('owner_mobile_1', 'N/A')}
Mobile 2: {row.get('owner_mobile_2', 'N/A')}
Original Mobile: {row.get('original_mobile', 'N/A')}
Owner Country: {row.get('owner_country', 'N/A')}
Transaction Type: {row.get('transaction_type', 'N/A')}

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
