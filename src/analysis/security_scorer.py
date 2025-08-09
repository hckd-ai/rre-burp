"""
Security Scoring Engine

Calculates comprehensive security scores based on vulnerability analysis,
security headers, and other security metrics.
"""

import math
from typing import Dict, List, Any
from dataclasses import dataclass

from .security_metrics import (
    SecurityMetrics, 
    VulnerabilityFinding, 
    SecurityLevel,
    VulnerabilityCategory
)


@dataclass
class ScoringWeights:
    """Weights for different security factors in scoring"""
    critical_vulnerability: float = 10.0
    high_vulnerability: float = 7.0
    medium_vulnerability: float = 4.0
    low_vulnerability: float = 1.0
    
    # Security header weights
    missing_security_header: float = 3.0
    weak_security_header: float = 1.5
    
    # Authentication and authorization
    auth_weakness: float = 8.0
    auth_missing: float = 15.0
    
    # Data protection
    sensitive_data_exposure: float = 6.0
    personal_data_exposure: float = 4.0
    
    # API security
    api_security_issue: float = 5.0
    
    # Network security
    tls_weakness: float = 5.0
    network_exposure: float = 4.0


class SecurityScorer:
    """Calculates security scores based on vulnerability analysis"""
    
    def __init__(self, weights: ScoringWeights = None):
        self.weights = weights or ScoringWeights()
        self.max_score = 100.0
    
    def calculate_security_score(self, metrics: SecurityMetrics) -> SecurityMetrics:
        """Calculate comprehensive security score for a website"""
        
        # Calculate individual category scores
        auth_score = self._calculate_authentication_score(metrics)
        authz_score = self._calculate_authorization_score(metrics)
        data_score = self._calculate_data_protection_score(metrics)
        api_score = self._calculate_api_security_score(metrics)
        config_score = self._calculate_configuration_score(metrics)
        
        # Calculate overall score
        overall_score = self._calculate_overall_score(
            auth_score, authz_score, data_score, api_score, config_score
        )
        
        # Update metrics with calculated scores
        metrics.authentication_score = auth_score
        metrics.authorization_score = authz_score
        metrics.data_protection_score = data_score
        metrics.api_security_score = api_score
        metrics.configuration_score = config_score
        metrics.overall_score = overall_score
        
        # Determine risk levels
        metrics.overall_risk = self._determine_risk_level(overall_score)
        metrics.highest_risk = self._determine_highest_risk(metrics.vulnerabilities)
        
        # Count vulnerabilities by severity
        self._count_vulnerabilities(metrics)
        
        return metrics
    
    def _calculate_authentication_score(self, metrics: SecurityMetrics) -> float:
        """Calculate authentication security score"""
        score = self.max_score
        deductions = 0.0
        
        # Check for authentication vulnerabilities
        auth_vulns = [v for v in metrics.vulnerabilities 
                     if v.category == VulnerabilityCategory.AUTHENTICATION]
        
        for vuln in auth_vulns:
            if vuln.severity == SecurityLevel.CRITICAL:
                deductions += self.weights.auth_missing
            elif vuln.severity == SecurityLevel.HIGH:
                deductions += self.weights.auth_weakness
            elif vuln.severity == SecurityLevel.MEDIUM:
                deductions += self.weights.auth_weakness * 0.7
            elif vuln.severity == SecurityLevel.LOW:
                deductions += self.weights.auth_weakness * 0.3
        
        # Check for missing authentication mechanisms
        if not metrics.auth_mechanisms:
            deductions += self.weights.auth_missing
        
        # Check session management issues
        session_issues = [v for v in metrics.vulnerabilities 
                         if v.category == VulnerabilityCategory.SESSION_MANAGEMENT]
        for vuln in session_issues:
            deductions += self.weights.auth_weakness * 0.8
        
        return max(0.0, score - deductions)
    
    def _calculate_authorization_score(self, metrics: SecurityMetrics) -> float:
        """Calculate authorization security score"""
        score = self.max_score
        deductions = 0.0
        
        # Check for authorization vulnerabilities
        authz_vulns = [v for v in metrics.vulnerabilities 
                      if v.category == VulnerabilityCategory.AUTHORIZATION]
        
        for vuln in authz_vulns:
            if vuln.severity == SecurityLevel.CRITICAL:
                deductions += self.weights.high_vulnerability
            elif vuln.severity == SecurityLevel.HIGH:
                deductions += self.weights.high_vulnerability
            elif vuln.severity == SecurityLevel.MEDIUM:
                deductions += self.weights.medium_vulnerability
            elif vuln.severity == SecurityLevel.LOW:
                deductions += self.weights.low_vulnerability
        
        return max(0.0, score - deductions)
    
    def _calculate_data_protection_score(self, metrics: SecurityMetrics) -> float:
        """Calculate data protection security score"""
        score = self.max_score
        deductions = 0.0
        
        # Check for data exposure vulnerabilities
        data_vulns = [v for v in metrics.vulnerabilities 
                     if v.category == VulnerabilityCategory.DATA_EXPOSURE]
        
        for vuln in data_vulns:
            if vuln.severity == SecurityLevel.CRITICAL:
                deductions += self.weights.sensitive_data_exposure * 1.5
            elif vuln.severity == SecurityLevel.HIGH:
                deductions += self.weights.sensitive_data_exposure
            elif vuln.severity == SecurityLevel.MEDIUM:
                deductions += self.weights.personal_data_exposure
            elif vuln.severity == SecurityLevel.LOW:
                deductions += self.weights.personal_data_exposure * 0.5
        
        # Check for sensitive data exposure in findings
        if metrics.sensitive_data_exposure:
            deductions += len(metrics.sensitive_data_exposure) * self.weights.sensitive_data_exposure
        
        return max(0.0, score - deductions)
    
    def _calculate_api_security_score(self, metrics: SecurityMetrics) -> float:
        """Calculate API security score"""
        score = self.max_score
        deductions = 0.0
        
        # Check for API security vulnerabilities
        api_vulns = [v for v in metrics.vulnerabilities 
                    if v.category == VulnerabilityCategory.API_SECURITY]
        
        for vuln in api_vulns:
            if vuln.severity == SecurityLevel.CRITICAL:
                deductions += self.weights.api_security_issue * 1.5
            elif vuln.severity == SecurityLevel.HIGH:
                deductions += self.weights.api_security_issue
            elif vuln.severity == SecurityLevel.MEDIUM:
                deductions += self.weights.api_security_issue * 0.7
            elif vuln.severity == SecurityLevel.LOW:
                deductions += self.weights.api_security_issue * 0.3
        
        # Check for injection vulnerabilities (often affect APIs)
        injection_vulns = [v for v in metrics.vulnerabilities 
                          if v.category == VulnerabilityCategory.INJECTION]
        for vuln in injection_vulns:
            deductions += self.weights.api_security_issue * 0.8
        
        return max(0.0, score - deductions)
    
    def _calculate_configuration_score(self, metrics: SecurityMetrics) -> float:
        """Calculate configuration security score"""
        score = self.max_score
        deductions = 0.0
        
        # Check for configuration vulnerabilities
        config_vulns = [v for v in metrics.vulnerabilities 
                       if v.category == VulnerabilityCategory.CONFIGURATION]
        
        for vuln in config_vulns:
            if vuln.severity == SecurityLevel.CRITICAL:
                deductions += self.weights.medium_vulnerability * 1.5
            elif vuln.severity == SecurityLevel.HIGH:
                deductions += self.weights.medium_vulnerability
            elif vuln.severity == SecurityLevel.MEDIUM:
                deductions += self.weights.medium_vulnerability
            elif vuln.severity == SecurityLevel.LOW:
                deductions += self.weights.low_vulnerability
        
        # Check for missing security headers
        missing_headers = []
        for header in ['strict-transport-security', 'content-security-policy', 
                      'x-frame-options', 'x-content-type-options']:
            if header not in metrics.security_headers:
                missing_headers.append(header)
        
        deductions += len(missing_headers) * self.weights.missing_security_header
        
        # Check for weak security header values
        weak_headers = 0
        if 'x-frame-options' in metrics.security_headers:
            value = metrics.security_headers['x-frame-options']
            if value.lower() not in ['deny', 'sameorigin']:
                weak_headers += 1
        
        deductions += weak_headers * self.weights.weak_security_header
        
        return max(0.0, score - deductions)
    
    def _calculate_overall_score(self, auth_score: float, authz_score: float,
                                data_score: float, api_score: float, 
                                config_score: float) -> float:
        """Calculate overall security score"""
        
        # Weighted average of category scores
        weights = {
            'auth': 0.25,      # Authentication is critical
            'authz': 0.20,     # Authorization is important
            'data': 0.25,      # Data protection is critical
            'api': 0.15,       # API security is important
            'config': 0.15     # Configuration is important
        }
        
        overall_score = (
            auth_score * weights['auth'] +
            authz_score * weights['authz'] +
            data_score * weights['data'] +
            api_score * weights['api'] +
            config_score * weights['config']
        )
        
        return round(overall_score, 2)
    
    def _determine_risk_level(self, score: float) -> SecurityLevel:
        """Determine overall risk level based on score"""
        if score >= 90:
            return SecurityLevel.SECURE
        elif score >= 75:
            return SecurityLevel.LOW
        elif score >= 60:
            return SecurityLevel.MEDIUM
        elif score >= 40:
            return SecurityLevel.HIGH
        else:
            return SecurityLevel.CRITICAL
    
    def _determine_highest_risk(self, vulnerabilities: List[VulnerabilityFinding]) -> SecurityLevel:
        """Determine the highest risk level from vulnerabilities"""
        if not vulnerabilities:
            return SecurityLevel.LOW
        
        severity_levels = [v.severity for v in vulnerabilities]
        
        if SecurityLevel.CRITICAL in severity_levels:
            return SecurityLevel.CRITICAL
        elif SecurityLevel.HIGH in severity_levels:
            return SecurityLevel.HIGH
        elif SecurityLevel.MEDIUM in severity_levels:
            return SecurityLevel.MEDIUM
        elif SecurityLevel.LOW in severity_levels:
            return SecurityLevel.LOW
        else:
            return SecurityLevel.SECURE
    
    def _count_vulnerabilities(self, metrics: SecurityMetrics) -> None:
        """Count vulnerabilities by severity level"""
        metrics.critical_count = len([v for v in metrics.vulnerabilities 
                                    if v.severity == SecurityLevel.CRITICAL])
        metrics.high_count = len([v for v in metrics.vulnerabilities 
                                if v.severity == SecurityLevel.HIGH])
        metrics.medium_count = len([v for v in metrics.vulnerabilities 
                                  if v.severity == SecurityLevel.MEDIUM])
        metrics.low_count = len([v for v in metrics.vulnerabilities 
                               if v.severity == SecurityLevel.LOW])
    
    def compare_sites(self, site_metrics: List[SecurityMetrics]) -> List[Dict[str, Any]]:
        """Compare multiple sites and rank them by security"""
        
        # Add site information if available
        for i, metrics in enumerate(site_metrics):
            if not hasattr(metrics, 'site_name'):
                metrics.site_name = f"Site {i+1}"
            if not hasattr(metrics, 'site_url'):
                metrics.site_url = f"Unknown URL {i+1}"
        
        # Sort by overall score (descending - most secure first)
        sorted_sites = sorted(site_metrics, key=lambda x: x.overall_score, reverse=True)
        
        # Create comparison data
        comparison = []
        for i, metrics in enumerate(sorted_sites):
            comparison.append({
                'rank': i + 1,
                'site_name': getattr(metrics, 'site_name', f"Site {i+1}"),
                'site_url': getattr(metrics, 'site_url', f"Unknown URL {i+1}"),
                'overall_score': metrics.overall_score,
                'overall_risk': metrics.overall_risk.value,
                'highest_risk': metrics.highest_risk.value,
                'vulnerability_summary': {
                    'critical': metrics.critical_count,
                    'high': metrics.high_count,
                    'medium': metrics.medium_count,
                    'low': metrics.low_count
                },
                'category_scores': {
                    'authentication': metrics.authentication_score,
                    'authorization': metrics.authorization_score,
                    'data_protection': metrics.data_protection_score,
                    'api_security': metrics.api_security_score,
                    'configuration': metrics.configuration_score
                },
                'risk_summary': metrics.get_risk_summary(),
                'priority_actions': metrics.get_priority_actions()
            })
        
        return comparison
    
    def generate_security_report(self, site_metrics: List[SecurityMetrics]) -> Dict[str, Any]:
        """Generate comprehensive security report for multiple sites"""
        
        comparison = self.compare_sites(site_metrics)
        
        # Calculate statistics
        total_sites = len(site_metrics)
        avg_score = sum(m.overall_score for m in site_metrics) / total_sites if total_sites > 0 else 0
        
        risk_distribution = {
            'secure': len([m for m in site_metrics if m.overall_risk == SecurityLevel.SECURE]),
            'low': len([m for m in site_metrics if m.overall_risk == SecurityLevel.LOW]),
            'medium': len([m for m in site_metrics if m.overall_risk == SecurityLevel.MEDIUM]),
            'high': len([m for m in site_metrics if m.overall_risk == SecurityLevel.HIGH]),
            'critical': len([m for m in site_metrics if m.overall_risk == SecurityLevel.CRITICAL])
        }
        
        # Most common vulnerabilities
        all_vulns = []
        for metrics in site_metrics:
            all_vulns.extend(metrics.vulnerabilities)
        
        vuln_categories = {}
        for vuln in all_vulns:
            cat = vuln.category.value
            vuln_categories[cat] = vuln_categories.get(cat, 0) + 1
        
        most_common_vulns = sorted(vuln_categories.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'summary': {
                'total_sites': total_sites,
                'average_score': round(avg_score, 2),
                'risk_distribution': risk_distribution,
                'most_common_vulnerabilities': most_common_vulns[:5]
            },
            'site_rankings': comparison,
            'recommendations': self._generate_recommendations(site_metrics)
        }
    
    def _generate_recommendations(self, site_metrics: List[SecurityMetrics]) -> List[str]:
        """Generate actionable security recommendations"""
        recommendations = []
        
        # Check for common issues across sites
        missing_headers = set()
        for metrics in site_metrics:
            for header in ['strict-transport-security', 'content-security-policy', 
                          'x-frame-options']:
                if header not in metrics.security_headers:
                    missing_headers.add(header)
        
        if missing_headers:
            recommendations.append(
                f"🔒 Implement missing security headers across sites: {', '.join(missing_headers)}"
            )
        
        # Check for authentication issues
        auth_issues = [m for m in site_metrics if m.authentication_score < 60]
        if auth_issues:
            recommendations.append(
                f"🔐 Review authentication mechanisms for {len(auth_issues)} sites with low auth scores"
            )
        
        # Check for data protection issues
        data_issues = [m for m in site_metrics if m.data_protection_score < 60]
        if data_issues:
            recommendations.append(
                f"🛡️ Review data protection practices for {len(data_issues)} sites with low data protection scores"
            )
        
        # Overall recommendations
        if any(m.overall_score < 40 for m in site_metrics):
            recommendations.append("🚨 Conduct immediate security audits for sites with critical vulnerabilities")
        
        if any(m.overall_score < 60 for m in site_metrics):
            recommendations.append("⚠️ Implement security improvement plans for sites with poor security posture")
        
        return recommendations 