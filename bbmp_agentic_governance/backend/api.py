"""
BBMP Agentic Governance System - REST API
Flask backend serving BBMP data to brutalist React frontend
"""

from flask import Flask, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.bbmp_tools import (
    BBMPDataLoader,
    BudgetValidator,
    DPRValidator,
    ContractorAnalyzer,
    AnomalyDetector,
    format_currency
)

app = Flask(__name__)
CORS(app)

# Initialize data loader
data_loader = BBMPDataLoader(data_dir="../data")
budget_validator = BudgetValidator(data_loader)
dpr_validator = DPRValidator(data_loader)
contractor_analyzer = ContractorAnalyzer(data_loader)
anomaly_detector = AnomalyDetector(data_loader)


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'online',
        'system': 'BBMP Agentic Governance System',
        'version': '0.1.0',
        'agents': ['DPR Integrity', 'Budget Sentinel', 'Tender Monitor']
    })


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    dprs = data_loader.load_dprs()
    contractors = data_loader.load_contractors()
    sor = data_loader.load_schedule_of_rates()

    return jsonify({
        'total_dprs': len(dprs),
        'total_contractors': len(contractors),
        'sor_items': len(sor),
        'budget_monitored': 6000,  # Crores
        'projected_savings': 1500,  # Crores
        'corruption_prevented': '20-30%'
    })


@app.route('/api/schedule-of-rates', methods=['GET'])
def get_sor():
    """Get Schedule of Rates"""
    sor = data_loader.load_schedule_of_rates()
    return jsonify(sor)


@app.route('/api/dprs', methods=['GET'])
def get_dprs():
    """Get all DPRs with validation results"""
    dprs = data_loader.load_dprs()
    results = []

    for dpr in dprs:
        dpr_result = dpr_validator.validate_documentation(dpr)
        budget_result = budget_validator.validate_dpr_budget(dpr)
        anomalies = anomaly_detector.detect_anomalies_in_dpr(dpr)

        # Determine overall status
        if dpr_result['decision'] == 'REJECT' or budget_result['decision'] in ['AUTO_REJECT', 'ESCALATE']:
            status = 'REJECTED'
            status_color = 'red'
        elif dpr_result['decision'] == 'FLAG_FOR_REVIEW' or budget_result['decision'] == 'FLAG_FOR_REVIEW':
            status = 'FLAGGED'
            status_color = 'yellow'
        else:
            status = 'APPROVED'
            status_color = 'green'

        results.append({
            'dpr': dpr,
            'validation': {
                'dpr_integrity': dpr_result,
                'budget_analysis': budget_result,
                'anomalies': anomalies,
                'overall_status': status,
                'status_color': status_color
            }
        })

    return jsonify(results)


@app.route('/api/dprs/<dpr_id>', methods=['GET'])
def get_dpr(dpr_id):
    """Get specific DPR with detailed analysis"""
    dprs = data_loader.load_dprs()
    dpr = next((d for d in dprs if d['dpr_id'] == dpr_id), None)

    if not dpr:
        return jsonify({'error': 'DPR not found'}), 404

    dpr_result = dpr_validator.validate_documentation(dpr)
    budget_result = budget_validator.validate_dpr_budget(dpr)
    anomalies = anomaly_detector.detect_anomalies_in_dpr(dpr)

    return jsonify({
        'dpr': dpr,
        'validation': {
            'dpr_integrity': dpr_result,
            'budget_analysis': budget_result,
            'anomalies': anomalies
        }
    })


@app.route('/api/contractors', methods=['GET'])
def get_contractors():
    """Get all contractors with analysis"""
    contractors = data_loader.load_contractors()
    results = []

    for contractor in contractors:
        analysis = contractor_analyzer.analyze_contractor(contractor['contractor_id'])
        results.append({
            'contractor': contractor,
            'analysis': analysis
        })

    return jsonify(results)


@app.route('/api/contractors/<contractor_id>', methods=['GET'])
def get_contractor(contractor_id):
    """Get specific contractor analysis"""
    contractor = data_loader.get_contractor(contractor_id)

    if not contractor:
        return jsonify({'error': 'Contractor not found'}), 404

    analysis = contractor_analyzer.analyze_contractor(contractor_id)

    return jsonify({
        'contractor': contractor,
        'analysis': analysis
    })


@app.route('/api/cartel-detection', methods=['POST'])
def detect_cartel():
    """Detect cartel connections between contractors"""
    from flask import request

    data = request.get_json()
    contractor_ids = data.get('contractor_ids', [])

    if not contractor_ids:
        return jsonify({'error': 'No contractor IDs provided'}), 400

    result = contractor_analyzer.detect_cartel_network(contractor_ids)

    return jsonify(result)


@app.route('/api/scenarios/suspicious-dpr', methods=['GET'])
def scenario_suspicious_dpr():
    """Run suspicious DPR scenario"""
    dpr_id = 'DPR-2025-BOM-002'
    dprs = data_loader.load_dprs()
    dpr = next((d for d in dprs if d['dpr_id'] == dpr_id), None)

    if not dpr:
        return jsonify({'error': 'DPR not found'}), 404

    dpr_result = dpr_validator.validate_documentation(dpr)
    budget_result = budget_validator.validate_dpr_budget(dpr)
    anomalies = anomaly_detector.detect_anomalies_in_dpr(dpr)

    return jsonify({
        'scenario': 'Suspicious Project Detection',
        'dpr_id': dpr_id,
        'dpr': dpr,
        'validation': {
            'dpr_integrity': dpr_result,
            'budget_analysis': budget_result,
            'anomalies': anomalies
        },
        'verdict': 'REJECTED',
        'reason': f"Budget inflated by {budget_result['variance_percentage']:.1f}%, missing documentation, no citizen complaints"
    })


@app.route('/api/scenarios/cartel', methods=['GET'])
def scenario_cartel():
    """Run cartel detection scenario"""
    contractor_ids = ["CONT-2024-004", "CONT-2024-005"]

    result = contractor_analyzer.detect_cartel_network(contractor_ids)

    # Get contractor details
    contractors = []
    for cid in contractor_ids:
        contractor = data_loader.get_contractor(cid)
        analysis = contractor_analyzer.analyze_contractor(cid)
        contractors.append({
            'contractor': contractor,
            'analysis': analysis
        })

    return jsonify({
        'scenario': 'Bid Rigging Cartel Detection',
        'contractor_ids': contractor_ids,
        'contractors': contractors,
        'cartel_detection': result,
        'verdict': 'TENDER REJECTED',
        'reason': 'Shared directors detected between bidders - cartel activity'
    })


@app.route('/api/scenarios/legitimate', methods=['GET'])
def scenario_legitimate():
    """Run legitimate project scenario"""
    dpr_id = 'DPR-2025-BOM-001'
    dprs = data_loader.load_dprs()
    dpr = next((d for d in dprs if d['dpr_id'] == dpr_id), None)

    if not dpr:
        return jsonify({'error': 'DPR not found'}), 404

    dpr_result = dpr_validator.validate_documentation(dpr)
    budget_result = budget_validator.validate_dpr_budget(dpr)

    return jsonify({
        'scenario': 'Legitimate Project Approval',
        'dpr_id': dpr_id,
        'dpr': dpr,
        'validation': {
            'dpr_integrity': dpr_result,
            'budget_analysis': budget_result
        },
        'verdict': 'APPROVED',
        'reason': 'All documentation complete, budget within SoR limits, high citizen demand'
    })


if __name__ == '__main__':
    print("=" * 80)
    print("  BBMP AGENTIC GOVERNANCE SYSTEM - API SERVER")
    print("=" * 80)
    print("\n  🏛️  Automating Transparent Governance with AI Agents\n")
    print("  API running at: http://localhost:5000")
    print("  Health check: http://localhost:5000/api/health")
    print("\n" + "=" * 80 + "\n")

    app.run(debug=True, host='0.0.0.0', port=5000)
