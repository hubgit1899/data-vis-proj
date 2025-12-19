# Traffic Safety & Education Analysis

A comprehensive data visualization project analyzing the relationship between educational attainment and traffic fatality rates across US counties from 2010-2023.

## 📊 Project Overview

This project investigates a critical question: **Does education level correlate with traffic safety?**

Using data from the **FARS (Fatality Analysis Reporting System)** and **US Census education data**, we analyze over 35,000 county-year observations to reveal patterns in traffic fatalities, alcohol involvement, and other risk factors.

### Key Findings

- Counties with **lower high school graduation rates** have significantly higher traffic fatality rates
- **Rural areas** show 2-3x higher fatality rates compared to urban areas
- **Alcohol involvement** is strongly correlated with education levels
- The education-safety gap has remained consistent over 14 years

---

## 🗂️ Project Structure

```
data-vis-proj/
├── analysis-code/           # Python analysis scripts
│   └── analysis_report_v2.py
├── dashboard/               # React interactive dashboard
│   ├── src/
│   ├── public/data/
│   └── package.json
├── datasets/                # Raw data files (not tracked in git)
├── output/                  # Generated visualizations (not tracked in git)
├── reports/                 # Written reports
├── requirements.txt         # Python dependencies
├── setup.sh                 # macOS/Linux setup script
├── setup.bat                # Windows setup script
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for analysis)
- **Node.js 18+** (for dashboard)
- Internet connection (for GeoJSON data)

### Option 1: Run Analysis Only

Generate static visualizations (PNG files):

#### macOS/Linux
```bash
# Run setup script
bash setup.sh

# Activate virtual environment
source venv/bin/activate

# Run analysis
python analysis-code/analysis_report_v2.py
```

#### Windows
```cmd
# Run setup script (double-click or run in Command Prompt)
setup.bat

# Activate virtual environment
venv\Scripts\activate.bat

# Run analysis
python analysis-code\analysis_report_v2.py
```

### Option 2: Run Interactive Dashboard

Launch a web-based interactive visualization:

```bash
# Navigate to dashboard folder
cd dashboard

# Install dependencies
npm install

# Prepare data (requires Python venv active)
source ../venv/bin/activate  # macOS/Linux
# or: ..\venv\Scripts\activate.bat  # Windows
python prepare_data.py

# Start development server
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## 📈 Analysis Outputs

The analysis script generates **20+ visualizations** in the `output/` folder:

### Infographic
| File | Description |
|------|-------------|
| `INFOGRAPHIC_Composite.png` | Professional poster comparing high vs low education counties |

### Exploratory Data Analysis (EDA)
| File | Description |
|------|-------------|
| `EDA_01_Trend_Fatality.png` | Fatality rate trend over time (2010-2023) |
| `EDA_02_Dual_Totals.png` | Accidents vs fatalities dual-axis chart |
| `EDA_03_Dist_Fatality.png` | Distribution of county fatality rates |
| `EDA_04_Box_Urbanicity.png` | Rural vs urban safety gap boxplot |
| `EDA_05_Bar_Edu.png` | Fatality rate by education quartile |
| `EDA_06_Scatter_Corr.png` | Education vs fatality correlation scatter |
| `EDA_07_Line_Alcohol.png` | Alcohol incident trends by education |
| `EDA_08_Bar_Dark.png` | Nighttime accidents by education |
| `EDA_09_Hex_Density.png` | Risk density hexbin plot |
| `EDA_10_Corr_Heatmap.png` | Correlation matrix of all variables |
| `EDA_11_Scatter_Alcohol.png` | Alcohol % vs fatality rate |
| `EDA_12_Bar_States.png` | Top 10 highest-risk states |
| `EDA_13_Scatter_Weather.png` | Weather impact analysis |
| `EDA_14_Scatter_Pop.png` | Population vs fatality rate |
| `EDA_15_KDE_Alcohol.png` | Alcohol involvement distribution |

### Maps
| File | Description |
|------|-------------|
| `MAP_Fatality_Rate.png` | US choropleth - fatality rates by state |
| `MAP_Education.png` | US choropleth - education levels by state |
| `MAP_Population.png` | US choropleth - population by state |

### Exploratory Analysis (ExDA)
| File | Description |
|------|-------------|
| `EXDA_01_Feature_Imp.png` | Random Forest feature importance |
| `EXDA_02_Cluster_Heatmap.png` | K-Means cluster profiles |

---

## 🖥️ Interactive Dashboard

The React dashboard provides **two interactive views**:

### 1. Scatter Plot Tab
- Interactive scatter plot of **Education vs Fatality Rate**
- Each point represents a county (averaged over 14 years)
- **Click legend** to filter Rural/Urban
- **Hover** to see county details (FIPS, state, population, etc.)

### 2. Interactive Maps Tab
- US choropleth map with three metrics:
  - Fatality Rate (per 100k population)
  - % Without High School Diploma
  - Population
- **Click any state** to drill down to county-level view
- **Switch metrics** while maintaining zoom level
- **Reset button** to return to state view

---

## 📁 Data Sources

### FARS (Fatality Analysis Reporting System)
- **Source**: NHTSA (National Highway Traffic Safety Administration)
- **Years**: 2010-2023
- **Contains**: Fatal accident records including alcohol involvement, weather conditions, lighting conditions

### US Census Education Data
- **Source**: US Census Bureau
- **Years**: 2010-2023
- **Contains**: County-level educational attainment statistics

### Required Data Structure
Place data files in the `datasets/` folder:
```
datasets/
├── Education2010.csv
├── Education2011.csv
├── ...
├── Education2023.csv
├── FARS2010National/
│   └── ACCIDENT.CSV
├── FARS2011National/
│   └── ACCIDENT.CSV
├── ...
└── FARS2023National/
    └── ACCIDENT.CSV
```

---

## 🎨 Design System

The project uses a **colorblind-safe** color palette:

| Color | Hex | Usage |
|-------|-----|-------|
| Danger (Orange-Red) | `#D55E00` | High risk, low education |
| Safety (Teal-Green) | `#009E73` | Low risk, high education |
| Education (Sky Blue) | `#56B4E9` | Education-related data |
| Accent (Yellow) | `#F0E442` | Highlights |
| Primary (Dark Grey) | `#333333` | Text, neutral |

---

## 🛠️ Technologies Used

### Analysis
- **Python 3.8+**
- pandas, numpy - Data processing
- matplotlib, seaborn - Visualization
- geopandas - Geographic data
- scikit-learn - Machine learning (clustering, feature importance)

### Dashboard
- **React 18** with TypeScript
- **Vite** - Build tool
- **TailwindCSS** - Styling
- **Plotly.js** - Interactive scatter plot
- **Leaflet** - Interactive maps

---

## 📝 License

This project was created for educational purposes as part of a Data Visualization course.

---

## 👥 Authors

Data Visualization Project - Fall 2025
