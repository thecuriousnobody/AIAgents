import { useState, useEffect } from 'react'

const API_BASE = 'http://localhost:5000/api'

export default function DPRList() {
  const [dprs, setDprs] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedDpr, setSelectedDpr] = useState(null)

  useEffect(() => {
    fetch(`${API_BASE}/dprs`)
      .then(res => res.json())
      .then(data => {
        setDprs(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load DPRs:', err)
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
          <p className="font-bold uppercase">Loading DPRs...</p>
        </div>
      </div>
    )
  }

  if (selectedDpr) {
    const { dpr, validation } = selectedDpr
    return (
      <div>
        <button
          onClick={() => setSelectedDpr(null)}
          className="brutal-button mb-6"
        >
          ← Back to List
        </button>

        <div className="brutal-card">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-3xl font-bold uppercase mb-2">{dpr.dpr_id}</h2>
              <p className="text-xl">{dpr.title}</p>
            </div>
            <span className={`
              px-4 py-2 border-4 border-black font-bold uppercase
              ${validation.overall_status === 'APPROVED' ? 'bg-green-400' :
                validation.overall_status === 'REJECTED' ? 'bg-red-500 text-white' :
                'bg-yellow-400'}
            `}>
              {validation.overall_status}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div className="brutal-box-sm p-4">
              <div className="text-xs uppercase text-concrete-600 mb-1">Zone/Ward</div>
              <div className="font-bold">{dpr.zone}, Ward {dpr.ward}</div>
            </div>
            <div className="brutal-box-sm p-4">
              <div className="text-xs uppercase text-concrete-600 mb-1">Project Type</div>
              <div className="font-bold uppercase">{dpr.project_type.replace('_', ' ')}</div>
            </div>
            <div className="brutal-box-sm p-4">
              <div className="text-xs uppercase text-concrete-600 mb-1">Estimated Cost</div>
              <div className="font-bold text-xl">{formatCurrency(dpr.estimated_cost)}</div>
            </div>
          </div>

          {/* DPR Integrity Analysis */}
          <div className="brutal-card bg-concrete-100">
            <h3 className="text-xl font-bold uppercase mb-4">◼ DPR Integrity Analysis</h3>
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="font-bold">Decision:</span>
                <span className={`
                  px-3 py-1 border-2 border-black font-bold uppercase text-xs
                  ${validation.dpr_integrity.decision === 'APPROVE' ? 'bg-green-400' :
                    validation.dpr_integrity.decision === 'REJECT' ? 'bg-red-500 text-white' :
                    'bg-yellow-400'}
                `}>
                  {validation.dpr_integrity.decision}
                </span>
              </div>
              <p className="text-sm p-3 border-2 border-black bg-white">{validation.dpr_integrity.reason}</p>
            </div>

            {validation.dpr_integrity.critical_issues && validation.dpr_integrity.critical_issues.length > 0 && (
              <div className="mb-4">
                <div className="font-bold mb-2">❌ Critical Issues:</div>
                <ul className="list-none">
                  {validation.dpr_integrity.critical_issues.map((issue, idx) => (
                    <li key={idx} className="p-2 mb-2 border-2 border-black bg-red-100">
                      • {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {validation.dpr_integrity.warnings && validation.dpr_integrity.warnings.length > 0 && (
              <div>
                <div className="font-bold mb-2">⚠️ Warnings:</div>
                <ul className="list-none">
                  {validation.dpr_integrity.warnings.map((warning, idx) => (
                    <li key={idx} className="p-2 mb-2 border-2 border-black bg-yellow-100">
                      • {warning}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Budget Analysis */}
          <div className="brutal-card bg-concrete-100 mt-6">
            <h3 className="text-xl font-bold uppercase mb-4">◼ Budget Analysis</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="text-center p-4 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">DPR Estimate</div>
                <div className="text-2xl font-bold">{formatCurrency(validation.budget_analysis.dpr_estimate)}</div>
              </div>
              <div className="text-center p-4 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">SoR Estimate</div>
                <div className="text-2xl font-bold">{formatCurrency(validation.budget_analysis.sor_estimate)}</div>
              </div>
              <div className="text-center p-4 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">Variance</div>
                <div className={`text-2xl font-bold ${
                  Math.abs(validation.budget_analysis.variance_percentage) > 20 ? 'text-red-600' :
                  Math.abs(validation.budget_analysis.variance_percentage) > 10 ? 'text-yellow-600' :
                  'text-green-600'
                }`}>
                  {validation.budget_analysis.variance_percentage > 0 ? '+' : ''}
                  {validation.budget_analysis.variance_percentage.toFixed(1)}%
                </div>
              </div>
            </div>
            <div className="p-4 border-2 border-black bg-white">
              <div className="font-bold mb-2">Decision: {validation.budget_analysis.decision}</div>
              <p>{validation.budget_analysis.reason}</p>
            </div>
          </div>

          {/* Anomalies */}
          {validation.anomalies && validation.anomalies.length > 0 && (
            <div className="brutal-card bg-red-100 border-red-600 mt-6">
              <h3 className="text-xl font-bold uppercase mb-4">🚨 Anomalies Detected</h3>
              <ul className="list-none">
                {validation.anomalies.map((anomaly, idx) => (
                  <li key={idx} className="p-3 mb-2 border-2 border-black bg-white">
                    • {anomaly}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Project Details */}
          <div className="brutal-card mt-6">
            <h3 className="text-xl font-bold uppercase mb-4">Project Details</h3>
            <div className="space-y-3">
              <div className="p-3 border-2 border-black bg-white">
                <div className="text-xs uppercase text-concrete-600 mb-1">Justification</div>
                <p>{dpr.justification}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 border-2 border-black bg-white">
                  <div className="text-xs uppercase text-concrete-600 mb-1">Citizen Complaints</div>
                  <div className="text-2xl font-bold">{dpr.citizen_complaints}</div>
                </div>
                <div className="p-3 border-2 border-black bg-white">
                  <div className="text-xs uppercase text-concrete-600 mb-1">Timeline</div>
                  <div className="text-2xl font-bold">{dpr.estimated_timeline_days} days</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div>
      <h2 className="brutal-subheader mb-6">DPR Analysis Dashboard</h2>
      <p className="mb-6 text-sm uppercase text-concrete-600">
        Analyzing {dprs.length} Detailed Project Reports
      </p>

      <div className="space-y-4">
        {dprs.map(({ dpr, validation }, idx) => (
          <div
            key={idx}
            className="brutal-card hover:shadow-brutal-lg transition-all cursor-pointer"
            onClick={() => setSelectedDpr({ dpr, validation })}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-4 mb-2">
                  <h3 className="text-xl font-bold">{dpr.dpr_id}</h3>
                  <span className={`
                    px-3 py-1 border-2 border-black font-bold uppercase text-xs
                    ${validation.overall_status === 'APPROVED' ? 'bg-green-400' :
                      validation.overall_status === 'REJECTED' ? 'bg-red-500 text-white' :
                      'bg-yellow-400'}
                  `}>
                    {validation.overall_status}
                  </span>
                </div>
                <p className="text-sm mb-3">{dpr.title}</p>
                <div className="flex gap-6 text-xs">
                  <span className="font-mono">
                    <strong>Zone:</strong> {dpr.zone}
                  </span>
                  <span className="font-mono">
                    <strong>Cost:</strong> {formatCurrency(dpr.estimated_cost)}
                  </span>
                  <span className="font-mono">
                    <strong>Variance:</strong>
                    <span className={
                      Math.abs(validation.budget_analysis.variance_percentage) > 20 ? 'text-red-600 font-bold' :
                      Math.abs(validation.budget_analysis.variance_percentage) > 10 ? 'text-yellow-600 font-bold' :
                      'text-green-600'
                    }>
                      {' '}{validation.budget_analysis.variance_percentage > 0 ? '+' : ''}
                      {validation.budget_analysis.variance_percentage.toFixed(1)}%
                    </span>
                  </span>
                </div>
              </div>
              <div className="text-right">
                <button className="brutal-button-secondary text-sm px-4 py-2">
                  View Details →
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
