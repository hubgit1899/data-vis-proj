import { useState } from 'react';
import ScatterPlot from './components/ScatterPlot';
import InteractiveMap from './components/InteractiveMap';
import type { MetricType } from './types';
import { COLORS } from './types';

type TabType = 'scatter' | 'maps';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>('scatter');
  const [metric, setMetric] = useState<MetricType>('Fatality_Rate');

  return (
    <div className="h-screen flex flex-col bg-gray-100">
      {/* Header */}
      <header 
        className="px-6 py-4 shadow-md"
        style={{ backgroundColor: COLORS.primary }}
      >
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">
            Traffic Safety Dashboard
          </h1>
          <p className="text-gray-300 text-sm">
            Education & Fatality Analysis (2010-2023)
          </p>
        </div>
        
        {/* Tabs */}
        <nav className="mt-4 flex gap-2">
          <button
            onClick={() => setActiveTab('scatter')}
            className={`px-5 py-2 rounded-t-lg font-medium transition-colors ${
              activeTab === 'scatter'
                ? 'bg-white text-gray-800'
                : 'bg-gray-600 text-gray-200 hover:bg-gray-500'
            }`}
          >
            📊 Scatter Plot
          </button>
          <button
            onClick={() => setActiveTab('maps')}
            className={`px-5 py-2 rounded-t-lg font-medium transition-colors ${
              activeTab === 'maps'
                ? 'bg-white text-gray-800'
                : 'bg-gray-600 text-gray-200 hover:bg-gray-500'
            }`}
          >
            🗺️ Interactive Maps
          </button>
        </nav>
      </header>

      {/* Content */}
      <main className="flex-1 bg-white overflow-hidden">
        {activeTab === 'scatter' && <ScatterPlot />}
        {activeTab === 'maps' && (
          <InteractiveMap 
            metric={metric} 
            onMetricChange={setMetric} 
          />
        )}
      </main>

      {/* Footer */}
      <footer className="px-6 py-3 bg-gray-200 text-center text-sm text-gray-600">
        Data: FARS & US Census (2010-2023) | Built with React, Plotly & Leaflet
      </footer>
    </div>
  );
}

export default App;
