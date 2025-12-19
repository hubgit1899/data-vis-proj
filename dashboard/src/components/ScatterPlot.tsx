import { useEffect, useState } from 'react';
import Plot from 'react-plotly.js';
import type { CountyData } from '../types';
import { COLORS } from '../types';

export default function ScatterPlot() {
  const [data, setData] = useState<CountyData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/data/county_scatter.json')
      .then(res => res.json())
      .then((json: CountyData[]) => {
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to load scatter data:', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-lg text-gray-600">Loading scatter plot data...</div>
      </div>
    );
  }

  // Filter out invalid data points and separate Rural/Urban
  const validData = data.filter(d => 
    d.Pct_Less_HS != null && !isNaN(d.Pct_Less_HS) &&
    d.Fatality_Rate != null && !isNaN(d.Fatality_Rate) &&
    d.Fatality_Rate < 150 && d.Fatality_Rate > 0
  );
  
  console.log('Total data points:', data.length);
  console.log('Valid data points:', validData.length);
  
  const ruralData = validData.filter(d => d.Urbanicity === 'Rural');
  const urbanData = validData.filter(d => d.Urbanicity === 'Urban');
  
  console.log('Rural:', ruralData.length, 'Urban:', urbanData.length);

  // Create hover text
  const createHoverText = (d: CountyData) => 
    `<b>County:</b> ${d.FIPS_STR}<br>` +
    `<b>State:</b> ${d.State_Abbrev}<br>` +
    `<b>% Without HS:</b> ${d.Pct_Less_HS.toFixed(1)}%<br>` +
    `<b>Fatality Rate:</b> ${d.Fatality_Rate.toFixed(1)} per 100k<br>` +
    `<b>Population:</b> ${d.Population >= 1e6 ? (d.Population/1e6).toFixed(1) + 'M' : (d.Population/1e3).toFixed(0) + 'k'}<br>` +
    `<b>Urbanicity:</b> ${d.Urbanicity}`;

  return (
    <div className="w-full h-full p-4">
      <Plot
        data={[
          {
            x: ruralData.map(d => d.Pct_Less_HS),
            y: ruralData.map(d => d.Fatality_Rate),
            mode: 'markers',
            type: 'scatter',
            name: 'Rural',
            marker: {
              color: COLORS.danger,
              opacity: 0.6,
              size: 10
            },
            text: ruralData.map(createHoverText),
            hoverinfo: 'text',
            hoverlabel: {
              bgcolor: 'white',
              font: { size: 12 }
            }
          },
          {
            x: urbanData.map(d => d.Pct_Less_HS),
            y: urbanData.map(d => d.Fatality_Rate),
            mode: 'markers',
            type: 'scatter',
            name: 'Urban',
            marker: {
              color: COLORS.safety,
              opacity: 0.6,
              size: 10
            },
            text: urbanData.map(createHoverText),
            hoverinfo: 'text',
            hoverlabel: {
              bgcolor: 'white',
              font: { size: 12 }
            }
          }
        ]}
        layout={{
          title: {
            text: 'Education vs Fatality Rate by County (2010-2023 Average)',
            font: { size: 18, color: COLORS.primary }
          },
          xaxis: {
            title: { text: '% Without High School Diploma' },
            gridcolor: COLORS.grid,
            range: [0, 50]
          },
          yaxis: {
            title: { text: 'Fatalities per 100k Population' },
            gridcolor: COLORS.grid,
            range: [0, 150]
          },
          legend: {
            x: 0.02,
            y: 0.98,
            bgcolor: 'rgba(255,255,255,0.8)'
          },
          hovermode: 'closest',
          paper_bgcolor: 'white',
          plot_bgcolor: 'white',
          margin: { l: 60, r: 30, t: 60, b: 60 }
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          modeBarButtonsToRemove: ['lasso2d', 'select2d']
        }}
        style={{ width: '100%', height: '100%' }}
      />
    </div>
  );
}
