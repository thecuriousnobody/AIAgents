import React, { useState, useEffect } from 'react';
import './App.css';

// Import Lucide React icons
import { 
  Activity, 
  TrendingUp, 
  Users, 
  DollarSign, 
  Code, 
  Building2,
  Calendar,
  Zap,
  AlertCircle,
  CheckCircle,
  Clock,
  RefreshCw
} from 'lucide-react';

// Import Recharts for data visualization
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

function App() {
  // State management
  const [intelligenceData, setIntelligenceData] = useState({});
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [agentStatuses, setAgentStatuses] = useState([]);
  const [websocket, setWebsocket] = useState(null);

  // Initialize WebSocket connection and fetch initial data
  useEffect(() => {
    initializeConnection();
    fetchInitialData();
    
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, []);

  const initializeConnection = () => {
    const ws = new WebSocket('ws://localhost:8000/ws/intelligence');
    
    ws.onopen = () => {
      console.log('🔌 Connected to Chennai Tech Intelligence Hub');
      setIsConnected(true);
    };
    
    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      
      if (message.type === 'intelligence_update') {
        setIntelligenceData(message.data);
        setLastUpdate(new Date());
      }
    };
    
    ws.onclose = () => {
      console.log('🔌 Disconnected from intelligence hub');
      setIsConnected(false);
      
      // Attempt to reconnect after 5 seconds
      setTimeout(initializeConnection, 5000);
    };
    
    ws.onerror = (error) => {
      console.error('❌ WebSocket error:', error);
    };
    
    setWebsocket(ws);
  };

  const fetchInitialData = async () => {
    try {
      // Fetch intelligence data
      const intelligenceResponse = await fetch('/api/intelligence');
      if (intelligenceResponse.ok) {
        const data = await intelligenceResponse.json();
        setIntelligenceData(data);
      }
      
      // Fetch agent statuses
      const agentsResponse = await fetch('/api/agents');
      if (agentsResponse.ok) {
        const agents = await agentsResponse.json();
        setAgentStatuses(agents);
      }
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('❌ Failed to fetch initial data:', error);
    }
  };

  const triggerManualUpdate = async () => {
    try {
      await fetch('/api/agents/job_market_scout/trigger', { method: 'POST' });
      console.log('🔄 Manual update triggered');
    } catch (error) {
      console.error('❌ Failed to trigger update:', error);
    }
  };

  // Sample data for charts (would be replaced by real data)
  const jobTrendData = [
    { month: 'Aug', jobs: 450 },
    { month: 'Sep', jobs: 520 },
    { month: 'Oct', jobs: 680 },
    { month: 'Nov', jobs: 750 },
    { month: 'Dec', jobs: 890 }
  ];

  const skillDemandData = [
    { skill: 'Python', demand: 85 },
    { skill: 'React', demand: 78 },
    { skill: 'AWS', demand: 72 },
    { skill: 'Docker', demand: 65 },
    { skill: 'ML/AI', demand: 58 }
  ];

  const salaryDistribution = [
    { range: '5-10 LPA', count: 25, fill: '#8884d8' },
    { range: '10-15 LPA', count: 35, fill: '#82ca9d' },
    { range: '15-25 LPA', count: 28, fill: '#ffc658' },
    { range: '25+ LPA', count: 12, fill: '#ff7c7c' }
  ];

  return (
    <div className=\"min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900\">
      {/* Header */}
      <div className=\"bg-white/10 backdrop-blur-md border-b border-white/20\">
        <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8\">
          <div className=\"flex items-center justify-between h-16\">
            <div className=\"flex items-center space-x-4\">
              <Activity className=\"h-8 w-8 text-blue-400\" />
              <div>
                <h1 className=\"text-xl font-bold text-white\">
                  Chennai Tech Intelligence Hub
                </h1>
                <p className=\"text-sm text-blue-200\">
                  Real-time IT Ecosystem Monitoring
                </p>
              </div>
            </div>
            
            <div className=\"flex items-center space-x-4\">
              {/* Connection Status */}
              <div className=\"flex items-center space-x-2\">
                {isConnected ? (
                  <CheckCircle className=\"h-5 w-5 text-green-400\" />
                ) : (
                  <AlertCircle className=\"h-5 w-5 text-red-400\" />
                )}
                <span className=\"text-sm text-white\">
                  {isConnected ? 'Live' : 'Reconnecting...'}
                </span>
              </div>
              
              {/* Last Update */}
              {lastUpdate && (
                <div className=\"flex items-center space-x-2 text-sm text-blue-200\">
                  <Clock className=\"h-4 w-4\" />
                  <span>
                    {lastUpdate.toLocaleTimeString()}
                  </span>
                </div>
              )}
              
              {/* Manual Refresh */}
              <button
                onClick={triggerManualUpdate}
                className=\"flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 px-3 py-1 rounded-md text-white text-sm transition-colors\"
              >
                <RefreshCw className=\"h-4 w-4\" />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Dashboard */}
      <div className=\"max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8\">
        {/* Key Metrics Cards */}
        <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8\">
          {/* Total Jobs */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-blue-200 text-sm font-medium\">Active Jobs</p>
                <p className=\"text-3xl font-bold text-white\">890</p>
                <p className=\"text-green-400 text-sm flex items-center mt-1\">
                  <TrendingUp className=\"h-4 w-4 mr-1\" />
                  +15% from last month
                </p>
              </div>
              <div className=\"bg-blue-500/20 p-3 rounded-lg\">
                <Users className=\"h-8 w-8 text-blue-400\" />
              </div>
            </div>
          </div>

          {/* Average Salary */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-green-200 text-sm font-medium\">Avg Salary</p>
                <p className=\"text-3xl font-bold text-white\">18.5 LPA</p>
                <p className=\"text-green-400 text-sm flex items-center mt-1\">
                  <TrendingUp className=\"h-4 w-4 mr-1\" />
                  +8% YoY growth
                </p>
              </div>
              <div className=\"bg-green-500/20 p-3 rounded-lg\">
                <DollarSign className=\"h-8 w-8 text-green-400\" />
              </div>
            </div>
          </div>

          {/* Hot Skills */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-purple-200 text-sm font-medium\">Trending Tech</p>
                <p className=\"text-3xl font-bold text-white\">AI/ML</p>
                <p className=\"text-purple-400 text-sm flex items-center mt-1\">
                  <Zap className=\"h-4 w-4 mr-1\" />
                  45% demand increase
                </p>
              </div>
              <div className=\"bg-purple-500/20 p-3 rounded-lg\">
                <Code className=\"h-8 w-8 text-purple-400\" />
              </div>
            </div>
          </div>

          {/* Active Startups */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <div className=\"flex items-center justify-between\">
              <div>
                <p className=\"text-orange-200 text-sm font-medium\">New Startups</p>
                <p className=\"text-3xl font-bold text-white\">25</p>
                <p className=\"text-orange-400 text-sm flex items-center mt-1\">
                  <Building2 className=\"h-4 w-4 mr-1\" />
                  This month
                </p>
              </div>
              <div className=\"bg-orange-500/20 p-3 rounded-lg\">
                <Building2 className=\"h-8 w-8 text-orange-400\" />
              </div>
            </div>
          </div>
        </div>

        {/* Charts Section */}
        <div className=\"grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8\">
          {/* Job Trend Chart */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <h3 className=\"text-lg font-semibold text-white mb-4 flex items-center\">
              <TrendingUp className=\"h-5 w-5 mr-2 text-blue-400\" />
              Job Posting Trends
            </h3>
            <ResponsiveContainer width=\"100%\" height={300}>
              <LineChart data={jobTrendData}>
                <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
                <XAxis dataKey=\"month\" stroke=\"#9CA3AF\" />
                <YAxis stroke=\"#9CA3AF\" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }} 
                />
                <Line 
                  type=\"monotone\" 
                  dataKey=\"jobs\" 
                  stroke=\"#3B82F6\" 
                  strokeWidth={3}
                  dot={{ fill: '#3B82F6', strokeWidth: 2, r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Skill Demand Chart */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <h3 className=\"text-lg font-semibold text-white mb-4 flex items-center\">
              <Code className=\"h-5 w-5 mr-2 text-green-400\" />
              Top Skills in Demand
            </h3>
            <ResponsiveContainer width=\"100%\" height={300}>
              <BarChart data={skillDemandData}>
                <CartesianGrid strokeDasharray=\"3 3\" stroke=\"#374151\" />
                <XAxis dataKey=\"skill\" stroke=\"#9CA3AF\" />
                <YAxis stroke=\"#9CA3AF\" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }} 
                />
                <Bar dataKey=\"demand\" fill=\"#10B981\" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Bottom Section */}
        <div className=\"grid grid-cols-1 lg:grid-cols-3 gap-6\">
          {/* Salary Distribution */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <h3 className=\"text-lg font-semibold text-white mb-4 flex items-center\">
              <DollarSign className=\"h-5 w-5 mr-2 text-yellow-400\" />
              Salary Distribution
            </h3>
            <ResponsiveContainer width=\"100%\" height={250}>
              <PieChart>
                <Pie
                  data={salaryDistribution}
                  cx=\"50%\"
                  cy=\"50%\"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey=\"count\"
                >
                  {salaryDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          {/* Top Companies Hiring */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <h3 className=\"text-lg font-semibold text-white mb-4 flex items-center\">
              <Building2 className=\"h-5 w-5 mr-2 text-blue-400\" />
              Top Hiring Companies
            </h3>
            <div className=\"space-y-3\">
              {['Zoho', 'Freshworks', 'PayPal', 'TCS', 'Cognizant'].map((company, index) => (
                <div key={company} className=\"flex items-center justify-between p-3 bg-white/5 rounded-lg\">
                  <span className=\"text-white font-medium\">{company}</span>
                  <span className=\"text-blue-400 text-sm\">{85 - index * 10} jobs</span>
                </div>
              ))}
            </div>
          </div>

          {/* Upcoming Events */}
          <div className=\"bg-white/10 backdrop-blur-md rounded-xl border border-white/20 p-6\">
            <h3 className=\"text-lg font-semibold text-white mb-4 flex items-center\">
              <Calendar className=\"h-5 w-5 mr-2 text-purple-400\" />
              Upcoming Events
            </h3>
            <div className=\"space-y-3\">
              <div className=\"p-3 bg-white/5 rounded-lg\">
                <p className=\"text-white font-medium\">Chennai Python Meetup</p>
                <p className=\"text-purple-400 text-sm\">Dec 15 • 250+ attendees</p>
              </div>
              <div className=\"p-3 bg-white/5 rounded-lg\">
                <p className=\"text-white font-medium\">React Chennai</p>
                <p className=\"text-green-400 text-sm\">Dec 18 • 180+ attendees</p>
              </div>
              <div className=\"p-3 bg-white/5 rounded-lg\">
                <p className=\"text-white font-medium\">AI/ML Conference</p>
                <p className=\"text-blue-400 text-sm\">Dec 22 • 500+ attendees</p>
              </div>
            </div>
          </div>
        </div>

        {/* Agent Status Footer */}
        <div className=\"mt-8 bg-white/5 backdrop-blur-md rounded-xl border border-white/10 p-4\">
          <h4 className=\"text-white font-medium mb-3 flex items-center\">
            <Activity className=\"h-5 w-5 mr-2 text-green-400\" />
            AI Agent Status
          </h4>
          <div className=\"grid grid-cols-2 md:grid-cols-5 gap-4\">
            {[
              'Job Market Scout',
              'Salary Intelligence', 
              'Tech Stack Monitor',
              'Startup Tracker',
              'Community Pulse'
            ].map((agent) => (
              <div key={agent} className=\"flex items-center space-x-2\">
                <div className=\"w-2 h-2 bg-green-400 rounded-full animate-pulse\"></div>
                <span className=\"text-sm text-white\">{agent}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;