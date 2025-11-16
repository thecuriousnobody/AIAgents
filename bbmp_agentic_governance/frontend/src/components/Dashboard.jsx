import { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:5000/api'

export default function Dashboard({ stats }) {
  const [agentStatus, setAgentStatus] = useState([
    { name: 'DPR Integrity Agent', status: 'active', processed: 4 },
    { name: 'Budget Sentinel', status: 'active', processed: 4 },
    { name: 'Tender Monitor', status: 'active', processed: 0 },
  ])

  return (
    <div>
      {/* ASCII Art Banner */}
      <div className="terminal mb-8">
        <pre className="text-xs leading-tight">
{`
 ██████╗  ██████╗ ██╗   ██╗███████╗██████╗ ███╗   ██╗ █████╗ ███╗   ██╗ ██████╗███████╗
██╔════╝ ██╔═══██╗██║   ██║██╔════╝██╔══██╗████╗  ██║██╔══██╗████╗  ██║██╔════╝██╔════╝
██║  ███╗██║   ██║██║   ██║█████╗  ██████╔╝██╔██╗ ██║███████║██╔██╗ ██║██║     █████╗
██║   ██║██║   ██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██║╚██╗██║██╔══██║██║╚██╗██║██║     ██╔══╝
╚██████╔╝╚██████╔╝ ╚████╔╝ ███████╗██║  ██║██║ ╚████║██║  ██║██║ ╚████║╚██████╗███████╗
 ╚═════╝  ╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝╚══════╝
`}
        </pre>
        <div className="mt-4 text-green-400">
          <div className="terminal-line">System operational</div>
          <div className="terminal-line">3 agents active</div>
          <div className="terminal-line">Monitoring ₹6,000 crore budget</div>
          <div className="terminal-line">Corruption detection: ENABLED</div>
        </div>
      </div>

      {/* Impact Metrics */}
      <h2 className="brutal-subheader mb-6">Impact Metrics</h2>
      <div className="data-grid mb-8">
        <div className="metric-box">
          <div className="metric-value text-red-600">₹6,000</div>
          <div className="metric-label">Total Budget (Cr)</div>
        </div>
        <div className="metric-box animate-pulse-brutal">
          <div className="metric-value text-green-600">₹{stats?.projected_savings || '1,500'}</div>
          <div className="metric-label">Projected Savings (Cr/Yr)</div>
        </div>
        <div className="metric-box">
          <div className="metric-value text-black">20-30%</div>
          <div className="metric-label">Leakage Prevented</div>
        </div>
      </div>

      {/* Agent Status */}
      <h2 className="brutal-subheader mb-6">Agent Status</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {agentStatus.map((agent, idx) => (
          <div key={idx} className="brutal-card">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold uppercase">{agent.name}</h3>
              <span className={`px-3 py-1 border-2 border-black font-bold text-xs ${
                agent.status === 'active' ? 'bg-green-400' : 'bg-red-500 text-white'
              }`}>
                {agent.status.toUpperCase()}
              </span>
            </div>
            <div className="text-4xl font-bold mb-2">{agent.processed}</div>
            <div className="text-xs uppercase text-concrete-600">Projects Processed</div>
            <div className="mt-4 h-2 bg-concrete-200 border-2 border-black">
              <div className="h-full bg-black" style={{ width: '75%' }}></div>
            </div>
          </div>
        ))}
      </div>

      {/* System Stats */}
      <h2 className="brutal-subheader mb-6">System Statistics</h2>
      <div className="brutal-card">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold mb-2">{stats?.total_dprs || 4}</div>
            <div className="text-xs uppercase text-concrete-600">DPRs Analyzed</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold mb-2">{stats?.total_contractors || 6}</div>
            <div className="text-xs uppercase text-concrete-600">Contractors Monitored</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold mb-2">{stats?.sor_items || 10}</div>
            <div className="text-xs uppercase text-concrete-600">SoR Items</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-red-600 mb-2">2</div>
            <div className="text-xs uppercase text-concrete-600">Cartels Detected</div>
          </div>
        </div>
      </div>

      {/* Corruption Prevention Stats */}
      <h2 className="brutal-subheader mt-8 mb-6">Corruption Detection Log</h2>
      <div className="brutal-card">
        <table className="w-full font-mono text-sm">
          <tbody>
            <tr className="border-b-2 border-black">
              <td className="py-2 font-bold">2025-11-16 09:23</td>
              <td className="py-2">DPR-2025-BOM-002</td>
              <td className="py-2">
                <span className="status-rejected">REJECTED</span>
              </td>
              <td className="py-2">Budget inflated 35%</td>
            </tr>
            <tr className="border-b-2 border-black">
              <td className="py-2 font-bold">2025-11-16 09:25</td>
              <td className="py-2">DPR-2025-BOM-004</td>
              <td className="py-2">
                <span className="status-rejected">REJECTED</span>
              </td>
              <td className="py-2">Duplicate project detected</td>
            </tr>
            <tr className="border-b-2 border-black">
              <td className="py-2 font-bold">2025-11-16 09:27</td>
              <td className="py-2">CONT-2024-004, CONT-2024-005</td>
              <td className="py-2">
                <span className="status-rejected">CARTEL</span>
              </td>
              <td className="py-2">Shared directors - bid rigging</td>
            </tr>
            <tr>
              <td className="py-2 font-bold">2025-11-16 09:30</td>
              <td className="py-2">DPR-2025-BOM-001</td>
              <td className="py-2">
                <span className="status-approved">APPROVED</span>
              </td>
              <td className="py-2">All checks passed</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  )
}
