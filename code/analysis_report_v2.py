
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import seaborn as sns
import os
import matplotlib.gridspec as gridspec
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
import geopandas as gpd
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION & DESIGN SYSTEM ---
# Use the script's parent directory as base
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. CONSISTENT COLOR PALETTE
# We defined a strict dictionary to be used in ALL plots.
# COLORS = {
#     'primary': '#333333',    # Dark Grey (Neutral/Text)
#     'danger': '#E74C3C',     # Vermilion (High Risk/Red) - Colorblind Safe
#     'safety': '#27AE60',     # Bluish Green (Low Risk/Green) - Colorblind Safe
#     'education': '#56B4E9',  # Sky Blue (Education) - Colorblind Safe
#     'accent': '#F0E442',     # Yellow (Highlights) - Colorblind Safe
#     'text': '#333333',       
#     'grid': '#DDDDDD',       
#     'bg': '#FFFFFF'          
# }

COLORS = {
    'primary': '#333333',    # Dark Grey (Neutral/Text)
    'danger': '#D55E00',     # Vermilion (High Risk/Red) - Colorblind Safe
    'safety': '#009E73',     # Bluish Green (Low Risk/Green) - Colorblind Safe
    'education': '#56B4E9',  # Sky Blue (Education) - Colorblind Safe
    'accent': '#F0E442',     # Yellow (Highlights) - Colorblind Safe
    'text': '#333333',       
    'grid': '#DDDDDD',       
    'bg': '#FFFFFF'          
}

# COLORS = {
#     'primary': '#34495E',    # Dark Blue-Grey (Neutral/Data)
#     'danger': '#E74C3C',     # Red (High Risk, Low Edu)
#     'safety': '#27AE60',     # Green (Low Risk, High Edu)
#     'accent': '#F39C12',     # Orange/Yellow (Analysis/Highlight)
#     'text': '#2C3E50',       # Dark Text
#     'grid': '#BDC3C7',       # Light Grey Grid
#     'bg': '#FFFFFF'          # White Background
# }

# 2. GLOBAL PLOT SETTINGS
plt.style.use('seaborn-v0_8-white')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'sans-serif']
plt.rcParams['text.color'] = COLORS['text']
plt.rcParams['axes.labelcolor'] = COLORS['text']
plt.rcParams['xtick.color'] = COLORS['text']
plt.rcParams['ytick.color'] = COLORS['text']
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.titleweight'] = 'bold'
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'

def apply_theme(ax, title, xlabel, ylabel):
    """Uniform styling function for all axes."""
    ax.set_title(title, loc='left', pad=15, color=COLORS['primary'], fontweight='bold')
    ax.set_xlabel(xlabel, fontweight='medium')
    ax.set_ylabel(ylabel, fontweight='medium')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(COLORS['grid'])
    ax.spines['bottom'].set_color(COLORS['grid'])
    ax.grid(axis='y', color=COLORS['grid'], linestyle='--', linewidth=0.5, alpha=0.7)

# --- DATA LOADING (unchanged logic, optimized) ---
def load_data():
    print("Loading Data...")
    all_rows = []
    fips_map = {1:'AL', 2:'AK', 4:'AZ', 5:'AR', 6:'CA', 8:'CO', 9:'CT', 10:'DE', 11:'DC', 12:'FL', 13:'GA', 15:'HI', 16:'ID', 17:'IL', 18:'IN', 19:'IA', 20:'KS', 21:'KY', 22:'LA', 23:'ME', 24:'MD', 25:'MA', 26:'MI', 27:'MN', 28:'MS', 29:'MO', 30:'MT', 31:'NE', 32:'NV', 33:'NH', 34:'NJ', 35:'NM', 36:'NY', 37:'NC', 38:'ND', 39:'OH', 40:'OK', 41:'OR', 42:'PA', 44:'RI', 45:'SC', 46:'SD', 47:'TN', 48:'TX', 49:'UT', 50:'VT', 51:'VA', 53:'WA', 54:'WV', 55:'WI', 56:'WY'}
    
    # State Grid Coords (Reusable)
    state_coords = {
        'WA':(0,0), 'ID':(0,1), 'MT':(0,2), 'ND':(0,3), 'MN':(0,4), 'IL':(0,5), 'WI':(0,6), 'MI':(0,7), 'NY':(0,8), 'RI':(0,9), 'MA':(0,10),
        'OR':(1,0), 'NV':(1,1), 'WY':(1,2), 'SD':(1,3), 'IA':(1,4), 'IN':(1,5), 'OH':(1,6), 'PA':(1,7), 'NJ':(1,8), 'CT':(1,9), 'ME':(0,11),
        'CA':(2,0), 'UT':(2,1), 'CO':(2,2), 'NE':(2,3), 'MO':(2,4), 'KY':(2,5), 'WV':(2,6), 'VA':(2,7), 'MD':(2,8), 'DE':(2,9), 'NH':(1,11), 'VT':(1,10),
        'AZ':(3,1), 'NM':(3,2), 'KS':(3,3), 'AR':(3,4), 'TN':(3,5), 'NC':(3,6), 'SC':(3,7), 'DC':(3,8),
        'OK':(4,3), 'LA':(4,4), 'MS':(4,5), 'AL':(4,6), 'GA':(4,7),
        'HI':(5,0), 'AK':(5,1), 'TX':(5,3), 'FL':(5,8)
    }

    for year in range(2010, 2024):
        try:
            edu_path = os.path.join(DATA_DIR, f"Education{year}.csv")
            if not os.path.exists(edu_path): continue
            edu = pd.read_csv(edu_path, encoding='latin1', low_memory=False)
            
            # Find attrs
            attrs = edu['Attribute'].unique()
            c_attr, p_attr = None, None
            for a in attrs:
                if "less than" in str(a).lower() and "high school" in str(a).lower():
                    if "percent" in str(a).lower(): p_attr = a
                    else: c_attr = a
            if not c_attr: continue
            
            f_col = 'FIPS Code' if 'FIPS Code' in edu.columns else 'FIPS'
            if f_col not in edu.columns: continue
            
            # Clean
            edu['FIPS'] = pd.to_numeric(edu[f_col], errors='coerce')
            edu = edu[edu['FIPS'].notna()]
            edu = edu[edu['FIPS'] % 1000 != 0]
            
            piv = edu[edu['Attribute'].isin([c_attr, p_attr])].pivot(index='FIPS', columns='Attribute', values='Value').reset_index()
            piv['Count_Less_HS'] = pd.to_numeric(piv[c_attr], errors='coerce')
            piv['Pct_Less_HS'] = pd.to_numeric(piv[p_attr], errors='coerce')
            piv['Population'] = (piv['Count_Less_HS'] / (piv['Pct_Less_HS']/100))
            piv['FIPS_STR'] = piv['FIPS'].astype(int).astype(str).str.zfill(5)
            
            # FARS
            fdirs = [d for d in os.listdir(DATA_DIR) if f"FARS{year}" in d]
            if not fdirs: continue
            fars_dir = os.path.join(DATA_DIR, fdirs[0])
            acc_path = os.path.join(fars_dir, "ACCIDENT.CSV")
            if not os.path.exists(acc_path): acc_path = os.path.join(fars_dir, "accident.csv")
            if not os.path.exists(acc_path): continue
            
            acc = pd.read_csv(acc_path, encoding='latin1', low_memory=False)
            acc.columns = [c.upper() for c in acc.columns]
            acc['FIPS_STR'] = acc['STATE'].astype(str).str.zfill(2) + acc['COUNTY'].astype(str).str.zfill(3)
            
            # Factors
            acc['Drunk'] = acc['DRUNK_DR'].fillna(0).astype(int)
            w_col = 'WEATHER' if 'WEATHER' in acc.columns else 'WEATHER1'
            acc['Bad_Weather'] = acc[w_col].isin([2,3,4,10,11]).astype(int)
            acc['Dark'] = acc['LGT_COND'].isin([2,3]).astype(int)
            
            g = acc.groupby('FIPS_STR').agg({'ST_CASE':'count', 'FATALS':'sum', 'Drunk':'sum', 'Bad_Weather':'sum', 'Dark':'sum'}).reset_index()
            
            m = pd.merge(piv, g, on='FIPS_STR', how='left').fillna(0)
            m['Year'] = year
            m['State_Abbrev'] = m['FIPS_STR'].str[:2].astype(int).map(fips_map)
            all_rows.append(m)
        except: continue
        
    df = pd.concat(all_rows, ignore_index=True)
    df = df[df['Population'] > 0]
    
    # Calc Rates
    df['Fatality_Rate'] = (df['FATALS'] / df['Population']) * 100000
    df['Drunk_Pct'] = (df['Drunk'] / df['ST_CASE']) * 100
    df['Drunk_Rate_Per_100k'] = (df['Drunk'] / df['Population']) * 100000 # NEW METRIC
    df['Dark_Pct'] = (df['Dark'] / df['ST_CASE']) * 100
    df['Weather_Pct'] = (df['Bad_Weather'] / df['ST_CASE']) * 100
    
    df['Urbanicity'] = df['Population'].apply(lambda x: 'Urban' if x >= 50000 else 'Rural')
    df['Edu_Group'] = pd.qcut(df['Pct_Less_HS'], 4, labels=['High Edu (Low Risk)', 'Med-High', 'Med-Low', 'Low Edu (High Risk)'])
    
    return df, state_coords

# --- HELPER FUNCTIONS ---
def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, name))
    plt.close()
    print(f"Saved {name}")

# --- USA CHOROPLETH MAP GENERATOR ---
def plot_usa_choropleth(df, value_col, title, filename, cmap, agg_func='mean', legend_label=None):
    """Generates a proper USA choropleth map using actual state boundaries."""
    
    # Aggregate data by state
    if agg_func == 'mean':
        state_val = df.groupby('State_Abbrev')[value_col].mean().reset_index()
    else:
        state_val = df.groupby('State_Abbrev')[value_col].sum().reset_index()
    state_val.columns = ['STUSPS', value_col]
    
    # Human readable format for values
    def human_format(num):
        if pd.isna(num):
            return ''
        if num >= 1e6:
            return f'{num/1e6:.1f}M'
        if num >= 1e3:
            return f'{num/1e3:.0f}k'
        return f'{num:.1f}'
    
    # Load US states GeoJSON directly
    usa = gpd.read_file('https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json')
    
    # Create STUSPS from state names
    state_abbrev_map = {
        'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
        'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
        'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
        'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
        'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
        'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
        'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
        'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
        'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT',
        'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY',
        'District of Columbia': 'DC'
    }
    usa['STUSPS'] = usa['name'].map(state_abbrev_map)
    
    # Filter to continental US only
    # Exclude AK, HI, PR, and any unmapped territories (NaN STUSPS)
    usa_continental = usa[
        (~usa['STUSPS'].isin(['AK', 'HI', 'PR'])) & 
        (usa['STUSPS'].notna())
    ].copy()
    
    # Merge data
    usa_continental = usa_continental.merge(state_val, on='STUSPS', how='left')
    
    # Remove states without data (NaN values) to avoid distortion
    usa_continental = usa_continental[usa_continental[value_col].notna()]
    
    # Create figure
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    
    # Get colormap for determining text contrast
    cm = plt.get_cmap(cmap)
    vmin = usa_continental[value_col].min()
    vmax = usa_continental[value_col].max()
    norm = plt.Normalize(vmin=vmin, vmax=vmax)
    
    # Use custom legend label if provided, otherwise format from column name
    if legend_label is None:
        legend_label = value_col.replace('_', ' ').title()
    
    # Plot the map with subtle light gray edges (no built-in legend)
    usa_continental.plot(
        column=value_col,
        cmap=cmap,
        linewidth=0.8,  # Subtle border
        ax=ax,
        edgecolor='#CCCCCC',  # Light gray borders
        legend=False,  # We'll create our own colorbar
        missing_kwds={'color': 'lightgrey', 'label': 'No Data'}
    )
    
    # Create manual colorbar with full control
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = fig.colorbar(sm, ax=ax, orientation='horizontal', shrink=0.6, pad=0.02)
    cbar.set_label(legend_label, fontsize=12)
    cbar.ax.tick_params(labelsize=12)  # Larger tick font
    cbar.outline.set_visible(False)  # Remove border
    
    # Small states where labels would overlap - skip these
    small_states = ['RI', 'CT', 'NJ', 'DE', 'MD', 'DC', 'VT', 'NH', 'MA']
    
    # Add state abbreviation labels and values at centroids
    for idx, row in usa_continental.iterrows():
        state_abbrev = row['STUSPS']
        
        # Skip small states to avoid overlapping labels
        if state_abbrev in small_states:
            continue
        
        # Use representative_point() which guarantees a point inside the polygon
        # This works better than centroid for irregular shapes like FL, LA, MI
        rep_point = row.geometry.representative_point()
        label_x = rep_point.x
        label_y = rep_point.y
        
        val = row[value_col]
        val_text = human_format(val)
        
        # Determine text color based on background darkness
        if pd.notna(val):
            # Get the color for this value
            rgba = cm(norm(val))
            # Calculate luminance (brightness)
            luminance = 0.299 * rgba[0] + 0.587 * rgba[1] + 0.114 * rgba[2]
            # Use white text on dark backgrounds, black on light
            text_color = 'white' if luminance < 0.5 else COLORS['text']
        else:
            text_color = COLORS['text']
        
        # Add state abbreviation
        ax.annotate(
            text=state_abbrev,
            xy=(label_x, label_y + 0.3),  # Slightly above center
            ha='center',
            va='center',
            fontsize=12,
            fontweight='bold',
            color=text_color
        )
        
        # Add value below abbreviation
        if val_text:
            ax.annotate(
                text=val_text,
                xy=(label_x, label_y - 0.3),  # Slightly below center
                ha='center',
                va='center',
                fontsize=10,
                fontweight='bold',
                color=text_color
            )
    
    ax.axis('off')
    ax.set_title(title, fontsize=20, fontweight='bold', color=COLORS['primary'], pad=10, y=0.95)
    
    # Add source note
    fig.text(0.5, 0.02, 'Data: FARS & Census (2010-2023) | Continental US Only', 
             ha='center', fontsize=9, color='grey', style='italic')
    
    save(filename)

# --- POSTER INFOGRAPHIC (NEW PROFESSIONAL DESIGN) ---
def create_poster_infographic(df):
    """Generates a professional 'Tale of Two Worlds' comparison poster."""
    print("Generating Professional Poster Infographic...")
    
    # 1. Prepare Data: High Edu vs Low Edu (Quartiles)
    high_edu = df[df['Edu_Group'].str.contains('High Edu')] # Top Quartile
    low_edu = df[df['Edu_Group'].str.contains('Low Edu')]   # Bottom Quartile
    
    stats = {
        'high': {
            'fatality': high_edu['Fatality_Rate'].mean(),
            'alcohol': high_edu['Drunk_Rate_Per_100k'].mean(),
            'weather': high_edu['Weather_Pct'].mean(),
            'dark': high_edu['Dark_Pct'].mean(),
            'pop_label': "Urban / Suburban"
        },
        'low': {
            'fatality': low_edu['Fatality_Rate'].mean(),
            'alcohol': low_edu['Drunk_Rate_Per_100k'].mean(),
            'weather': low_edu['Weather_Pct'].mean(),
            'dark': low_edu['Dark_Pct'].mean(),
            'pop_label': "Rural / Isolated"
        }
    }
    
    # Setup Canvas
    fig = plt.figure(figsize=(16, 12))
    fig.patch.set_facecolor('#F4F6F6') # Light Neutral Grey Background
    gs = gridspec.GridSpec(10, 2)
    
    # --- HEADER ---
    ax_header = fig.add_subplot(gs[0:2, :])
    ax_header.axis('off')
    ax_header.text(0.5, 0.7, "THE EDUCATION SAFETY GAP", ha='center', va='center', fontsize=32, fontweight='extra bold', color=COLORS['primary'])
    ax_header.text(0.5, 0.35, "How Educational Attainment Correlates with Traffic Mortality (2010-2023)", ha='center', va='center', fontsize=16, color=COLORS['text'])
    ax_header.axhline(y=0.1, xmin=0.1, xmax=0.9, color=COLORS['grid'], linewidth=2)

    # --- LEFT PANEL (HIGH EDU / SAFE) ---
    ax_left = fig.add_subplot(gs[2:9, 0])
    ax_left.axis('off')
    
    # Background Box
    rect_left = plt.Rectangle((0.05, 0), 0.9, 1, transform=ax_left.transAxes, color='white', zorder=0)
    ax_left.add_patch(rect_left)
    ax_left.text(0.5, 0.92, "HIGH GRADUATION RATE", transform=ax_left.transAxes, ha='center', fontsize=18, fontweight='bold', color=COLORS['safety'])
    ax_left.text(0.5, 0.88, stats['high']['pop_label'], transform=ax_left.transAxes, ha='center', fontsize=12, style='italic', color='#7F8C8D')

    # Main Metric: Fatality Rate
    ax_left.text(0.5, 0.75, f"{stats['high']['fatality']:.1f}", transform=ax_left.transAxes, ha='center', fontsize=70, fontweight='bold', color=COLORS['safety'])
    ax_left.text(0.5, 0.68, "Fatalities per 100k", transform=ax_left.transAxes, ha='center', fontsize=12, color=COLORS['text'])
    
    # Secondary Metrics
    y_start = 0.50
    gap = 0.12
    
    # Alcohol
    ax_left.text(0.5, y_start, "Alcohol Incidents / 100k", transform=ax_left.transAxes, ha='center', fontsize=10, fontweight='bold', color=COLORS['primary'])
    ax_left.text(0.5, y_start-0.05, f"{stats['high']['alcohol']:.1f}", transform=ax_left.transAxes, ha='center', fontsize=28, fontweight='bold', color=COLORS['safety'])
    
    # Dark
    ax_left.text(0.5, y_start-gap, "Low Light Crash (Pct)", transform=ax_left.transAxes, ha='center', fontsize=10, fontweight='bold', color=COLORS['primary'])
    ax_left.text(0.5, y_start-gap-0.05, f"{stats['high']['dark']:.1f}%", transform=ax_left.transAxes, ha='center', fontsize=28, fontweight='bold', color=COLORS['safety'])

    # --- RIGHT PANEL (LOW EDU / RISKY) ---
    ax_right = fig.add_subplot(gs[2:9, 1])
    ax_right.axis('off')
    
    # Background Box
    rect_right = plt.Rectangle((0.05, 0), 0.9, 1, transform=ax_right.transAxes, color='white', zorder=0)
    ax_right.add_patch(rect_right)
    ax_right.text(0.5, 0.92, "LOW GRADUATION RATE", transform=ax_right.transAxes, ha='center', fontsize=18, fontweight='bold', color=COLORS['danger'])
    ax_right.text(0.5, 0.88, stats['low']['pop_label'], transform=ax_right.transAxes, ha='center', fontsize=12, style='italic', color='#7F8C8D')

    # Main Metric: Fatality Rate
    ax_right.text(0.5, 0.75, f"{stats['low']['fatality']:.1f}", transform=ax_right.transAxes, ha='center', fontsize=70, fontweight='bold', color=COLORS['danger'])
    ax_right.text(0.5, 0.68, "Fatalities per 100k", transform=ax_right.transAxes, ha='center', fontsize=12, color=COLORS['text'])
    
    # Secondary Metrics
    # Alcohol
    ax_right.text(0.5, y_start, "Alcohol Incidents / 100k", transform=ax_right.transAxes, ha='center', fontsize=10, fontweight='bold', color=COLORS['primary'])
    ax_right.text(0.5, y_start-0.05, f"{stats['low']['alcohol']:.1f}", transform=ax_right.transAxes, ha='center', fontsize=28, fontweight='bold', color=COLORS['danger'])
    
    # Dark
    ax_right.text(0.5, y_start-gap, "Low Light Crash (Pct)", transform=ax_right.transAxes, ha='center', fontsize=10, fontweight='bold', color=COLORS['primary'])
    ax_right.text(0.5, y_start-gap-0.05, f"{stats['low']['dark']:.1f}%", transform=ax_right.transAxes, ha='center', fontsize=28, fontweight='bold', color=COLORS['danger'])

    # --- CROSS COMPARISON (Visual Bars) ---
    # Add small visual bars under the numbers
    def draw_bar(ax, x, y, val, max_val, color):
        width = (val / max_val) * 0.4
        rect = plt.Rectangle((x - width/2, y), width, 0.015, transform=ax.transAxes, color=color)
        ax.add_patch(rect)
        # Background bar
        rect_bg = plt.Rectangle((x - 0.2, y), 0.4, 0.015, transform=ax.transAxes, color='#ECF0F1', zorder=-1)
        ax.add_patch(rect_bg)

    # Max values for scaling
    max_alc = max(stats['high']['alcohol'], stats['low']['alcohol']) * 1.2
    max_drk = max(stats['high']['dark'], stats['low']['dark']) * 1.2

    draw_bar(ax_left, 0.5, y_start-0.07, stats['high']['alcohol'], max_alc, COLORS['safety'])
    draw_bar(ax_left, 0.5, y_start-gap-0.07, stats['high']['dark'], max_drk, COLORS['safety'])
    
    draw_bar(ax_right, 0.5, y_start-0.07, stats['low']['alcohol'], max_alc, COLORS['danger'])
    draw_bar(ax_right, 0.5, y_start-gap-0.07, stats['low']['dark'], max_drk, COLORS['danger'])

    # --- FOOTER ---
    ax_footer = fig.add_subplot(gs[9, :])
    ax_footer.axis('off')
    ratio = stats['low']['fatality'] / stats['high']['fatality']
    ax_footer.text(0.5, 0.5, f"KEY INSIGHT: Rural, low-education counties face a {ratio:.1f}x higher risk of death per capita.", 
                   ha='center', va='center', fontsize=16, fontweight='bold', color='white', 
                   bbox=dict(facecolor=COLORS['primary'], edgecolor='none', boxstyle='round,pad=1'))

    save("INFOGRAPHIC_Composite.png")

# --- EDA GRAPH SUITE ---
def run_eda(df):
    print("Generating EDA Graphs...")
    
    # 1. Fatality Rate Trend (COLORS['danger'])
    plt.figure()
    d = df.groupby('Year')['Fatality_Rate'].mean().reset_index()
    sns.lineplot(data=d, x='Year', y='Fatality_Rate', color=COLORS['danger'], linewidth=3, marker='o')
    apply_theme(plt.gca(), "1. Avg Fatality Rate Over Time", "Year", "Fatalities per 100k")
    plt.ylim(bottom=0) # START AT 0
    save("EDA_01_Trend_Fatality.png")
    
    # 2. Total Accidents vs Fatalities (Dual Axis)
    # 2. Total Accidents vs Fatalities (Dual Axis) - IMPROVED
    d2 = df.groupby('Year')[['FATALS', 'ST_CASE']].sum().reset_index()
    fig, ax1 = plt.subplots(figsize=(10,6))
    
    # Left Axis: Accidents (Education Color / Blue)
    ax1.bar(d2['Year'], d2['ST_CASE'], color=COLORS['education'], alpha=0.3)
    ax1.set_xlabel("Year", fontweight='bold')
    ax1.set_ylabel("Total Accidents (Millions)", color=COLORS['education'], fontweight='bold')
    ax1.tick_params(axis='y', colors=COLORS['education'])
    ax1.spines['left'].set_color(COLORS['education'])
    ax1.spines['left'].set_linewidth(2)
    
    # Right Axis: Fatalities (Danger Color / Red)
    ax2 = ax1.twinx()
    ax2.plot(d2['Year'], d2['FATALS'], color=COLORS['danger'], linewidth=4, marker='D', markersize=8)
    ax2.set_ylabel("Total Fatalities", color=COLORS['danger'], fontweight='bold')
    ax2.tick_params(axis='y', colors=COLORS['danger'])
    ax2.spines['right'].set_color(COLORS['danger'])
    ax2.spines['right'].set_linewidth(2)
    
    # Clean other spines
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False) # Hide primary right
    ax2.spines['left'].set_visible(False)  # Hide secondary left
    
    # Unified Legend
    legend_elements = [
        Patch(facecolor=COLORS['education'], alpha=0.3, label='Total Accidents (Left Scale)'),
        Line2D([0], [0], color=COLORS['danger'], lw=4, marker='D', label='Total Fatalities (Right Scale)')
    ]
    ax1.legend(handles=legend_elements, loc='upper center', ncol=2, frameon=False, fontsize=10)
    
    # Title
    ax1.set_title("2. Volume vs. Lethality: Accidents are Flat, but Deaths are Rising", 
                  loc='left', pad=20, color=COLORS['primary'], fontweight='bold', fontsize=14)
    ax1.grid(axis='y', linestyle='--', alpha=0.3)
    
    save("EDA_02_Dual_Totals.png")
    
    # 3. Fatality Distribution (Hist)
    plt.figure()
    sns.histplot(df['Fatality_Rate'], bins=80, color=COLORS['primary'], kde=True, line_kws={'linewidth':2})
    apply_theme(plt.gca(), "3. Distribution of Fatality Rates", "Fatality Rate", "Count of Counties")
    plt.xlim(0, 100)
    save("EDA_03_Dist_Fatality.png")
    
    # 4. Urban vs Rural Boxplot
    plt.figure()
    sns.boxplot(data=df, x='Urbanicity', y='Fatality_Rate', palette=[COLORS['danger'], COLORS['safety']]) # Rural=Red, Urban=Green (Approx)
    apply_theme(plt.gca(), "4. Rural vs Urban Safety Gap", "Area Type", "Fatality Rate")
    plt.ylim(0, 150)
    save("EDA_04_Box_Urbanicity.png")
    
    # 5. Edu Group Bar Chart
    plt.figure()
    o = ['High Edu (Low Risk)', 'Med-High', 'Med-Low', 'Low Edu (High Risk)']
    sns.barplot(data=df, x='Edu_Group', y='Fatality_Rate', order=o, palette="Blues_d")
    apply_theme(plt.gca(), "5. Fatality Rate by Education Level", "", "Avg Fatality Rate")
    save("EDA_05_Bar_Edu.png")
    
    # 6. Scatter Edu vs Fatality (County Averages)
    plt.figure()
    # Average each county across all years for a stable representation
    county_avg = df.groupby('FIPS_STR').agg({
        'Pct_Less_HS': 'mean',
        'Fatality_Rate': 'mean',
        'Urbanicity': 'first'  # Use the most common urbanicity classification
    }).reset_index()
    sns.scatterplot(data=county_avg, x='Pct_Less_HS', y='Fatality_Rate', hue='Urbanicity', palette={'Rural':COLORS['danger'], 'Urban':COLORS['safety']}, alpha=0.3)
    apply_theme(plt.gca(), "6. Education vs Fatality Correlation", "% Without High School Diploma", "Fatalities per 100k Population")
    plt.ylim(0, 150)
    save("EDA_06_Scatter_Corr.png")
    
    # 7. Alcohol Trend by Edu - FIXED METRIC
    plt.figure()
    d7 = df.groupby(['Year', 'Edu_Group'])['Drunk_Rate_Per_100k'].mean().reset_index()
    sns.lineplot(data=d7, x='Year', y='Drunk_Rate_Per_100k', hue='Edu_Group', palette=[COLORS['safety'], COLORS['education'], COLORS['danger'], '#000000']) # Custom discrete
    apply_theme(plt.gca(), "7. Alcohol Fatalities per 100k Population", "Year", "Alcohol Incidents / 100k")
    plt.ylim(bottom=0)
    save("EDA_07_Line_Alcohol.png")
    
    # 8. Dark Accidents Bar
    plt.figure()
    palette = [
    COLORS['safety'],
    COLORS['education'],
    COLORS['danger'],
    '#4D4D4D'   # dark gray (WCAG friendly)
    ]

    sns.barplot(
        data=df,
        x='Edu_Group',
        y='Dark_Pct',
        palette=palette,
        order=o
    )
    apply_theme(plt.gca(), "8. Night Time Accidents by Education", "", "% Dark Accidents")
    save("EDA_08_Bar_Dark.png")
    
    # 9. Hexbin Density (Fixed labels)
    plt.figure()
    hb = plt.hexbin(df['Pct_Less_HS'], df['Fatality_Rate'], gridsize=25, cmap='inferno', bins='log')
    cb = plt.colorbar(hb)
    cb.set_label("Count of Counties (Log Scale)")
    apply_theme(plt.gca(), "9. Risk Density: Education vs Fatality", "% Less Than HS", "Fatality Rate")
    plt.ylim(0, 150)
    save("EDA_09_Hex_Density.png")
    
    # 10. Correlation Heatmap
    plt.figure()
    c = df[['Fatality_Rate', 'Pct_Less_HS', 'Drunk_Pct', 'Dark_Pct', 'Population']].corr()
    sns.heatmap(c, annot=True, fmt=".2f", cmap='RdBu_r', center=0)
    plt.title("10. Correlation Matrix", fontweight='bold', color=COLORS['primary'])
    save("EDA_10_Corr_Heatmap.png")
    
    # 11-20 Simplified Variations
    # 11. Alcohol vs Fatality Scatter
    plt.figure()
    sns.scatterplot(data=df.sample(5000), x='Drunk_Pct', y='Fatality_Rate', color=COLORS['danger'], alpha=0.1)
    apply_theme(plt.gca(), "11. Alcohol % vs Fatality Rate", "% Alcohol Accidents", "Fatality Rate")
    save("EDA_11_Scatter_Alcohol.png")
    
    # 12. Top 10 Deadliest States
    plt.figure()
    top10 = df.groupby('State_Abbrev')['Fatality_Rate'].mean().sort_values(ascending=False).head(10).reset_index()
    sns.barplot(data=top10, y='State_Abbrev', x='Fatality_Rate', palette='Reds_r')
    apply_theme(plt.gca(), "12. Highest Risk States", "Fatality Rate", "")
    save("EDA_12_Bar_States.png")
    
    # 13. Weather Impact Scatter (Weak)
    plt.figure()
    sns.scatterplot(data=df.sample(5000), x='Weather_Pct', y='Fatality_Rate', color=COLORS['primary'], alpha=0.1)
    apply_theme(plt.gca(), "13. Weather Impact (Weak Correlation)", "% Bad Weather", "Fatality Rate")
    save("EDA_13_Scatter_Weather.png")
    
    # 14. Population Log Scatter
    plt.figure()
    sns.scatterplot(data=df.sample(5000), x='Population', y='Fatality_Rate', color=COLORS['accent'], alpha=0.3)
    plt.xscale('log')
    apply_theme(plt.gca(), "14. Population Scale vs Risk", "Population (Log)", "Fatality Rate")
    save("EDA_14_Scatter_Pop.png")
    
    # 15. Alcohol Dist
    plt.figure()
    sns.kdeplot(df['Drunk_Pct'], fill=True, color=COLORS['danger'])
    apply_theme(plt.gca(), "15. Distribution of Alcohol Involvement", "% Accidents with Drunk Driver", "Density")
    save("EDA_15_KDE_Alcohol.png")

# --- EXDA & MAPS ---
def run_exda_and_maps(df, state_coords):
    print("Generating ExDA and Maps...")
    
    # MAPS - Using proper USA choropleth maps with custom legend labels
    plot_usa_choropleth(df, 'Fatality_Rate', "Average Fatality Rate by State", "MAP_Fatality_Rate.png", 'Reds', 'mean', 
                        legend_label="Fatalities per 100k Population")
    plot_usa_choropleth(df, 'Pct_Less_HS', "Population without High School Diploma (%)", "MAP_Education.png", 'Blues', 'mean',
                        legend_label="% Without High School Diploma")
    
    # Fix Population Map: Verify we are averaging the *State Totals*, not averaging County Pops
    # 1. Sum Population by State and Year
    pop_agg = df.groupby(['State_Abbrev', 'Year'])['Population'].sum().reset_index()
    # 2. Plot the Mean of these Annual Totals
    plot_usa_choropleth(pop_agg, 'Population', "Avg State Population (2010-2023)", "MAP_Population.png", 'Greens', 'mean',
                        legend_label="Population in Millions")

    # ExDA 1: Feature Importance
    # ExDA 1: Feature Importance - RENAMED LABELS
    plt.figure()
    f = df[['Fatality_Rate', 'Pct_Less_HS', 'Drunk_Rate_Per_100k', 'Dark_Pct', 'Population', 'Weather_Pct']].dropna()
    rf = RandomForestRegressor(n_estimators=50).fit(f.drop('Fatality_Rate', axis=1), f['Fatality_Rate'])
    imp = pd.DataFrame({'Feature':f.drop('Fatality_Rate', axis=1).columns, 'Importance':rf.feature_importances_}).sort_values('Importance', ascending=False)
    
    # Rename for Audience
    name_map = {
        'Pct_Less_HS': 'Education Level',
        'Drunk_Rate_Per_100k': 'Alcohol Incidents',
        'Dark_Pct': 'Lighting Conditions',
        'Population': 'Population Density',
        'Weather_Pct': 'Bad Weather'
    }
    imp['Feature'] = imp['Feature'].map(name_map)
    
    sns.barplot(data=imp, x='Importance', y='Feature', color=COLORS['education'])
    apply_theme(plt.gca(), "ExDA 1: Risk Factors Ranked by Importance", "Relative Importance", "Factor")
    save("EXDA_01_Feature_Imp.png")
    
    # ExDA 2: Cluster Heatmap
    ccols = ['Fatality_Rate', 'Pct_Less_HS', 'Drunk_Pct']
    cdata = df[ccols].dropna()
    km = KMeans(n_clusters=3, random_state=42).fit(StandardScaler().fit_transform(cdata))
    cdata['Cluster'] = km.labels_
    means = cdata.groupby('Cluster').mean().sort_values('Fatality_Rate')
    means.index = ['Safe', 'Mixed', 'Danger']
    plt.figure()
    sns.heatmap((means-means.min())/(means.max()-means.min()), annot=means.round(1), cmap='Reds')
    plt.title("ExDA 2: Cluster Profiles", fontweight='bold', color=COLORS['primary'])
    save("EXDA_02_Cluster_Heatmap.png")

# --- MAIN ---
def main():
    df, state_coords = load_data()
    print(f"Loaded {len(df)} records.")
    
    create_poster_infographic(df) # The New Professional Poster
    run_eda(df)
    run_exda_and_maps(df, state_coords)
    print("Done.")

if __name__ == "__main__":
    main()
