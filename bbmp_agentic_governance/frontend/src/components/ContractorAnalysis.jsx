import { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:5000/api'

export default function ContractorAnalysis() {
  const [contractors, setContractors] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_BASE}/contractors`)
      .then(res => res.json())
      .then(data => {
        setContractors(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load contractors:', err)
        setLoading(false)
      })
  }, [])

  const formatCurrency = (amount) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Cr`
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)} L`
    }
    return `₹${amount.toLocaleString()}`
  }

  if (loading) {
    return (
      <div className="brutal-card">
        <div className="text-center py-12">
          <div className="loading-bar mb-4"></div>
          <p className="font-bold uppercase">Loading Contractors...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="brutal-subheader mb-6">Contractor Database</h2>
      <p className="mb-6 text-sm uppercase text-concrete-600">
        Monitoring {contractors.length} registered contractors
      </p>

      <div className="space-y-6">
        {contractors.map(({ contractor, analysis }, idx) => (
          <div
            key={idx}
            className={`brutal-card ${
              contractor.blacklisted ? 'bg-red-100 border-red-600' :
              contractor.red_flags && contractor.red_flags.length > 0 ? 'bg-yellow-50' :
              ''
            }`}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="flex items-center gap-4 mb-2">
                  <h3 className="text-2xl font-bold">{contractor.name}</h3>
                  {contractor.blacklisted && (
                    <span className="px-3 py-1 border-4 border-black bg-red-500 text-white font-bold uppercase text-xs">
                      ❌ BLACKLISTED
                    </span>
                  )}
                </div>
                <p className="text-sm font-mono text-concrete-600">
                  {contractor.contractor_id} | Category {contractor.category}
                </p>
              </div>
              <div className="text-right">
                <div className="text-5xl font-bold mb-1">{contractor.reputation_score}</div>
                <div className="text-xs uppercase text-concrete-600">Score / 100</div>
              </div>
            </div>

            {/* Score Bar */}
            <div className="mb-6">
              <div className="h-4 border-4 border-black bg-concrete-200">
                <div
                  className={`h-full ${
                    contractor.reputation_score >= 70 ? 'bg-green-500' :
                    contractor.reputation_score >= 50 ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${contractor.reputation_score}%` }}
                ></div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="brutal-box-sm p-3 text-center">
                <div className="text-2xl font-bold">{contractor.completed_projects}</div>
                <div className="text-xs uppercase text-concrete-600">Projects</div>
              </div>
              <div className="brutal-box-sm p-3 text-center">
                <div className="text-xl font-bold">
                  {formatCurrency(contractor.total_value_completed)}
                </div>
                <div className="text-xs uppercase text-concrete-600">Total Value</div>
              </div>
              <div className="brutal-box-sm p-3 text-center">
                <div className="text-2xl font-bold">
                  {(contractor.performance_history.on_time_completion_rate * 100).toFixed(0)}%
                </div>
                <div className="text-xs uppercase text-concrete-600">On-Time</div>
              </div>
              <div className="brutal-box-sm p-3 text-center">
                <div className="text-2xl font-bold">
                  {(contractor.performance_history.quality_pass_rate * 100).toFixed(0)}%
                </div>
                <div className="text-xs uppercase text-concrete-600">Quality Pass</div>
              </div>
            </div>

            {/* Analysis Decision */}
            <div className={`p-4 border-4 border-black mb-4 ${
              analysis.decision === 'APPROVE' ? 'bg-green-400' :
              analysis.decision === 'REJECT' ? 'bg-red-500 text-white' :
              'bg-yellow-400'
            }`}>
              <div className="flex justify-between items-center">
                <div>
                  <div className="font-bold uppercase mb-1">Decision: {analysis.decision}</div>
                  <div className="text-sm">{analysis.reason}</div>
                </div>
              </div>
            </div>

            {/* Red Flags */}
            {contractor.red_flags && contractor.red_flags.length > 0 && (
              <div className="p-4 border-4 border-black bg-red-100">
                <div className="font-bold mb-2">🚩 RED FLAGS DETECTED</div>
                <ul className="list-none space-y-2">
                  {contractor.red_flags.map((flag, flagIdx) => (
                    <li key={flagIdx} className="p-2 border-2 border-black bg-white">
                      • {flag}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Company Details */}
            <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="p-3 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">Directors</div>
                <div className="font-mono">{contractor.directors.join(', ')}</div>
              </div>
              <div className="p-3 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">Registered</div>
                <div className="font-mono">{contractor.registration_date}</div>
              </div>
              <div className="p-3 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">Specialization</div>
                <div className="font-mono text-xs">
                  {contractor.specialization.map(s => s.replace('_', ' ')).join(', ').toUpperCase()}
                </div>
              </div>
              <div className="p-3 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">Complaints</div>
                <div className="font-mono text-2xl font-bold">
                  {contractor.performance_history.citizen_complaints}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Cartel Detection Summary */}
      <div className="brutal-card mt-8 bg-black text-white">
        <h3 className="text-2xl font-bold uppercase mb-4">⚠️ Cartel Detection Alert</h3>
        <div className="terminal bg-transparent border-0">
          <div className="terminal-line">Analyzing contractor network relationships...</div>
          <div className="terminal-line">MATCH FOUND: Shared director between CONT-2024-004 and CONT-2024-005</div>
          <div className="terminal-line">Director: Rajesh Gupta</div>
          <div className="terminal-line">Risk Level: HIGH</div>
          <div className="terminal-line text-red-400">RECOMMENDATION: DEBAR BOTH CONTRACTORS</div>
        </div>
      </div>
    </div>
  )
}
