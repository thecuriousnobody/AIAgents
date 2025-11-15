"""
BBMP Agentic Governance System - Custom Tools
Tools for agents to interact with BBMP data and systems
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math


class BBMPDataLoader:
    """Load mock BBMP data from JSON files"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._sor_cache = None
        self._contractors_cache = None
        self._dprs_cache = None

    def load_schedule_of_rates(self) -> List[Dict]:
        """Load Karnataka PWD Schedule of Rates"""
        if self._sor_cache is None:
            with open(f"{self.data_dir}/schedule_of_rates.json", 'r') as f:
                self._sor_cache = json.load(f)
        return self._sor_cache

    def load_contractors(self) -> List[Dict]:
        """Load contractor database"""
        if self._contractors_cache is None:
            with open(f"{self.data_dir}/contractors.json", 'r') as f:
                self._contractors_cache = json.load(f)
        return self._contractors_cache

    def load_dprs(self) -> List[Dict]:
        """Load sample DPRs"""
        if self._dprs_cache is None:
            with open(f"{self.data_dir}/sample_dprs.json", 'r') as f:
                self._dprs_cache = json.load(f)
        return self._dprs_cache

    def get_sor_item(self, item_code: str) -> Optional[Dict]:
        """Get specific SoR item by code"""
        sor = self.load_schedule_of_rates()
        for item in sor:
            if item['item_code'] == item_code:
                return item
        return None

    def get_contractor(self, contractor_id: str) -> Optional[Dict]:
        """Get contractor by ID"""
        contractors = self.load_contractors()
        for contractor in contractors:
            if contractor['contractor_id'] == contractor_id:
                return contractor
        return None


class BudgetValidator:
    """Validate project budgets against Schedule of Rates"""

    def __init__(self, data_loader: BBMPDataLoader):
        self.data_loader = data_loader

    def calculate_sor_estimate(self, technical_details: Dict) -> Dict[str, Any]:
        """Calculate project cost based on SoR rates"""
        sor = self.data_loader.load_schedule_of_rates()

        # Create lookup dict
        sor_lookup = {item['item_code']: item for item in sor}

        total_material_cost = 0
        line_items = []

        if 'layers' in technical_details:
            for layer in technical_details['layers']:
                layer_type = layer['type']
                quantity = layer['quantity']
                unit = layer.get('unit', 'sqm')

                # Find matching SoR item
                sor_item = None
                for item in sor:
                    if layer_type in item['description'] or layer_type == item['description'].split()[0]:
                        sor_item = item
                        break

                if sor_item:
                    line_cost = quantity * sor_item['rate_inr']
                    total_material_cost += line_cost
                    line_items.append({
                        'description': sor_item['description'],
                        'item_code': sor_item['item_code'],
                        'quantity': quantity,
                        'unit': unit,
                        'rate': sor_item['rate_inr'],
                        'cost': line_cost
                    })

        # Add overheads (15% materials, 25% labor estimate, 10% equipment, 5% overhead)
        labor_cost = total_material_cost * 0.25
        equipment_cost = total_material_cost * 0.10
        overhead_cost = total_material_cost * 0.05

        total_estimate = total_material_cost + labor_cost + equipment_cost + overhead_cost

        return {
            'material_cost': total_material_cost,
            'labor_cost': labor_cost,
            'equipment_cost': equipment_cost,
            'overhead_cost': overhead_cost,
            'total_estimate': total_estimate,
            'line_items': line_items
        }

    def validate_dpr_budget(self, dpr: Dict) -> Dict[str, Any]:
        """Validate DPR estimated cost against SoR"""
        sor_estimate = self.calculate_sor_estimate(dpr['technical_details'])
        dpr_estimate = dpr['estimated_cost']

        variance = (dpr_estimate - sor_estimate['total_estimate']) / sor_estimate['total_estimate']
        variance_percentage = variance * 100

        # Determine decision based on variance thresholds
        if abs(variance) <= 0.10:
            decision = "AUTO_APPROVE"
            reason = f"Budget within 10% of SoR (variance: {variance_percentage:.1f}%)"
        elif abs(variance) <= 0.20:
            decision = "FLAG_FOR_REVIEW"
            reason = f"Budget variance {variance_percentage:.1f}% requires human review"
        elif abs(variance) <= 0.50:
            decision = "AUTO_REJECT"
            reason = f"Budget variance {variance_percentage:.1f}% exceeds acceptable limit"
        else:
            decision = "ESCALATE"
            reason = f"Critical budget variance {variance_percentage:.1f}% - possible fraud"

        return {
            'dpr_id': dpr['dpr_id'],
            'dpr_estimate': dpr_estimate,
            'sor_estimate': sor_estimate['total_estimate'],
            'variance_amount': dpr_estimate - sor_estimate['total_estimate'],
            'variance_percentage': variance_percentage,
            'decision': decision,
            'reason': reason,
            'detailed_estimate': sor_estimate
        }


class DPRValidator:
    """Validate DPR completeness and authenticity"""

    def __init__(self, data_loader: BBMPDataLoader):
        self.data_loader = data_loader

    def check_duplicate_projects(self, dpr: Dict) -> List[str]:
        """Check for duplicate/overlapping projects"""
        issues = []

        # Simple check: look for duplicate flag in DPR
        if 'flags' in dpr:
            duplicates = [flag for flag in dpr['flags'] if 'Duplicate' in flag or 'duplicate' in flag]
            if duplicates:
                issues.extend(duplicates)

        return issues

    def validate_documentation(self, dpr: Dict) -> Dict[str, Any]:
        """Validate required documentation and surveys"""
        issues = []
        warnings = []

        tech = dpr.get('technical_details', {})

        # Check traffic study (required for roads > 1 crore)
        if dpr['estimated_cost'] > 10000000:
            if not tech.get('traffic_study_date'):
                issues.append("Traffic study required for projects > ₹1 crore")
            else:
                study_date = datetime.strptime(tech['traffic_study_date'], '%Y-%m-%d')
                if (datetime.now() - study_date).days > 180:
                    warnings.append(f"Traffic study is {(datetime.now() - study_date).days} days old (>6 months)")

        # Check soil test
        if dpr['project_type'] in ['road_asphalting', 'concrete_roads']:
            if not tech.get('soil_test_date'):
                issues.append("Soil/geotechnical test required for road projects")
            else:
                test_date = datetime.strptime(tech['soil_test_date'], '%Y-%m-%d')
                if (datetime.now() - test_date).days > 730:
                    issues.append(f"Soil test older than 2 years - must be redone")

        # Check citizen complaints alignment
        if dpr['citizen_complaints'] == 0:
            warnings.append("No citizen complaints on record - verify genuine need")

        # Check ward committee approval
        if not dpr.get('ward_committee_approval'):
            warnings.append("No ward committee approval - required for community buy-in")

        # Check for duplicate projects
        duplicate_issues = self.check_duplicate_projects(dpr)
        if duplicate_issues:
            issues.extend(duplicate_issues)

        # Determine decision
        if len(issues) > 0:
            decision = "REJECT"
            reason = f"DPR has {len(issues)} critical issues"
        elif len(warnings) > 2:
            decision = "FLAG_FOR_REVIEW"
            reason = f"DPR has {len(warnings)} warnings requiring review"
        elif len(warnings) > 0:
            decision = "FLAG_FOR_REVIEW"
            reason = f"DPR has minor issues - recommend review"
        else:
            decision = "APPROVE"
            reason = "All documentation complete and valid"

        return {
            'dpr_id': dpr['dpr_id'],
            'decision': decision,
            'reason': reason,
            'critical_issues': issues,
            'warnings': warnings,
            'justification_quality': self._assess_justification(dpr.get('justification', ''))
        }

    def _assess_justification(self, justification: str) -> str:
        """Assess quality of project justification"""
        if not justification:
            return "Missing"

        # Simple heuristic based on length and keywords
        keywords = ['complaint', 'citizen', 'traffic', 'flooding', 'deteriorat', 'urgent', 'committee']
        keyword_count = sum(1 for kw in keywords if kw.lower() in justification.lower())

        if len(justification) < 50:
            return "Vague"
        elif keyword_count >= 3 and len(justification) > 100:
            return "Strong"
        elif keyword_count >= 2:
            return "Adequate"
        else:
            return "Weak"


class ContractorAnalyzer:
    """Analyze contractor credibility and detect cartels"""

    def __init__(self, data_loader: BBMPDataLoader):
        self.data_loader = data_loader

    def analyze_contractor(self, contractor_id: str) -> Dict[str, Any]:
        """Analyze single contractor credibility"""
        contractor = self.data_loader.get_contractor(contractor_id)

        if not contractor:
            return {
                'contractor_id': contractor_id,
                'decision': 'REJECT',
                'reason': 'Contractor not found in database'
            }

        score = contractor['reputation_score']
        red_flags = contractor.get('red_flags', [])
        blacklisted = contractor.get('blacklisted', False)

        if blacklisted:
            decision = "REJECT"
            reason = "Contractor is blacklisted"
        elif score >= 70 and len(red_flags) == 0:
            decision = "APPROVE"
            reason = f"Contractor has good reputation (score: {score}/100)"
        elif score >= 50:
            decision = "FLAG_FOR_REVIEW"
            reason = f"Contractor score {score}/100 - review recommended. Red flags: {len(red_flags)}"
        else:
            decision = "REJECT"
            reason = f"Contractor score {score}/100 below threshold. Red flags: {len(red_flags)}"

        return {
            'contractor_id': contractor_id,
            'name': contractor['name'],
            'reputation_score': score,
            'red_flags': red_flags,
            'blacklisted': blacklisted,
            'decision': decision,
            'reason': reason,
            'performance_history': contractor['performance_history']
        }

    def detect_cartel_network(self, contractor_ids: List[str]) -> Dict[str, Any]:
        """Detect potential cartel connections between bidders"""
        contractors = self.data_loader.load_contractors()
        bidders = [c for c in contractors if c['contractor_id'] in contractor_ids]

        connections = []

        # Check for shared directors
        for i, bidder1 in enumerate(bidders):
            for bidder2 in bidders[i+1:]:
                shared_directors = set(bidder1['directors']) & set(bidder2['directors'])
                if shared_directors:
                    connections.append({
                        'type': 'shared_director',
                        'contractor_1': bidder1['contractor_id'],
                        'contractor_2': bidder2['contractor_id'],
                        'shared': list(shared_directors)
                    })

        # Check for same address patterns
        for i, bidder1 in enumerate(bidders):
            for bidder2 in bidders[i+1:]:
                if bidder1['address'].split('-')[-1] == bidder2['address'].split('-')[-1]:
                    # Same pincode
                    connections.append({
                        'type': 'same_area',
                        'contractor_1': bidder1['contractor_id'],
                        'contractor_2': bidder2['contractor_id'],
                        'detail': 'Same pincode'
                    })

        cartel_risk = "HIGH" if len(connections) > 0 else "LOW"

        return {
            'bidder_count': len(bidders),
            'connections_found': len(connections),
            'connections': connections,
            'cartel_risk': cartel_risk
        }


class AnomalyDetector:
    """Detect patterns and anomalies in BBMP data"""

    def __init__(self, data_loader: BBMPDataLoader):
        self.data_loader = data_loader

    def detect_anomalies_in_dpr(self, dpr: Dict) -> List[str]:
        """Detect various anomalies in a DPR"""
        anomalies = []

        # Already flagged issues
        if 'flags' in dpr and len(dpr['flags']) > 0:
            anomalies.extend(dpr['flags'])

        # Cost anomalies
        cost_breakdown = dpr.get('cost_breakdown', {})
        total_breakdown = sum(cost_breakdown.values())
        if abs(total_breakdown - dpr['estimated_cost']) > 1000:
            anomalies.append(f"Cost breakdown ({total_breakdown}) doesn't match estimated cost ({dpr['estimated_cost']})")

        # Material cost ratio check (should be 60-70% typically)
        if cost_breakdown:
            material_ratio = cost_breakdown.get('materials', 0) / dpr['estimated_cost']
            if material_ratio < 0.50 or material_ratio > 0.80:
                anomalies.append(f"Unusual material cost ratio: {material_ratio*100:.1f}% (expected 60-70%)")

        return anomalies


def format_currency(amount: float) -> str:
    """Format currency in Indian lakhs/crores"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount:,.0f}"
