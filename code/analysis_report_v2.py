
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import matplotlib.gridspec as gridspec
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION & DESIGN SYSTEM ---
BASE_DIR = r"d:\Projects\DataVis Project"
DATA_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. CONSISTENT COLOR PALETTE
# We defined a strict dictionary to be used in ALL plots.
COLORS = {
    'primary': '#34495E',    # Dark Blue-Grey (Neutral/Data)
    'danger': '#E74C3C',     # Red (High Risk, Low Edu)
    'safety': '#27AE60',     # Green (Low Risk, High Edu)
    'accent': '#F39C12',     # Orange/Yellow (Analysis/Highlight)
    'text': '#2C3E50',       # Dark Text
    'grid': '#BDC3C7',       # Light Grey Grid
    'bg': '#FFFFFF'          # White Background
}

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

# --- MAP GENERATOR (REFINED) ---
def plot_state_grid(df, state_coords, value_col, title, filename, cmap, agg_func='mean'):
    """Generates a tile grid map for any metric."""
    if agg_func == 'mean':
        state_val = df.groupby('State_Abbrev')[value_col].mean()
        label_fmt = "{:.1f}"
    else: # sum
        state_val = df.groupby('State_Abbrev')[value_col].sum()
        label_fmt = "{:,.0f}"

    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_aspect('equal')
    ax.axis('off')
    
    norm = plt.Normalize(state_val.min(), state_val.max())
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    
    for state, (row, col) in state_coords.items():
        val = state_val.get(state, np.nan)
        color = sm.to_rgba(val) if not np.isnan(val) else '#EEEEEE'
        
        # Tile
        rect = plt.Rectangle((col, -row), 1, 1, facecolor=color, edgecolor='white', linewidth=1.5)
        ax.add_patch(rect)
        
        # Label
        contrast_color = 'white' if np.mean(color[:3]) < 0.5 else COLORS['text']
        ax.text(col+0.5, -row+0.6, state, ha='center', va='center', fontweight='bold', color=contrast_color, fontsize=11)
        if not np.isnan(val):
            val_txt = label_fmt.format(val)
            if agg_func == 'sum' and val > 1000000: # Abbreviate millions
                 val_txt = f"{val/1000000:.1f}M"
            ax.text(col+0.5, -row+0.3, val_txt, ha='center', va='center', fontsize=9, color=contrast_color)

    plt.xlim(-0.5, 12.5)
    plt.ylim(-6.5, 1.5)
    
    # Title & Legend
    ax.set_title(title, fontsize=20, fontweight='bold', color=COLORS['primary'], pad=20)
    cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.04)
    cbar.outline.set_visible(False)
    
    save(filename)

# --- COMPLEX INFOGRAPHIC (RESTORED) ---
def create_complex_infographic(df):
    """Restores the requested 'Old Style' composite infographic."""
    print("Generating Composite Infographic...")
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1, 1])
    
    # Main Header Area (Implicit in top chart)
    fig.suptitle("The Hidden Cost of Inequality on American Roads\nAnalysis of 14 Years of Fatality & Education Data (2010-2023)", 
                 fontsize=24, fontweight='bold', color=COLORS['primary'], y=0.98)
    
    # 1. Main Trend Line (Top Left spanning 2 cols)
    ax1 = fig.add_subplot(gs[0, :2])
    d_trend = df.groupby('Year')['Fatality_Rate'].mean().reset_index()
    sns.lineplot(data=d_trend, x='Year', y='Fatality_Rate', ax=ax1, color=COLORS['danger'], linewidth=4, marker='o', markersize=8)
    apply_theme(ax1, "Rising Fatality Rates Per Capita (2010-2023)", "Year", "Fatalities / 100k")
    
    # 2. Key Stats (Top Right)
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.axis('off')
    low_edu_rate = df[df['Edu_Group'] == 'Low Edu (High Risk)']['Fatality_Rate'].mean()
    high_edu_rate = df[df['Edu_Group'] == 'High Edu (Low Risk)']['Fatality_Rate'].mean()
    
    ax2.text(0.5, 0.8, "The Education Gap", ha='center', fontsize=20, fontweight='bold', color=COLORS['text'])
    ax2.text(0.5, 0.6, f"{low_edu_rate:.1f}", ha='center', fontsize=60, fontweight='bold', color=COLORS['danger'])
    ax2.text(0.5, 0.5, "Fatalities/100k in Low Edu Counties", ha='center', fontsize=12, color=COLORS['text'])
    ax2.text(0.5, 0.4, "vs", ha='center', fontsize=16, style='italic', color=COLORS['grid'])
    ax2.text(0.5, 0.25, f"{high_edu_rate:.1f}", ha='center', fontsize=40, fontweight='bold', color=COLORS['safety'])
    ax2.text(0.5, 0.15, "in High Edu Counties", ha='center', fontsize=12, color=COLORS['text'])

    # 3. Bar Chart (Bottom Left)
    ax3 = fig.add_subplot(gs[1, 0])
    d_alc = df.groupby('Edu_Group')['Drunk_Pct'].mean().reset_index()
    # Ensure correct order
    d_alc = d_alc.sort_index(ascending=False) # Plot Low Risky first? No, let's follow index
    sns.barplot(data=d_alc, x='Edu_Group', y='Drunk_Pct', palette="Reds", ax=ax3)
    ax3.set_xticklabels(['High Edu', 'Med-High', 'Med-Low', 'Low Edu'], fontsize=9)
    apply_theme(ax3, "Alcohol Factor %", "Education Group", "% Drunk Driving")

    # 4. Scatter Plot (Bottom Middle)
    ax4 = fig.add_subplot(gs[1, 1])
    smp = df.sample(3000)
    sns.scatterplot(data=smp, x='Pct_Less_HS', y='Fatality_Rate', hue='Urbanicity', palette={'Urban':COLORS['accent'], 'Rural':COLORS['danger']}, alpha=0.4, s=20, ax=ax4, legend=False)
    # Fake legend
    ax4.text(0.95, 0.95, "• Rural", color=COLORS['danger'], transform=ax4.transAxes, ha='right', fontweight='bold')
    ax4.text(0.95, 0.90, "• Urban", color=COLORS['accent'], transform=ax4.transAxes, ha='right', fontweight='bold')
    apply_theme(ax4, "Education vs. Risk", "% Less than HS", "Fatality Rate")

    # 5. Box Plot (Bottom Right)
    ax5 = fig.add_subplot(gs[1, 2])
    sns.boxplot(data=df, x='Urbanicity', y='Fatality_Rate', palette={'Urban':COLORS['safety'], 'Rural':COLORS['danger']}, ax=ax5)
    apply_theme(ax5, "Urban vs. Rural Risk", "Urbanicity", "Fatality Rate")
    
    # Footer
    fig.text(0.5, 0.02, "CONCLUSION: Communities with lower education levels face significantly higher risks, largely driven by rural infrastructure challenges and higher rates of alcohol involvement.", 
             ha='center', fontsize=12, style='italic', backgroundcolor='#ecf0f1')
    
    save("INFOGRAPHIC_Composite.png")

# --- EDA GRAPH SUITE ---
def run_eda(df):
    print("Generating EDA Graphs...")
    
    # 1. Fatality Rate Trend (COLORS['danger'])
    plt.figure()
    d = df.groupby('Year')['Fatality_Rate'].mean().reset_index()
    sns.lineplot(data=d, x='Year', y='Fatality_Rate', color=COLORS['danger'], linewidth=3, marker='o')
    apply_theme(plt.gca(), "1. Avg Fatality Rate Over Time", "Year", "Fatalities per 100k")
    save("EDA_01_Trend_Fatality.png")
    
    # 2. Total Accidents vs Fatalities (Dual Axis)
    d2 = df.groupby('Year')[['FATALS', 'ST_CASE']].sum().reset_index()
    fig, ax1 = plt.subplots(figsize=(10,6))
    ax1.bar(d2['Year'], d2['ST_CASE'], color=COLORS['primary'], alpha=0.3, label='Accidents')
    ax2 = ax1.twinx()
    ax2.plot(d2['Year'], d2['FATALS'], color=COLORS['danger'], linewidth=3, marker='D', label='Fatalities')
    apply_theme(ax1, "2. Total Accidents vs Fatalities", "Year", "Accidents")
    ax2.set_ylabel("Fatalities", color=COLORS['danger'])
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
    
    # 6. Scatter Edu vs Fatality
    plt.figure()
    sns.scatterplot(data=df.sample(5000), x='Pct_Less_HS', y='Fatality_Rate', hue='Urbanicity', palette={'Rural':COLORS['danger'], 'Urban':COLORS['safety']}, alpha=0.3)
    apply_theme(plt.gca(), "6. Education vs Fatality Correlation", "% Less Than HS", "Fatality Rate")
    plt.ylim(0, 150)
    save("EDA_06_Scatter_Corr.png")
    
    # 7. Alcohol Trend by Edu
    plt.figure()
    d7 = df.groupby(['Year', 'Edu_Group'])['Drunk_Pct'].mean().reset_index()
    sns.lineplot(data=d7, x='Year', y='Drunk_Pct', hue='Edu_Group', palette="magma")
    apply_theme(plt.gca(), "7. Alcohol Involvement Trends by Group", "Year", "% Accidents with Alcohol")
    save("EDA_07_Line_Alcohol.png")
    
    # 8. Dark Accidents Bar
    plt.figure()
    sns.barplot(data=df, x='Edu_Group', y='Dark_Pct', palette="cividis", order=o)
    apply_theme(plt.gca(), "8. Nighttime Accidents by Education", "", "% Dark Accidents")
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
    
    # MAPS
    plot_state_grid(df, state_coords, 'Fatality_Rate', "Average Fatality Rate by State", "MAP_Fatality_Rate.png", 'Reds', 'mean')
    plot_state_grid(df, state_coords, 'Pct_Less_HS', "Average % Less Than HS by State", "MAP_Education.png", 'Blues', 'mean')
    plot_state_grid(df, state_coords, 'Population', "Total State Population (2010-2023 Avg)", "MAP_Population.png", 'Greens', 'sum')

    # ExDA 1: Feature Importance
    plt.figure()
    f = df[['Fatality_Rate', 'Pct_Less_HS', 'Drunk_Pct', 'Dark_Pct', 'Population']].dropna()
    rf = RandomForestRegressor(n_estimators=50).fit(f.drop('Fatality_Rate', axis=1), f['Fatality_Rate'])
    imp = pd.DataFrame({'Feature':f.drop('Fatality_Rate', axis=1).columns, 'Importance':rf.feature_importances_}).sort_values('Importance', ascending=False)
    sns.barplot(data=imp, x='Importance', y='Feature', palette='viridis')
    apply_theme(plt.gca(), "ExDA 1: What drives Fatality Rate?", "Importance", "Factor")
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
    
    create_complex_infographic(df) # The "Old Style" one
    run_eda(df)
    run_exda_and_maps(df, state_coords)
    print("Done.")

if __name__ == "__main__":
    main()
