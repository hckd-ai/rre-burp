"""
Threat Modeling and Risk Assessment

Advanced threat modeling capabilities for web application security analysis.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum

from .security_metrics import SecurityLevel, VulnerabilityCategory


class ThreatLevel(Enum):
    """Threat level classifications"""
    NEGLIGIBLE = "negligible"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AttackVector(Enum):
    """Attack vector classifications"""
    NETWORK = "network"
    ADJACENT_NETWORK = "adjacent_network"
    LOCAL = "local"
    PHYSICAL = "physical"


@dataclass
class Threat:
    """Individual threat definition"""
    id: str
    name: str
    description: str
    category: VulnerabilityCategory
    threat_level: ThreatLevel
    attack_vector: AttackVector
    likelihood: float  # 0.0 to 1.0
    impact: float     # 0.0 to 1.0
    risk_score: float = 0.0
    mitigations: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        # Calculate risk score based on likelihood and impact
        self.risk_score = round(self.likelihood * self.impact, 2)


@dataclass
class ThreatModel:
    """Comprehensive threat model for a web application"""
    
    application_name: str
    application_url: str
    threats: List[Threat] = field(default_factory=list)
    risk_assessment: Dict[str, Any] = field(default_factory=dict)
    
    def add_threat(self, threat: Threat) -> None:
        """Add a threat to the model"""
        self.threats.append(threat)
    
    def get_high_risk_threats(self) -> List[Threat]:
        """Get threats with high or critical risk levels"""
        return [t for t in self.threats if t.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
    
    def get_threats_by_category(self, category: VulnerabilityCategory) -> List[Threat]:
        """Get threats by vulnerability category"""
        return [t for t in self.threats if t.category == category]
    
    def calculate_overall_risk(self) -> ThreatLevel:
        """Calculate overall risk level based on all threats"""
        if not self.threats:
            return ThreatLevel.NEGLIGIBLE
        
        # Calculate weighted risk score
        total_risk = sum(t.risk_score for t in self.threats)
        avg_risk = total_risk / len(self.threats)
        
        if avg_risk >= 0.8:
            return ThreatLevel.CRITICAL
        elif avg_risk >= 0.6:
            return ThreatLevel.HIGH
        elif avg_risk >= 0.4:
            return ThreatLevel.MEDIUM
        elif avg_risk >= 0.2:
            return ThreatLevel.LOW
        else:
            return ThreatLevel.NEGLIGIBLE
    
    def generate_risk_report(self) -> Dict[str, Any]:
        """Generate comprehensive risk assessment report"""
        
        # Group threats by level
        threats_by_level = {}
        for level in ThreatLevel:
            threats_by_level[level.value] = [t for t in self.threats if t.threat_level == level]
        
        # Calculate statistics
        total_threats = len(self.threats)
        high_risk_count = len(self.get_high_risk_threats())
        
        # Calculate average risk scores by category
        category_risks = {}
        for category in VulnerabilityCategory:
            cat_threats = self.get_threats_by_category(category)
            if cat_threats:
                avg_risk = sum(t.risk_score for t in cat_threats) / len(cat_threats)
                category_risks[category.value] = round(avg_risk, 2)
        
        return {
            'application_info': {
                'name': self.application_name,
                'url': self.application_url
            },
            'overall_risk': self.calculate_overall_risk().value,
            'threat_statistics': {
                'total_threats': total_threats,
                'high_risk_threats': high_risk_count,
                'threats_by_level': {k: len(v) for k, v in threats_by_level.items()}
            },
            'category_risk_scores': category_risks,
            'threats_by_level': {
                level: [
                    {
                        'id': t.id,
                        'name': t.name,
                        'description': t.description,
                        'risk_score': t.risk_score,
                        'attack_vector': t.attack_vector.value,
                        'mitigations': t.mitigations
                    }
                    for t in threats
                ]
                for level, threats in threats_by_level.items()
            },
            'recommendations': self._generate_risk_recommendations()
        }
    
    def _generate_risk_recommendations(self) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []
        
        # High-risk threat recommendations
        high_risk_threats = self.get_high_risk_threats()
        if high_risk_threats:
            recommendations.append(
                f"🚨 IMMEDIATE: Address {len(high_risk_threats)} high-risk threats"
            )
        
        # Category-specific recommendations
        for category in VulnerabilityCategory:
            cat_threats = self.get_threats_by_category(category)
            if cat_threats:
                high_cat_threats = [t for t in cat_threats if t.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
                if high_cat_threats:
                    recommendations.append(
                        f"🛡️ {category.value.title()}: Mitigate {len(high_cat_threats)} high-risk {category.value} threats"
                    )
        
        # Attack vector recommendations
        network_threats = [t for t in self.threats if t.attack_vector == AttackVector.NETWORK]
        if network_threats:
            high_network_threats = [t for t in network_threats if t.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]]
            if high_network_threats:
                recommendations.append(
                    f"🌐 NETWORK: Implement network security controls for {len(high_network_threats)} high-risk network threats"
                )
        
        return recommendations


class ThreatModelBuilder:
    """Builder class for creating comprehensive threat models"""
    
    @staticmethod
    def create_web_application_threat_model() -> ThreatModel:
        """Create a standard web application threat model"""
        
        model = ThreatModel(
            application_name="Web Application",
            application_url="https://example.com"
        )
        
        # Authentication threats
        model.add_threat(Threat(
            id="AUTH-001",
            name="Weak Password Policy",
            description="Application allows weak passwords that can be easily guessed or brute-forced",
            category=VulnerabilityCategory.AUTHENTICATION,
            threat_level=ThreatLevel.HIGH,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.8,
            impact=0.7,
            mitigations=[
                "Implement strong password requirements",
                "Add rate limiting for login attempts",
                "Implement account lockout after failed attempts"
            ],
            examples=[
                "Password '123456' accepted",
                "No minimum length requirement",
                "No complexity requirements"
            ]
        ))
        
        model.add_threat(Threat(
            id="AUTH-002",
            name="Session Fixation",
            description="Session identifiers are predictable or can be manipulated by attackers",
            category=VulnerabilityCategory.SESSION_MANAGEMENT,
            threat_level=ThreatLevel.MEDIUM,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.6,
            impact=0.6,
            mitigations=[
                "Generate new session IDs after login",
                "Use cryptographically secure random session IDs",
                "Implement proper session invalidation"
            ],
            examples=[
                "Session ID in URL parameters",
                "Predictable session ID generation",
                "Session ID not changed after authentication"
            ]
        ))
        
        # Injection threats
        model.add_threat(Threat(
            id="INJ-001",
            name="SQL Injection",
            description="User input is directly concatenated into SQL queries, allowing database manipulation",
            category=VulnerabilityCategory.INJECTION,
            threat_level=ThreatLevel.CRITICAL,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.7,
            impact=0.9,
            mitigations=[
                "Use parameterized queries",
                "Implement input validation",
                "Apply principle of least privilege to database users"
            ],
            examples=[
                "User input directly in SQL query",
                "No input sanitization",
                "Error messages revealing database structure"
            ]
        ))
        
        model.add_threat(Threat(
            id="INJ-002",
            name="Cross-Site Scripting (XSS)",
            description="User input is rendered as HTML/JavaScript, allowing script execution in user browsers",
            category=VulnerabilityCategory.INJECTION,
            threat_level=ThreatLevel.HIGH,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.8,
            impact=0.7,
            mitigations=[
                "Implement proper output encoding",
                "Use Content Security Policy (CSP)",
                "Validate and sanitize all user input"
            ],
            examples=[
                "User input rendered without encoding",
                "No CSP headers",
                "Reflected XSS in search results"
            ]
        ))
        
        # Data exposure threats
        model.add_threat(Threat(
            id="DATA-001",
            name="Sensitive Data in URLs",
            description="Sensitive information like tokens, keys, or personal data exposed in URL parameters",
            category=VulnerabilityCategory.DATA_EXPOSURE,
            threat_level=ThreatLevel.HIGH,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.9,
            impact=0.6,
            mitigations=[
                "Use POST requests for sensitive data",
                "Implement secure token storage",
                "Use secure headers for sensitive information"
            ],
            examples=[
                "API key in URL parameters",
                "User ID in query string",
                "Authentication token in URL"
            ]
        ))
        
        # Configuration threats
        model.add_threat(Threat(
            id="CONFIG-001",
            name="Missing Security Headers",
            description="Important security headers are not implemented, reducing application security",
            category=VulnerabilityCategory.CONFIGURATION,
            threat_level=ThreatLevel.MEDIUM,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.9,
            impact=0.4,
            mitigations=[
                "Implement HSTS header",
                "Add Content Security Policy",
                "Set X-Frame-Options header",
                "Configure X-Content-Type-Options"
            ],
            examples=[
                "No HSTS header",
                "Missing CSP header",
                "No X-Frame-Options protection"
            ]
        ))
        
        # API security threats
        model.add_threat(Threat(
            id="API-001",
            name="Missing Rate Limiting",
            description="API endpoints lack rate limiting, making them vulnerable to abuse and attacks",
            category=VulnerabilityCategory.API_SECURITY,
            threat_level=ThreatLevel.MEDIUM,
            attack_vector=AttackVector.NETWORK,
            likelihood=0.8,
            impact=0.5,
            mitigations=[
                "Implement rate limiting per IP/user",
                "Add request throttling",
                "Monitor for unusual traffic patterns"
            ],
            examples=[
                "Login endpoint without rate limiting",
                "No protection against brute force",
                "Unlimited API requests allowed"
            ]
        ))
        
        return model
    
    @staticmethod
    def create_custom_threat_model(application_name: str, application_url: str,
                                 custom_threats: List[Threat] = None) -> ThreatModel:
        """Create a custom threat model with specific threats"""
        
        model = ThreatModel(
            application_name=application_name,
            application_url=application_url
        )
        
        # Add custom threats if provided
        if custom_threats:
            for threat in custom_threats:
                model.add_threat(threat)
        
        return model 