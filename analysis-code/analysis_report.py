
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import statsmodels.api as sm
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
BASE_DIR = r"d:\Projects\DataVis Project"
DATA_DIR = os.path.join(BASE_DIR, "datasets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CODE_DIR = os.path.join(BASE_DIR, "code")

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Plotting Style
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk")
sns.set_palette("viridis")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['savefig.dpi'] = 300

# --- DATA PROCESSING FUNCTIONS ---

def get_education_attributes(df, year):
    """Dynamically find attributes for a given year."""
    attrs = df['Attribute'].unique()
    count_attr = None
    pct_attr = None
    
    # Heuristics for attribute interpretation across years
    for a in attrs:
        a_lower = str(a).lower()
        if "less than" in a_lower and "high school" in a_lower:
            if "percent" in a_lower:
                pct_attr = a
            else:
                count_attr = a
    return count_attr, pct_attr

def load_and_process_data(start_year=2010, end_year=2023):
    """
    Loads FARS and Education data, merges them, and creates a master DataFrame.
    This consolidates logic from ali.ipynb, meerab.ipynb, and nafeel.ipynb.
    """
    print("--- Loading and Processing Data ---")
    all_data = []

    for year in range(start_year, end_year + 1):
        print(f"Processing {year}...", end=" ")
        try:
            # 1. Load Education Data
            edu_path = os.path.join(DATA_DIR, f"Education{year}.csv")
            if not os.path.exists(edu_path):
                print(f"Skipping {year} (Edu file missing)")
                continue
                
            edu_df = pd.read_csv(edu_path, encoding='latin1', low_memory=False)
            count_attr, pct_attr = get_education_attributes(edu_df, year)
            
            if not count_attr or not pct_attr:
                print(f"Skipping {year} (Attributes not found)")
                continue

            # Filter & Pivot Education
            # Filter for counties (roughly FIPS 1000-56999, excluding state/national totals)
            # Note: Specific logic adapted to ensure we get counties
            edu_subset = edu_df[edu_df['Attribute'].isin([count_attr, pct_attr])].copy()
            
            # Standardize FIPS column name
            fips_col = 'FIPS Code' if 'FIPS Code' in edu_subset.columns else 'FIPS'
            if fips_col not in edu_subset.columns: # fallback
                 print(f"Skipping {year} (No FIPS col found)")
                 continue

            edu_subset['FIPS'] = pd.to_numeric(edu_subset[fips_col], errors='coerce')
            edu_subset = edu_subset.dropna(subset=['FIPS'])
            edu_subset = edu_subset[(edu_subset['FIPS'] % 1000 != 0)] # Exclude state totals
            
            edu_pivot = edu_subset.pivot(index='FIPS', columns='Attribute', values='Value').reset_index()
            
            # Clean Pivot
            edu_pivot['FIPS'] = edu_pivot['FIPS'].astype(int).astype(str).str.zfill(5)
            edu_pivot['Count_Less_HS'] = pd.to_numeric(edu_pivot[count_attr], errors='coerce')
            edu_pivot['Pct_Less_HS'] = pd.to_numeric(edu_pivot[pct_attr], errors='coerce')
            
            # Calculate Population (Reverse Engineering)
            # Pop = Count / (Pct / 100)
            edu_pivot['Population'] = (edu_pivot['Count_Less_HS'] / (edu_pivot['Pct_Less_HS'] / 100))
            edu_pivot = edu_pivot.dropna(subset=['Population'])
            edu_pivot = edu_pivot[edu_pivot['Population'] > 0]
            
            # Education Level Groups (Quartiles per year)
            edu_pivot['Edu_Quantile'] = pd.qcut(edu_pivot['Pct_Less_HS'], 4, labels=['High Edu', 'Med-High Edu', 'Med-Low Edu', 'Low Edu'])

            # 2. Load FARS Data
            fars_dir = os.path.join(DATA_DIR, f"FARS{year}")
            acc_file = os.path.join(fars_dir, "ACCIDENT.CSV")
            if not os.path.exists(acc_file): acc_file = os.path.join(fars_dir, "accident.csv")
            
            person_file = os.path.join(fars_dir, "PERSON.CSV")
            if not os.path.exists(person_file): person_file = os.path.join(fars_dir, "person.csv")
            
            vehicle_file = os.path.join(fars_dir, "VEHICLE.CSV")
            if not os.path.exists(vehicle_file): vehicle_file = os.path.join(fars_dir, "vehicle.csv")

            if not os.path.exists(acc_file):
                print(f"Skipping {year} (Accident file missing)")
                continue

            acc_df = pd.read_csv(acc_file, encoding='latin1', low_memory=False)
            acc_df.columns = [c.upper() for c in acc_df.columns]
            
            # Create FIPS
            acc_df['FIPS'] = acc_df['STATE'].astype(str).str.zfill(2) + acc_df['COUNTY'].astype(str).str.zfill(3)
            
            # Aggregate Accident Data
            # Factors: Weather, Light, Drunk, Speeding
            
            # Weather (2=Rain, 3=Sleet, 4=Snow)
            w_col = 'WEATHER' if 'WEATHER' in acc_df.columns else 'WEATHER1' # Handle schema drift
            acc_df['Is_Adverse_Weather'] = acc_df[w_col].isin([2, 3, 4, 10, 11]).astype(int) # Standardize codes
            
            # Light (2=Dark, 3=Dark-Lighted) -> Focus on Dark (2)
            l_col = 'LGT_COND'
            acc_df['Is_Dark'] = (acc_df[l_col] == 2).astype(int)
            
            # Drunk (From Person or Accident? Person is more granular, but Accident has DRUNK_DR column often)
            # Using DRUNK_DR from Accident for simplicity as it sums active drunk drivers
            acc_df['Drunk_Drivers'] = acc_df['DRUNK_DR'].fillna(0).astype(int)
            acc_df['Is_Alcohol'] = (acc_df['Drunk_Drivers'] > 0).astype(int)

            # Speeding (From Vehicle) -> Merge required if not in accident
            # Simplified: Use Accident aggregates
            aggs = {
                'ST_CASE': 'count',
                'FATALS': 'sum',
                'Is_Adverse_Weather': 'sum',
                'Is_Dark': 'sum',
                'Is_Alcohol': 'sum'
            }
            
            county_stats = acc_df.groupby('FIPS').agg(aggs).reset_index()
            county_stats.rename(columns={
                'ST_CASE': 'Total_Accidents',
                'FATALS': 'Total_Fatalities',
                'Is_Adverse_Weather': 'Weather_Accidents',
                'Is_Dark': 'Dark_Accidents',
                'Is_Alcohol': 'Alcohol_Accidents'
            }, inplace=True)
            
            # 3. Merge
            merged = pd.merge(edu_pivot, county_stats, on='FIPS', how='left')
            
            # Fill NaNs with 0 for accident stats (counties with no accidents)
            cols_to_fill = ['Total_Accidents', 'Total_Fatalities', 'Weather_Accidents', 'Dark_Accidents', 'Alcohol_Accidents']
            merged[cols_to_fill] = merged[cols_to_fill].fillna(0)
            
            merged['Year'] = year
            all_data.append(merged)
            print("Done.")
            
        except Exception as e:
            print(f"Error processing {year}: {e}")
            
    master_df = pd.concat(all_data, ignore_index=True)
    
    # --- GLOBAL CALCULATIONS ---
    # Fatality Rate per 100k
    master_df['Fatality_Rate'] = (master_df['Total_Fatalities'] / master_df['Population']) * 100000
    master_df['Accident_Rate'] = (master_df['Total_Accidents'] / master_df['Population']) * 100000
    
    # Ratios
    master_df['Pct_Alcohol_Accidents'] = (master_df['Alcohol_Accidents'] / master_df['Total_Accidents']) * 100
    master_df['Pct_Weather_Accidents'] = (master_df['Weather_Accidents'] / master_df['Total_Accidents']) * 100
    master_df['Pct_Dark_Accidents'] = (master_df['Dark_Accidents'] / master_df['Total_Accidents']) * 100
    
    # Rural/Urban Classification based on Density (approx) or Population
    # Simple Bucket: <50k Rural, >50k Urban
    master_df['Urbanicity'] = master_df['Population'].apply(lambda x: 'Rural' if x < 50000 else 'Urban') # Simple threshold
    
    return master_df

# --- EDA PLOTTING FUNCTIONS ---

def plot_correlation_heatmap(df):
    plt.figure(figsize=(10, 8))
    cols = ['Pct_Less_HS', 'Fatality_Rate', 'Accident_Rate', 'Pct_Alcohol_Accidents', 'Pct_Dark_Accidents', 'Population']
    corr = df[cols].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Correlation Matrix of Key Variables')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, '01_correlation_heatmap.png'))
    plt.close()

def plot_education_vs_fatality(df):
    plt.figure(figsize=(10, 6))
    # Sample to avoid overcrowding
    sample = df.sample(n=min(5000, len(df)), random_state=42)
    sns.scatterplot(data=sample, x='Pct_Less_HS', y='Fatality_Rate', hue='Urbanicity', alpha=0.5)
    sns.regplot(data=sample, x='Pct_Less_HS', y='Fatality_Rate', scatter=False, color='red', label='Trend')
    plt.title('Education Level vs. Fatality Rate (Per 100k)')
    plt.xlabel('% Less Than High School (Lower Education)')
    plt.ylabel('Fatalities per 100k')
    plt.ylim(0, 100) # Cap for visuals
    plt.legend()
    plt.savefig(os.path.join(OUTPUT_DIR, '02_edu_vs_fatality.png'))
    plt.close()

def plot_temporal_trends(df):
    yearly = df.groupby('Year')[['Total_Fatalities', 'Total_Accidents']].sum().reset_index()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    color = 'tab:red'
    ax1.set_xlabel('Year')
    ax1.set_ylabel('Total Fatalities', color=color)
    ax1.plot(yearly['Year'], yearly['Total_Fatalities'], color=color, marker='o', linewidth=2, label='Fatalities')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(False)
    
    ax2 = ax1.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Total Accidents', color=color)  
    ax2.plot(yearly['Year'], yearly['Total_Accidents'], color=color, marker='s', linestyle='--', linewidth=2, label='Accidents')
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.grid(False)
    
    plt.title('Total Traffic Accidents and Fatalities (2010-2023)')
    plt.savefig(os.path.join(OUTPUT_DIR, '03_temporal_trends.png'))
    plt.close()

def plot_risk_factors_by_group(df):
    # Alcohol
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Edu_Quantile', y='Pct_Alcohol_Accidents', hue='Urbanicity')
    plt.title('Alcohol-Involved Accidents by Education Level')
    plt.ylabel('% Accidents Involving Alcohol')
    plt.savefig(os.path.join(OUTPUT_DIR, '04_alcohol_by_edu.png'))
    plt.close()
    
    # Dark
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='Edu_Quantile', y='Pct_Dark_Accidents', hue='Urbanicity')
    plt.title('Nighttime/Unlit Accidents by Education Level')
    plt.ylabel('% Accidents in Dark')
    plt.savefig(os.path.join(OUTPUT_DIR, '05_dark_by_edu.png'))
    plt.close()

def plot_state_choropleth(df):
    # Simplified state comparison bar chart instead of map if geojson not avail
    # Group by State FIPS first 2 digits
    df['State_FIPS'] = df['FIPS'].str[:2]
    state_avg = df.groupby('State_FIPS')['Fatality_Rate'].mean().sort_values(ascending=False).head(10).reset_index()
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=state_avg, x='State_FIPS', y='Fatality_Rate', palette='magma')
    plt.title('Top 10 States by Average County Fatality Rate')
    plt.xlabel('State FIPS')
    plt.savefig(os.path.join(OUTPUT_DIR, '06_top_states_risk.png'))
    plt.close()

# --- EXDA PLOTTING FUNCTIONS ---

def perform_pca_and_plot(df):
    # PCA on Risk Factors
    features = ['Fatality_Rate', 'Pct_Alcohol_Accidents', 'Pct_Dark_Accidents', 'Pct_Weather_Accidents', 'Pct_Less_HS']
    # Aggregating by County (mean over years) for stable profile
    df_county = df.groupby('FIPS')[features].mean().dropna()
    
    x = StandardScaler().fit_transform(df_county)
    pca = PCA(n_components=2)
    components = pca.fit_transform(x)
    
    pca_df = pd.DataFrame(data=components, columns=['PC1', 'PC2'])
    pca_df['Pct_Less_HS'] = df_county['Pct_Less_HS'].values
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(pca_df['PC1'], pca_df['PC2'], c=pca_df['Pct_Less_HS'], cmap='viridis', alpha=0.6)
    plt.colorbar(scatter, label='% Less Than HS')
    plt.title('PCA: County Risk Profiles')
    plt.xlabel('Principal Component 1 (General Risk)')
    plt.ylabel('Principal Component 2 (Environmental Factors)')
    plt.savefig(os.path.join(OUTPUT_DIR, 'exda_01_pca.png'))
    plt.close()
    
    # Loadings
    print("\nPCA Loadings:")
    print(pd.DataFrame(pca.components_, columns=features, index=['PC1', 'PC2']))

def perform_clustering_and_plot(df):
    features = ['Fatality_Rate', 'Pct_Alcohol_Accidents', 'Pct_Less_HS']
    df_clean = df.groupby('FIPS')[features].mean().dropna()
    
    X = StandardScaler().fit_transform(df_clean)
    
    kmeans = KMeans(n_clusters=3, random_state=42)
    df_clean['Cluster'] = kmeans.fit_predict(X)
    
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df_clean, x='Pct_Less_HS', y='Fatality_Rate', hue='Cluster', palette='deep')
    plt.title('K-Means Clustering of Safety Archetypes')
    plt.savefig(os.path.join(OUTPUT_DIR, 'exda_02_clusters.png'))
    plt.close()

def main():
    print("Starting Analysis Report Generation...")
    
    # 1. Load Data
    df = load_and_process_data()
    print(f"Data Loaded: {len(df)} rows.")
    
    if len(df) == 0:
        print("CRITICAL: No data loaded. Check paths.")
        return

    # 2. EDA
    print("Generating EDA Graphs...")
    plot_correlation_heatmap(df)
    plot_education_vs_fatality(df)
    plot_temporal_trends(df)
    plot_risk_factors_by_group(df)
    plot_state_choropleth(df)
    
    # Distribution of Fatality Rates
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Fatality_Rate'], bins=50, kde=True, color='purple')
    plt.title('Distribution of Fatality Rates across Counties')
    plt.xlim(0, 100)
    plt.savefig(os.path.join(OUTPUT_DIR, '07_dist_fatality.png'))
    plt.close()
    
    # Scatter: Alcohol vs Fatality
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Pct_Alcohol_Accidents', y='Fatality_Rate', alpha=0.3)
    plt.title('Alcohol Involvement vs. Fatality Rate')
    plt.savefig(os.path.join(OUTPUT_DIR, '08_alcohol_scatter.png'))
    plt.close()
    
    # Boxplot: Year vs Fatality Rate
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='Year', y='Fatality_Rate')
    plt.ylim(0, 100)
    plt.title('Yearly Distribution of Fatality Rates')
    plt.savefig(os.path.join(OUTPUT_DIR, '09_yearly_boxplot.png'))
    plt.close()

    # --- ADDITIONAL PLOTS ---
    # 10. Accident Rate Dist
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Accident_Rate'], bins=50, kde=True, color='green')
    plt.title('Distribution of Accident Rates (Per 100k)')
    plt.xlim(0, 5000)
    plt.savefig(os.path.join(OUTPUT_DIR, '10_dist_accident_rate.png'))
    plt.close()

    # 11. Alcohol Rate Dist
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Pct_Alcohol_Accidents'], bins=50, kde=True, color='red')
    plt.title('Distribution of Alcohol-Involved Accident %')
    plt.savefig(os.path.join(OUTPUT_DIR, '11_dist_alcohol_rate.png'))
    plt.close()

    # 12. Weather vs Fatality
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Pct_Weather_Accidents', y='Fatality_Rate', alpha=0.3)
    plt.title('Adverse Weather % vs. Fatality Rate')
    plt.savefig(os.path.join(OUTPUT_DIR, '12_scatter_weather_fatality.png'))
    plt.close()

    # 13. Education vs Alcohol
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='Pct_Less_HS', y='Pct_Alcohol_Accidents', hue='Urbanicity', alpha=0.3)
    plt.title('% Less HS vs. % Alcohol Accidents')
    plt.savefig(os.path.join(OUTPUT_DIR, '13_scatter_edu_alcohol.png'))
    plt.close()

    # 14. Year vs Alcohol Bar
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Year', y='Pct_Alcohol_Accidents', palette='Reds')
    plt.title('Average Alcohol-Involved Accident % by Year')
    plt.savefig(os.path.join(OUTPUT_DIR, '14_bar_year_alcohol.png'))
    plt.close()

    # 15. Year vs Weather Bar
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='Year', y='Pct_Weather_Accidents', palette='Blues')
    plt.title('Average Adverse Weather Accident % by Year')
    plt.savefig(os.path.join(OUTPUT_DIR, '15_bar_year_weather.png'))
    plt.close()

    # 16. Urbanicity vs Fatality Box
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Urbanicity', y='Fatality_Rate', palette='Set2')
    plt.ylim(0, 150)
    plt.title('Fatality Rate by Urbanicity')
    plt.savefig(os.path.join(OUTPUT_DIR, '16_box_urbanicity_fatality.png'))
    plt.close()

    # 17. Urbanicity vs Alcohol Box
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='Urbanicity', y='Pct_Alcohol_Accidents', palette='Set2')
    plt.title('Alcohol Involvement % by Urbanicity')
    plt.savefig(os.path.join(OUTPUT_DIR, '17_box_urbanicity_alcohol.png'))
    plt.close()
    
    # 3. ExDA
    print("Generating ExDA Graphs...")
    perform_pca_and_plot(df)
    perform_clustering_and_plot(df)
    
    # Save processed data for report reference
    df.to_csv(os.path.join(BASE_DIR, "processed_analysis_data.csv"), index=False)
    print("Analysis Complete. Images saved to output/.")

if __name__ == "__main__":
    main()
