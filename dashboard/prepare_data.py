"""
Data preparation script for the interactive dashboard.
Generates JSON files from the analysis data.
"""
import sys
import os
import json
import numpy as np

# Add parent code directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'code'))

# Import load_data from analysis script
from analysis_report_v2 import load_data

def clean_for_json(obj):
    """Replace NaN and Inf values with None for JSON compatibility."""
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return obj
    return obj

def prepare_dashboard_data():
    print("Loading data...")
    df, state_coords = load_data()
    print(f"Loaded {len(df)} records")
    
    # Create public/data directory
    data_dir = os.path.join(os.path.dirname(__file__), 'public', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # 1. County Scatter Data (Averaged across years)
    print("Preparing county scatter data...")
    county_avg = df.groupby('FIPS_STR').agg({
        'Pct_Less_HS': 'mean',
        'Fatality_Rate': 'mean',
        'Urbanicity': 'first',
        'Population': 'mean',
        'State_Abbrev': 'first',
        'Drunk_Rate_Per_100k': 'mean',
        'Dark_Pct': 'mean',
        'Weather_Pct': 'mean'
    }).reset_index()
    
    # Drop rows with NaN in critical columns
    county_avg = county_avg.dropna(subset=['Pct_Less_HS', 'Fatality_Rate', 'Population'])
    
    # Add county name (we'll use FIPS for now, can enhance later)
    county_avg['county_id'] = county_avg['FIPS_STR']
    
    scatter_data = clean_for_json(county_avg.to_dict('records'))
    with open(os.path.join(data_dir, 'county_scatter.json'), 'w') as f:
        json.dump(scatter_data, f)
    print(f"  Saved {len(scatter_data)} counties to county_scatter.json")
    
    # 2. State Map Data (Averaged across years)
    print("Preparing state map data...")
    state_avg = df.groupby('State_Abbrev').agg({
        'Fatality_Rate': 'mean',
        'Pct_Less_HS': 'mean',
        'Population': 'sum'  # Total state population
    }).reset_index()
    
    # Get average population per year, then average
    state_pop = df.groupby(['State_Abbrev', 'Year'])['Population'].sum().reset_index()
    state_pop_avg = state_pop.groupby('State_Abbrev')['Population'].mean().reset_index()
    state_avg = state_avg.drop('Population', axis=1).merge(state_pop_avg, on='State_Abbrev')
    
    # Drop NaN states
    state_avg = state_avg.dropna(subset=['State_Abbrev', 'Fatality_Rate'])
    
    state_data = clean_for_json(state_avg.to_dict('records'))
    with open(os.path.join(data_dir, 'state_data.json'), 'w') as f:
        json.dump(state_data, f)
    print(f"  Saved {len(state_data)} states to state_data.json")
    
    # 3. County Data grouped by State (for drill-down)
    print("Preparing county data by state...")
    county_by_state = {}
    for state in df['State_Abbrev'].unique():
        if state is None or (isinstance(state, float) and np.isnan(state)):
            continue
        state_counties = county_avg[county_avg['State_Abbrev'] == state].to_dict('records')
        county_by_state[state] = clean_for_json(state_counties)
    
    with open(os.path.join(data_dir, 'county_by_state.json'), 'w') as f:
        json.dump(county_by_state, f)
    print(f"  Saved county data for {len(county_by_state)} states")
    
    print("\nData preparation complete!")
    print(f"Files saved to: {data_dir}")

if __name__ == '__main__':
    prepare_dashboard_data()
