import { useEffect, useState, useCallback, useMemo } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import type { StateData, CountyData, MetricType } from '../types';
import { METRIC_LABELS, COLORS } from '../types';

// State name to abbreviation mapping
const STATE_ABBREV: Record<string, string> = {
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
  'District of Columbia': 'DC', 'Puerto Rico': 'PR'
};

// Color scales for each metric - thresholds based on actual data distribution
const getColor = (value: number, metric: MetricType): string => {
  if (value === null || value === undefined || isNaN(value)) return '#CCCCCC';
  
  // Define ranges and color scales for each metric
  // Thresholds are based on data quartiles:
  // Fatality_Rate: min 5.6, max 72.2, mean 29.8
  // Pct_Less_HS: typical range 5-30%
  // Population: varies widely
  const scales: Record<MetricType, { colors: string[], thresholds: number[] }> = {
    Fatality_Rate: {
      colors: ['#FEE5D9', '#FCAE91', '#FB6A4A', '#DE2D26', '#A50F15'],
      thresholds: [20, 28, 35, 45]  // Adjusted for data range 5.6-72.2
    },
    Pct_Less_HS: {
      colors: ['#EFF3FF', '#BDD7E7', '#6BAED6', '#3182BD', '#08519C'],
      thresholds: [12, 16, 20, 25]  // Adjusted for typical education data
    },
    Population: {
      colors: ['#EDF8E9', '#BAE4B3', '#74C476', '#31A354', '#006D2C'],
      thresholds: [1e6, 3e6, 6e6, 15e6]
    }
  };
  
  const scale = scales[metric];
  for (let i = 0; i < scale.thresholds.length; i++) {
    if (value < scale.thresholds[i]) return scale.colors[i];
  }
  return scale.colors[scale.colors.length - 1];
};

// Format value for display
const formatValue = (value: number, metric: MetricType): string => {
  if (value === null || value === undefined || isNaN(value)) return 'N/A';
  if (metric === 'Population') {
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
    return `${(value / 1e3).toFixed(0)}k`;
  }
  return value.toFixed(1);
};

// Map controller component for programmatic view changes
function MapController({ center, zoom }: { center: [number, number], zoom: number }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, zoom, { duration: 0.8 });
  }, [center, zoom, map]);
  return null;
}

interface InteractiveMapProps {
  metric: MetricType;
  onMetricChange: (metric: MetricType) => void;
}

export default function InteractiveMap({ metric, onMetricChange }: InteractiveMapProps) {
  const [stateData, setStateData] = useState<StateData[]>([]);
  const [countyByState, setCountyByState] = useState<Record<string, CountyData[]>>({});
  const [stateGeoJSON, setStateGeoJSON] = useState<GeoJSON.FeatureCollection | null>(null);
  const [countyGeoJSON, setCountyGeoJSON] = useState<GeoJSON.FeatureCollection | null>(null);
  const [selectedState, setSelectedState] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [mapCenter, setMapCenter] = useState<[number, number]>([39.8, -98.5]);
  const [mapZoom, setMapZoom] = useState(4);

  // Load data on mount
  useEffect(() => {
    Promise.all([
      fetch('/data/state_data.json').then(r => r.json()),
      fetch('/data/county_by_state.json').then(r => r.json()),
      fetch('/data/us-states.json').then(r => r.json())  // Local file
    ]).then(([states, counties, geoJson]) => {
      console.log('Loaded state data:', states.length, 'states');
      console.log('Loaded county data for', Object.keys(counties).length, 'states');
      console.log('GeoJSON features:', geoJson.features.length);
      
      setStateData(states);
      setCountyByState(counties);
      // Filter out Alaska, Hawaii, Puerto Rico for continental view
      const filteredGeo = {
        ...geoJson,
        features: geoJson.features.filter((f: GeoJSON.Feature) => {
          const name = f.properties?.name;
          return name && !['Alaska', 'Hawaii', 'Puerto Rico'].includes(name);
        })
      };
      console.log('Filtered GeoJSON features:', filteredGeo.features.length);
      setStateGeoJSON(filteredGeo);
      setLoading(false);
    }).catch(err => {
      console.error('Failed to load map data:', err);
      setLoading(false);
    });
  }, []);

  // Get value for a state
  const getStateValue = useCallback((stateAbbrev: string): number => {
    const state = stateData.find(s => s.State_Abbrev === stateAbbrev);
    return state ? state[metric] : NaN;
  }, [stateData, metric]);

  // Create state data lookup
  const stateDataLookup = useMemo(() => {
    const lookup: Record<string, StateData> = {};
    stateData.forEach(s => { lookup[s.State_Abbrev] = s; });
    return lookup;
  }, [stateData]);

  // Style function for states
  const stateStyle = useCallback((feature: GeoJSON.Feature | undefined) => {
    if (!feature?.properties?.name) return { fillColor: '#CCCCCC', weight: 1, color: '#666', fillOpacity: 0.7 };
    const abbrev = STATE_ABBREV[feature.properties.name];
    const value = getStateValue(abbrev);
    return {
      fillColor: getColor(value, metric),
      weight: selectedState === abbrev ? 3 : 1,
      color: selectedState === abbrev ? COLORS.primary : '#666',
      fillOpacity: 0.7
    };
  }, [metric, getStateValue, selectedState]);

  // Handle state click
  const onStateClick = useCallback((e: L.LeafletMouseEvent, feature: GeoJSON.Feature) => {
    const stateName = feature.properties?.name;
    const abbrev = STATE_ABBREV[stateName];
    if (!abbrev) return;
    
    setSelectedState(abbrev);
    
    // Zoom to state bounds
    const bounds = e.target.getBounds();
    const center = bounds.getCenter();
    setMapCenter([center.lat, center.lng]);
    setMapZoom(6);
    
    // Load county GeoJSON for this state (from local file)
    fetch('/data/counties-fips.json')  // Local file
      .then(r => r.json())
      .then((allCounties: GeoJSON.FeatureCollection) => {
        // Filter to just this state's counties (FIPS starts with state code)
        // Get state FIPS prefix
        const stateFips: Record<string, string> = {
          'AL': '01', 'AK': '02', 'AZ': '04', 'AR': '05', 'CA': '06', 'CO': '08', 'CT': '09',
          'DE': '10', 'DC': '11', 'FL': '12', 'GA': '13', 'HI': '15', 'ID': '16', 'IL': '17',
          'IN': '18', 'IA': '19', 'KS': '20', 'KY': '21', 'LA': '22', 'ME': '23', 'MD': '24',
          'MA': '25', 'MI': '26', 'MN': '27', 'MS': '28', 'MO': '29', 'MT': '30', 'NE': '31',
          'NV': '32', 'NH': '33', 'NJ': '34', 'NM': '35', 'NY': '36', 'NC': '37', 'ND': '38',
          'OH': '39', 'OK': '40', 'OR': '41', 'PA': '42', 'RI': '44', 'SC': '45', 'SD': '46',
          'TN': '47', 'TX': '48', 'UT': '49', 'VT': '50', 'VA': '51', 'WA': '53', 'WV': '54',
          'WI': '55', 'WY': '56'
        };
        const fipsPrefix = stateFips[abbrev];
        if (fipsPrefix) {
          const stateCounties = {
            ...allCounties,
            features: allCounties.features.filter((f: GeoJSON.Feature) => 
              f.id?.toString().startsWith(fipsPrefix)
            )
          };
          setCountyGeoJSON(stateCounties);
        }
      });
  }, []);

  // Reset map
  const resetMap = useCallback(() => {
    setSelectedState(null);
    setCountyGeoJSON(null);
    setMapCenter([39.8, -98.5]);
    setMapZoom(4);
  }, []);

  // County style
  const countyStyle = useCallback((feature: GeoJSON.Feature | undefined) => {
    if (!feature?.id || !selectedState) return { fillColor: '#CCCCCC', weight: 0.5, color: '#999', fillOpacity: 0.7 };
    const fips = feature.id.toString().padStart(5, '0');
    const countyData = countyByState[selectedState]?.find(c => c.FIPS_STR === fips);
    const value = countyData ? countyData[metric as keyof CountyData] as number : NaN;
    return {
      fillColor: getColor(value, metric),
      weight: 0.5,
      color: '#666',
      fillOpacity: 0.7
    };
  }, [metric, selectedState, countyByState]);

  // Tooltip for counties
  const onEachCounty = useCallback((feature: GeoJSON.Feature, layer: L.Layer) => {
    if (!selectedState) return;
    const fips = feature.id?.toString().padStart(5, '0');
    const countyData = countyByState[selectedState]?.find(c => c.FIPS_STR === fips);
    if (countyData) {
      const value = countyData[metric as keyof CountyData] as number;
      layer.bindTooltip(
        `<b>County: ${fips}</b><br>` +
        `${METRIC_LABELS[metric]}: ${formatValue(value, metric)}<br>` +
        `Population: ${formatValue(countyData.Population, 'Population')}`
      );
    }
  }, [metric, selectedState, countyByState]);

  // Tooltip for states
  const onEachState = useCallback((feature: GeoJSON.Feature, layer: L.Layer) => {
    const stateName = feature.properties?.name;
    const abbrev = STATE_ABBREV[stateName];
    const data = stateDataLookup[abbrev];
    if (data) {
      const value = data[metric];
      layer.bindTooltip(
        `<b>${stateName} (${abbrev})</b><br>` +
        `${METRIC_LABELS[metric]}: ${formatValue(value, metric)}`
      );
    }
    layer.on('click', (e) => onStateClick(e, feature));
  }, [metric, stateDataLookup, onStateClick]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-lg text-gray-600">Loading map data...</div>
      </div>
    );
  }

  return (
    <div className="w-full h-full flex flex-col">
      {/* Controls */}
      <div className="flex items-center gap-4 p-4 bg-gray-50 border-b">
        <label className="font-medium text-gray-700">Metric:</label>
        <select
          value={metric}
          onChange={(e) => onMetricChange(e.target.value as MetricType)}
          className="px-3 py-2 border rounded-md bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="Fatality_Rate">Fatality Rate (per 100k)</option>
          <option value="Pct_Less_HS">% Without HS Diploma</option>
          <option value="Population">Population</option>
        </select>
        
        {selectedState && (
          <button
            onClick={resetMap}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
          >
            ← Reset Map
          </button>
        )}
        
        {selectedState && (
          <span className="ml-auto text-gray-600">
            Viewing: <strong>{selectedState}</strong> counties
          </span>
        )}
      </div>

      {/* Map */}
      <div className="flex-1">
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          style={{ width: '100%', height: '100%' }}
          scrollWheelZoom={true}
        >
          {/* Base map tiles - using OpenStreetMap which works without VPN */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <MapController center={mapCenter} zoom={mapZoom} />
          
          {/* State layer (always shown) */}
          {stateGeoJSON && !selectedState && (
            <GeoJSON
              key={`states-${metric}`}
              data={stateGeoJSON}
              style={stateStyle}
              onEachFeature={onEachState}
            />
          )}
          
          {/* County layer (shown when state is selected) */}
          {countyGeoJSON && selectedState && (
            <GeoJSON
              key={`counties-${selectedState}-${metric}`}
              data={countyGeoJSON}
              style={countyStyle}
              onEachFeature={onEachCounty}
            />
          )}
        </MapContainer>
      </div>
    </div>
  );
}
