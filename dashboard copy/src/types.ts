// Type definitions for the dashboard

export interface CountyData {
  FIPS_STR: string;
  county_id: string;
  Pct_Less_HS: number;
  Fatality_Rate: number;
  Urbanicity: 'Rural' | 'Urban';
  Population: number;
  State_Abbrev: string;
  Drunk_Rate_Per_100k: number;
  Dark_Pct: number;
  Weather_Pct: number;
}

export interface StateData {
  State_Abbrev: string;
  Fatality_Rate: number;
  Pct_Less_HS: number;
  Population: number;
}

export type MetricType = 'Fatality_Rate' | 'Pct_Less_HS' | 'Population';

export const METRIC_LABELS: Record<MetricType, string> = {
  Fatality_Rate: 'Fatalities per 100k',
  Pct_Less_HS: '% Without HS Diploma',
  Population: 'Population'
};

export const COLORS = {
  primary: '#333333',
  danger: '#D55E00',
  safety: '#009E73',
  education: '#56B4E9',
  accent: '#F0E442',
  text: '#333333',
  grid: '#DDDDDD',
  bg: '#FFFFFF'
};
