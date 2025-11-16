import { useState } from 'react'

const API_BASE = 'http://localhost:5000/api'

export default function ScenarioRunner() {
  const [activeScenario, setActiveScenario] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const scenarios = [
    {
      id: 'legitimate',
      title: 'Legitimate Project Approval',
      description: 'HSR Layout road with proper docs, citizen demand, SoR compliance',
      icon: '✓',
      color: 'green',
      expectedOutcome: 'APPROVED'
    },
    {
      id: 'suspicious-dpr',
      title: 'Suspicious Project Detection',
      description: 'Budget inflated 35%, no citizen complaints, missing documentation',
      icon: '✗',
      color: 'red',
      expectedOutcome: 'REJECTED'
    },
    {
      id: 'cartel',
      title: 'Cartel Detection',
      description: 'Two contractors with shared director attempting bid rigging',
      icon: '⚠',
      color: 'yellow',
      expectedOutcome: 'REJECTED - CARTEL'
    },
  ]

  const runScenario = async (scenarioId) => {
    setLoading(true)
    setActiveScenario(scenarioId)
    setResult(null)

    try {
      const response = await fetch(`${API_BASE}/scenarios/${scenarioId}`)
      const data = await response.json()

      // Simulate processing time for dramatic effect
      await new Promise(resolve => setTimeout(resolve, 1500))

      setResult(data)
    } catch (err) {
      console.error('Failed to run scenario:', err)
      setResult({ error: 'Failed to run scenario' })
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount) => {
    if (amount >= 10000000) {
      return `₹${(amount / 10000000).toFixed(2)} Cr`
    } else if (amount >= 100000) {
      return `₹${(amount / 100000).toFixed(2)} L`
    }
    return `₹${amount.toLocaleString()}`
  }

  return (
    <div>
      <h2 className="brutal-subheader mb-6">Live Demo Scenarios</h2>
      <p className="mb-8 text-sm uppercase text-concrete-600">
        Click any scenario to see AI agents in action
      </p>

      {/* Scenario Selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {scenarios.map(scenario => (
          <button
            key={scenario.id}
            onClick={() => runScenario(scenario.id)}
            disabled={loading}
            className={`
              brutal-card text-left hover:shadow-brutal-lg transition-all
              ${activeScenario === scenario.id ? 'ring-4 ring-black' : ''}
              ${loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
            `}
          >
            <div className={`text-6xl mb-4 ${
              scenario.color === 'green' ? 'text-green-600' :
              scenario.color === 'red' ? 'text-red-600' :
              'text-yellow-600'
            }`}>
              {scenario.icon}
            </div>
            <h3 className="text-xl font-bold uppercase mb-2">{scenario.title}</h3>
            <p className="text-sm mb-4">{scenario.description}</p>
            <div className={`px-3 py-1 border-2 border-black inline-block font-bold uppercase text-xs ${
              scenario.color === 'green' ? 'bg-green-400' :
              scenario.color === 'red' ? 'bg-red-500 text-white' :
              'bg-yellow-400'
            }`}>
              Expected: {scenario.expectedOutcome}
            </div>
          </button>
        ))}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="brutal-card">
          <div className="terminal">
            <div className="terminal-line">Initializing AI agents...</div>
            <div className="terminal-line">DPR Integrity Agent: ACTIVE</div>
            <div className="terminal-line">Budget Sentinel: ACTIVE</div>
            <div className="terminal-line">Tender Monitor: ACTIVE</div>
            <div className="terminal-line">Analyzing data...</div>
            <div className="loading-bar mt-4"></div>
          </div>
        </div>
      )}

      {/* Results */}
      {result && !result.error && (
        <div className="space-y-6">
          {/* Verdict Banner */}
          <div className={`brutal-card p-8 text-center ${
            result.verdict.includes('APPROVED') ? 'bg-green-400' :
            result.verdict.includes('REJECTED') ? 'bg-red-500 text-white' :
            'bg-yellow-400'
          }`}>
            <div className="text-6xl font-bold mb-4">{result.verdict}</div>
            <div className="text-xl">{result.reason}</div>
          </div>

          {/* Scenario Details */}
          <div className="brutal-card">
            <h3 className="brutal-subheader text-2xl mb-6">{result.scenario}</h3>

            {result.dpr && (
              <div>
                <h4 className="text-xl font-bold uppercase mb-4">Project Details</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                  <div className="p-4 border-4 border-black bg-white">
                    <div className="text-xs uppercase text-concrete-600 mb-1">DPR ID</div>
                    <div className="text-2xl font-bold">{result.dpr_id}</div>
                  </div>
                  <div className="p-4 border-4 border-black bg-white">
                    <div className="text-xs uppercase text-concrete-600 mb-1">Project</div>
                    <div className="font-bold">{result.dpr.title}</div>
                  </div>
                  <div className="p-4 border-4 border-black bg-white">
                    <div className="text-xs uppercase text-concrete-600 mb-1">Zone</div>
                    <div className="text-xl font-bold">{result.dpr.zone}</div>
                  </div>
                  <div className="p-4 border-4 border-black bg-white">
                    <div className="text-xs uppercase text-concrete-600 mb-1">Estimated Cost</div>
                    <div className="text-xl font-bold">{formatCurrency(result.dpr.estimated_cost)}</div>
                  </div>
                </div>

                {/* Validation Results */}
                {result.validation && (
                  <div>
                    <h4 className="text-xl font-bold uppercase mb-4">Agent Analysis</h4>

                    {/* DPR Integrity */}
                    {result.validation.dpr_integrity && (
                      <div className="mb-4 p-4 border-4 border-black bg-concrete-100">
                        <h5 className="font-bold mb-2">◼ DPR INTEGRITY AGENT</h5>
                        <div className="mb-2">
                          <span className={`px-3 py-1 border-2 border-black font-bold uppercase text-xs ${
                            result.validation.dpr_integrity.decision === 'APPROVE' ? 'bg-green-400' :
                            result.validation.dpr_integrity.decision === 'REJECT' ? 'bg-red-500 text-white' :
                            'bg-yellow-400'
                          }`}>
                            {result.validation.dpr_integrity.decision}
                          </span>
                        </div>
                        <p className="text-sm">{result.validation.dpr_integrity.reason}</p>

                        {result.validation.dpr_integrity.critical_issues &&
                         result.validation.dpr_integrity.critical_issues.length > 0 && (
                          <div className="mt-3">
                            <div className="font-bold text-sm mb-1">Critical Issues:</div>
                            {result.validation.dpr_integrity.critical_issues.map((issue, idx) => (
                              <div key={idx} className="p-2 mb-1 border-2 border-black bg-red-100 text-sm">
                                • {issue}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {/* Budget Analysis */}
                    {result.validation.budget_analysis && (
                      <div className="p-4 border-4 border-black bg-concrete-100">
                        <h5 className="font-bold mb-2">◼ BUDGET SENTINEL</h5>
                        <div className="mb-2">
                          <span className={`px-3 py-1 border-2 border-black font-bold uppercase text-xs ${
                            result.validation.budget_analysis.decision === 'AUTO_APPROVE' ? 'bg-green-400' :
                            result.validation.budget_analysis.decision === 'AUTO_REJECT' ? 'bg-red-500 text-white' :
                            'bg-yellow-400'
                          }`}>
                            {result.validation.budget_analysis.decision}
                          </span>
                        </div>
                        <p className="text-sm mb-3">{result.validation.budget_analysis.reason}</p>

                        <div className="grid grid-cols-3 gap-3">
                          <div className="p-2 border-2 border-black bg-white text-center">
                            <div className="text-xs uppercase text-concrete-600">DPR Est.</div>
                            <div className="font-bold text-sm">
                              {formatCurrency(result.validation.budget_analysis.dpr_estimate)}
                            </div>
                          </div>
                          <div className="p-2 border-2 border-black bg-white text-center">
                            <div className="text-xs uppercase text-concrete-600">SoR Est.</div>
                            <div className="font-bold text-sm">
                              {formatCurrency(result.validation.budget_analysis.sor_estimate)}
                            </div>
                          </div>
                          <div className="p-2 border-2 border-black bg-white text-center">
                            <div className="text-xs uppercase text-concrete-600">Variance</div>
                            <div className={`font-bold ${
                              Math.abs(result.validation.budget_analysis.variance_percentage) > 20
                                ? 'text-red-600' :
                                Math.abs(result.validation.budget_analysis.variance_percentage) > 10
                                  ? 'text-yellow-600'
                                  : 'text-green-600'
                            }`}>
                              {result.validation.budget_analysis.variance_percentage > 0 ? '+' : ''}
                              {result.validation.budget_analysis.variance_percentage.toFixed(1)}%
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Cartel Detection Results */}
            {result.cartel_detection && (
              <div>
                <h4 className="text-xl font-bold uppercase mb-4">Cartel Analysis</h4>
                <div className="p-4 border-4 border-black bg-red-100">
                  <h5 className="font-bold mb-2">◼ TENDER INTEGRITY MONITOR</h5>
                  <div className="mb-3">
                    <span className="px-3 py-1 border-2 border-black bg-red-500 text-white font-bold uppercase text-xs">
                      CARTEL RISK: {result.cartel_detection.cartel_risk}
                    </span>
                  </div>
                  <p className="mb-3 font-bold">
                    {result.cartel_detection.connections_found} suspicious connection(s) detected
                  </p>

                  {result.cartel_detection.connections && result.cartel_detection.connections.length > 0 && (
                    <div className="space-y-2">
                      {result.cartel_detection.connections.map((conn, idx) => (
                        <div key={idx} className="p-3 border-2 border-black bg-white">
                          <div className="font-bold uppercase text-sm mb-1">{conn.type.replace('_', ' ')}</div>
                          <div className="text-sm">
                            {conn.contractor_1} ↔ {conn.contractor_2}
                          </div>
                          {conn.shared && (
                            <div className="text-sm mt-1">
                              <strong>Shared:</strong> {conn.shared.join(', ')}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {result.contractors && (
                  <div className="mt-4">
                    <h5 className="font-bold mb-2">Contractor Details</h5>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {result.contractors.map(({ contractor }, idx) => (
                        <div key={idx} className="p-4 border-4 border-black bg-white">
                          <div className="font-bold mb-2">{contractor.name}</div>
                          <div className="text-sm space-y-1">
                            <div><strong>Score:</strong> {contractor.reputation_score}/100</div>
                            <div><strong>Directors:</strong> {contractor.directors.join(', ')}</div>
                            {contractor.red_flags && contractor.red_flags.length > 0 && (
                              <div className="mt-2 p-2 bg-red-100 border-2 border-black">
                                <strong>🚩 Red Flags:</strong>
                                <ul className="text-xs mt-1">
                                  {contractor.red_flags.map((flag, fIdx) => (
                                    <li key={fIdx}>• {flag}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {result?.error && (
        <div className="brutal-card bg-red-100">
          <p className="font-bold">Error: {result.error}</p>
          <p className="text-sm mt-2">Make sure the Flask backend is running on port 5000</p>
        </div>
      )}
    </div>
  )
}
