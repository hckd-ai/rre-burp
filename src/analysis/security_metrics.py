"""
Security Metrics and Scoring Models

Defines the structure for security assessment data and scoring calculations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import json


class SecurityLevel(Enum):
    """Security level classifications"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    SECURE = "secure"


class VulnerabilityCategory(Enum):
    """Categories of security vulnerabilities"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_EXPOSURE = "data_exposure"
    INJECTION = "injection"
    CONFIGURATION = "configuration"
    CRYPTOGRAPHY = "cryptography"
    SESSION_MANAGEMENT = "session_management"
    INPUT_VALIDATION = "input_validation"
    ERROR_HANDLING = "error_handling"
    LOGGING = "logging"
    NETWORK = "network"
    API_SECURITY = "api_security"


@dataclass
class VulnerabilityFinding:
    """Individual vulnerability finding"""
    category: VulnerabilityCategory
    severity: SecurityLevel
    title: str
    description: str
    evidence: str
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None
    remediation: Optional[str] = None
    confidence: float = 0.8  # 0.0 to 1.0


@dataclass
class SecurityMetrics:
    """Comprehensive security metrics for a website"""
    
    # Overall scores (0-100, higher is more secure)
    overall_score: float = 0.0
    authentication_score: float = 0.0
    authorization_score: float = 0.0
    data_protection_score: float = 0.0
    api_security_score: float = 0.0
    configuration_score: float = 0.0
    
    # Risk levels
    overall_risk: SecurityLevel = SecurityLevel.MEDIUM
    highest_risk: SecurityLevel = SecurityLevel.MEDIUM
    
    # Vulnerability counts
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    
    # Detailed findings
    vulnerabilities: List[VulnerabilityFinding] = field(default_factory=list)
    
    # Security headers analysis
    security_headers: Dict[str, Any] = field(default_factory=dict)
    
    # API endpoint analysis
    api_endpoints: Dict[str, Any] = field(default_factory=dict)
    
    # Data exposure analysis
    sensitive_data_exposure: List[str] = field(default_factory=list)
    
    # Authentication analysis
    auth_mechanisms: List[str] = field(default_factory=list)
    session_management: Dict[str, Any] = field(default_factory=dict)
    
    # Network security
    tls_analysis: Dict[str, Any] = field(default_factory=dict)
    network_exposure: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'overall_score': self.overall_score,
            'overall_risk': self.overall_risk.value,
            'highest_risk': self.highest_risk.value,
            'scores': {
                'authentication': self.authentication_score,
                'authorization': self.authorization_score,
                'data_protection': self.data_protection_score,
                'api_security': self.api_security_score,
                'configuration': self.configuration_score
            },
            'vulnerability_counts': {
                'critical': self.critical_count,
                'high': self.high_count,
                'medium': self.medium_count,
                'low': self.low_count
            },
            'vulnerabilities': [
                {
                    'category': v.category.value,
                    'severity': v.severity.value,
                    'title': v.title,
                    'description': v.description,
                    'evidence': v.evidence,
                    'cwe_id': v.cwe_id,
                    'cvss_score': v.cvss_score,
                    'remediation': v.remediation,
                    'confidence': v.confidence
                }
                for v in self.vulnerabilities
            ],
            'security_headers': self.security_headers,
            'api_endpoints': self.api_endpoints,
            'sensitive_data_exposure': self.sensitive_data_exposure,
            'auth_mechanisms': self.auth_mechanisms,
            'session_management': self.session_management,
            'tls_analysis': self.tls_analysis,
            'network_exposure': self.network_exposure
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def get_risk_summary(self) -> str:
        """Get a human-readable risk summary"""
        if self.overall_score >= 90:
            return "🟢 SECURE - Excellent security posture"
        elif self.overall_score >= 75:
            return "🟡 GOOD - Good security with minor issues"
        elif self.overall_score >= 60:
            return "🟠 MODERATE - Moderate security concerns"
        elif self.overall_score >= 40:
            return "🔴 POOR - Significant security issues"
        else:
            return "⚫ CRITICAL - Critical security vulnerabilities"
    
    def get_priority_actions(self) -> List[str]:
        """Get prioritized list of actions to improve security"""
        actions = []
        
        if self.critical_count > 0:
            actions.append(f"🔴 IMMEDIATE: Fix {self.critical_count} critical vulnerabilities")
        
        if self.high_count > 0:
            actions.append(f"🟠 HIGH: Address {self.high_count} high-risk issues")
        
        if self.medium_count > 0:
            actions.append(f"🟡 MEDIUM: Review {self.medium_count} medium-risk findings")
        
        if self.overall_score < 60:
            actions.append("📋 COMPREHENSIVE: Conduct full security audit")
        
        if not self.security_headers.get('strict-transport-security'):
            actions.append("🔒 SECURITY: Implement HSTS header")
        
        if not self.security_headers.get('content-security-policy'):
            actions.append("🛡️ SECURITY: Implement CSP header")
        
        return actions 