import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'
import DPRList from './components/DPRList'
import ContractorAnalysis from './components/ContractorAnalysis'
import ScenarioRunner from './components/ScenarioRunner'
import './index.css'

const API_BASE = 'http://localhost:5000/api'

function App() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [stats, setStats] = useState(null)
  const [systemStatus, setSystemStatus] = useState('loading')

  useEffect(() => {
    // Check system health
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(data => {
        setSystemStatus('online')
        console.log('System online:', data)
      })
      .catch(err => {
        setSystemStatus('offline')
        console.error('System offline:', err)
      })

    // Load stats
    fetch(`${API_BASE}/stats`)
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(err => console.error('Failed to load stats:', err))
  }, [])

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: '▣' },
    { id: 'dprs', label: 'DPR Analysis', icon: '◰' },
    { id: 'contractors', label: 'Contractors', icon: '◪' },
    { id: 'scenarios', label: 'Live Demo', icon: '▶' },
  ]

  return (
    <div className="min-h-screen bg-concrete-100">
      {/* Header */}
      <header className="brutal-box mb-8 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="brutal-header">BBMP</h1>
              <p className="text-2xl font-bold uppercase tracking-wide">
                Agentic Governance System
              </p>
              <p className="text-sm mt-2 font-mono text-concrete-600">
                AUTOMATING TRANSPARENT GOVERNANCE WITH AI AGENTS
              </p>
            </div>
            <div className="text-right">
              <div className={`inline-block px-4 py-2 border-4 border-black font-bold ${
                systemStatus === 'online' ? 'bg-green-400' :
                systemStatus === 'offline' ? 'bg-red-500 text-white' :
                'bg-yellow-400'
              }`}>
                SYSTEM: {systemStatus.toUpperCase()}
              </div>
              {stats && (
                <div className="mt-4 text-right">
                  <div className="text-4xl font-bold">₹{stats.projected_savings}</div>
                  <div className="text-xs uppercase tracking-wider">CRORES SAVED/YR</div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <div className="max-w-7xl mx-auto px-4 mb-8">
        <nav className="flex gap-4 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                px-6 py-3 border-4 border-black font-bold uppercase tracking-wider
                whitespace-nowrap transition-colors duration-100
                ${activeTab === tab.id
                  ? 'bg-black text-white'
                  : 'bg-white text-black hover:bg-black hover:text-white'
                }
              `}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 pb-12">
        {activeTab === 'dashboard' && <Dashboard stats={stats} />}
        {activeTab === 'dprs' && <DPRList />}
        {activeTab === 'contractors' && <ContractorAnalysis />}
        {activeTab === 'scenarios' && <ScenarioRunner />}
      </main>

      {/* Footer */}
      <footer className="mt-12 p-8 brutal-box">
        <div className="max-w-7xl mx-auto text-center">
          <p className="font-bold uppercase">
            Phase 0: Proof of Concept | Built with CrewAI + Claude Sonnet 4.5
          </p>
          <p className="text-xs mt-2 text-concrete-600">
            Open Source Civic Tech | github.com/thecuriousnobody/AIAgents
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
