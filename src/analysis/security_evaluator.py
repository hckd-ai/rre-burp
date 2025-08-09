"""
Security Evaluation Engine

Orchestrates the complete security evaluation process:
1. HAR data analysis
2. Vulnerability detection
3. Security scoring
4. Report generation
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass

from .security_metrics import SecurityMetrics
from .vulnerability_detector import VulnerabilityDetector
from .security_scorer import SecurityScorer, ScoringWeights


@dataclass
class EvaluationConfig:
    """Configuration for security evaluation"""
    custom_weights: Optional[ScoringWeights] = None
    include_rre_analysis: bool = True
    detailed_reporting: bool = True
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['json', 'html']


class SecurityEvaluator:
    """Main security evaluation engine"""
    
    def __init__(self, config: EvaluationConfig = None):
        self.config = config or EvaluationConfig()
        self.vulnerability_detector = VulnerabilityDetector()
        self.security_scorer = SecurityScorer(self.config.custom_weights)
        self.logger = logging.getLogger(__name__)
        
    def evaluate_single_site(self, har_file_path: Union[str, Path], 
                           site_name: str = None, site_url: str = None,
                           rre_analysis: Dict[str, Any] = None) -> SecurityMetrics:
        """Evaluate security for a single site"""
        
        self.logger.info(f"Starting security evaluation for: {site_name or har_file_path}")
        
        # Load HAR data
        har_data = self._load_har_data(har_file_path)
        if not har_data:
            raise ValueError(f"Failed to load HAR data from: {har_file_path}")
        
        # Create security metrics
        metrics = SecurityMetrics()
        
        # Add site information
        if site_name:
            metrics.site_name = site_name
        if site_url:
            metrics.site_url = site_url
        
        # Analyze HAR data for vulnerabilities
        self.logger.info("Analyzing HAR data for vulnerabilities...")
        vulnerabilities = self.vulnerability_detector.analyze_har_data(har_data)
        metrics.vulnerabilities = vulnerabilities
        
        # Analyze security headers
        self.logger.info("Analyzing security headers...")
        security_headers = self._analyze_security_headers(har_data)
        metrics.security_headers = security_headers
        
        # Analyze API endpoints
        self.logger.info("Analyzing API endpoints...")
        api_endpoints = self._analyze_api_endpoints(har_data)
        metrics.api_endpoints = api_endpoints
        
        # Analyze authentication mechanisms
        self.logger.info("Analyzing authentication mechanisms...")
        auth_mechanisms = self._analyze_authentication(har_data)
        metrics.auth_mechanisms = auth_mechanisms
        
        # Analyze session management
        self.logger.info("Analyzing session management...")
        session_management = self._analyze_session_management(har_data)
        metrics.session_management = session_management
        
        # Analyze TLS/network security
        self.logger.info("Analyzing TLS and network security...")
        tls_analysis = self._analyze_tls_security(har_data)
        metrics.tls_analysis = tls_analysis
        
        # Analyze network exposure
        self.logger.info("Analyzing network exposure...")
        network_exposure = self._analyze_network_exposure(har_data)
        metrics.network_exposure = network_exposure
        
        # Analyze RRE data if provided
        if self.config.include_rre_analysis and rre_analysis:
            self.logger.info("Analyzing RRE data...")
            rre_vulnerabilities = self.vulnerability_detector.analyze_rre_data(rre_analysis)
            metrics.vulnerabilities.extend(rre_vulnerabilities)
        
        # Calculate security scores
        self.logger.info("Calculating security scores...")
        scored_metrics = self.security_scorer.calculate_security_score(metrics)
        
        self.logger.info(f"Security evaluation completed. Overall score: {scored_metrics.overall_score}")
        
        return scored_metrics
    
    def evaluate_multiple_sites(self, site_data: List[Dict[str, Any]]) -> List[SecurityMetrics]:
        """Evaluate security for multiple sites"""
        
        self.logger.info(f"Starting security evaluation for {len(site_data)} sites")
        
        results = []
        
        for site_info in site_data:
            try:
                har_file = site_info.get('har_file')
                site_name = site_info.get('name', 'Unknown Site')
                site_url = site_info.get('url', 'Unknown URL')
                rre_analysis = site_info.get('rre_analysis')
                
                if not har_file or not Path(har_file).exists():
                    self.logger.warning(f"HAR file not found for {site_name}: {har_file}")
                    continue
                
                metrics = self.evaluate_single_site(
                    har_file, site_name, site_url, rre_analysis
                )
                results.append(metrics)
                
            except Exception as e:
                self.logger.error(f"Failed to evaluate {site_info.get('name', 'Unknown')}: {e}")
                continue
        
        self.logger.info(f"Completed evaluation for {len(results)} sites")
        return results
    
    def generate_comparison_report(self, site_metrics: List[SecurityMetrics]) -> Dict[str, Any]:
        """Generate comprehensive comparison report for multiple sites"""
        
        self.logger.info("Generating comparison report...")
        
        report = self.security_scorer.generate_security_report(site_metrics)
        
        # Add additional analysis
        report['detailed_analysis'] = self._generate_detailed_analysis(site_metrics)
        
        return report
    
    def export_report(self, report: Dict[str, Any], output_dir: Union[str, Path],
                     filename: str = "security_evaluation_report") -> List[Path]:
        """Export security report in multiple formats"""
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        exported_files = []
        
        # Export JSON
        if 'json' in self.config.export_formats:
            json_file = output_dir / f"{filename}.json"
            with open(json_file, 'w') as f:
                json.dump(report, f, indent=2)
            exported_files.append(json_file)
            self.logger.info(f"Exported JSON report: {json_file}")
        
        # Export HTML
        if 'html' in self.config.export_formats:
            html_file = output_dir / f"{filename}.html"
            html_content = self._generate_html_report(report)
            with open(html_file, 'w') as f:
                f.write(html_content)
            exported_files.append(html_file)
            self.logger.info(f"Exported HTML report: {html_file}")
        
        # Export CSV summary
        if 'csv' in self.config.export_formats:
            csv_file = output_dir / f"{filename}_summary.csv"
            csv_content = self._generate_csv_summary(report)
            with open(csv_file, 'w') as f:
                f.write(csv_content)
            exported_files.append(csv_file)
            self.logger.info(f"Exported CSV summary: {csv_file}")
        
        return exported_files
    
    def _load_har_data(self, har_file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load HAR data from file"""
        try:
            with open(har_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load HAR file {har_file_path}: {e}")
            return None
    
    def _analyze_security_headers(self, har_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze security headers from HAR data"""
        security_headers = {}
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return security_headers
        
        for entry in har_data['log']['entries']:
            response = entry.get('response', {})
            headers = response.get('headers', [])
            
            for header in headers:
                name = header.get('name', '').lower()
                value = header.get('value', '')
                
                # Focus on security-related headers
                if any(security_term in name for security_term in 
                       ['security', 'x-frame', 'x-content', 'x-xss', 'csp', 'hsts']):
                    security_headers[name] = value
        
        return security_headers
    
    def _analyze_api_endpoints(self, har_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze API endpoints from HAR data"""
        api_endpoints = {
            'count': 0,
            'endpoints': [],
            'methods': {},
            'status_codes': {},
            'authentication_required': 0,
            'public_endpoints': 0
        }
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return api_endpoints
        
        for entry in har_data['log']['entries']:
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            url = request.get('url', '')
            method = request.get('method', 'GET')
            status = response.get('status', 0)
            
            # Check if this looks like an API endpoint
            if any(api_indicator in url.lower() for api_indicator in 
                   ['/api/', '/rest/', '/v1/', '/v2/', '/graphql']):
                
                api_endpoints['count'] += 1
                api_endpoints['endpoints'].append({
                    'url': url,
                    'method': method,
                    'status': status
                })
                
                # Count methods
                api_endpoints['methods'][method] = api_endpoints['methods'].get(method, 0) + 1
                
                # Count status codes
                api_endpoints['status_codes'][status] = api_endpoints['status_codes'].get(status, 0) + 1
                
                # Check if authentication might be required
                headers = request.get('headers', [])
                has_auth = any('authorization' in h.get('name', '').lower() for h in headers)
                
                if has_auth:
                    api_endpoints['authentication_required'] += 1
                else:
                    api_endpoints['public_endpoints'] += 1
        
        return api_endpoints
    
    def _analyze_authentication(self, har_data: Dict[str, Any]) -> List[str]:
        """Analyze authentication mechanisms from HAR data"""
        auth_mechanisms = []
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return auth_mechanisms
        
        for entry in har_data['log']['entries']:
            request = entry.get('request', {})
            response = entry.get('response', {})
            
            # Check for authentication-related endpoints
            url = request.get('url', '').lower()
            if any(auth_term in url for auth_term in 
                   ['login', 'auth', 'signin', 'register', 'signup', 'logout']):
                
                method = request.get('method', 'GET')
                if method == 'POST':
                    auth_mechanisms.append(f"Form-based authentication: {url}")
                elif method == 'GET':
                    auth_mechanisms.append(f"Token-based authentication: {url}")
            
            # Check for OAuth flows
            if 'oauth' in url or 'callback' in url:
                auth_mechanisms.append(f"OAuth flow: {url}")
            
            # Check for JWT tokens
            headers = request.get('headers', [])
            for header in headers:
                if 'authorization' in header.get('name', '').lower():
                    value = header.get('value', '')
                    if value.startswith('Bearer '):
                        auth_mechanisms.append("JWT Bearer token authentication")
                    elif value.startswith('Basic '):
                        auth_mechanisms.append("Basic authentication")
        
        return list(set(auth_mechanisms))  # Remove duplicates
    
    def _analyze_session_management(self, har_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze session management from HAR data"""
        session_info = {
            'session_cookies': [],
            'session_parameters': [],
            'session_timeout': None,
            'secure_cookies': 0,
            'http_only_cookies': 0
        }
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return session_info
        
        for entry in har_data['log']['entries']:
            response = entry.get('response', {})
            headers = response.get('headers', [])
            
            # Look for Set-Cookie headers
            for header in headers:
                if header.get('name', '').lower() == 'set-cookie':
                    cookie_value = header.get('value', '')
                    
                    # Parse cookie attributes
                    if 'session' in cookie_value.lower() or 'sid' in cookie_value.lower():
                        session_info['session_cookies'].append(cookie_value)
                        
                        # Check security attributes
                        if 'secure' in cookie_value.lower():
                            session_info['secure_cookies'] += 1
                        if 'httponly' in cookie_value.lower():
                            session_info['http_only_cookies'] += 1
        
        return session_info
    
    def _analyze_tls_security(self, har_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze TLS/SSL security from HAR data"""
        tls_info = {
            'https_usage': 0,
            'http_usage': 0,
            'tls_versions': [],
            'weak_ciphers': 0
        }
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return tls_info
        
        for entry in har_data['log']['entries']:
            request = entry.get('request', {})
            url = request.get('url', '')
            
            if url.startswith('https://'):
                tls_info['https_usage'] += 1
            elif url.startswith('http://'):
                tls_info['http_usage'] += 1
        
        return tls_info
    
    def _analyze_network_exposure(self, har_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze network exposure from HAR data"""
        network_info = {
            'external_domains': set(),
            'internal_endpoints': 0,
            'cdn_usage': 0,
            'third_party_services': 0
        }
        
        if 'log' not in har_data or 'entries' not in har_data['log']:
            return {k: v if not isinstance(v, set) else list(v) for k, v in network_info.items()}
        
        for entry in har_data['log']['entries']:
            request = entry.get('request', {})
            url = request.get('url', '')
            
            try:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                domain = parsed.netloc
                
                if domain:
                    network_info['external_domains'].add(domain)
                    
                    # Check for CDN usage
                    if any(cdn in domain for cdn in ['cdn', 'cloudfront', 'fastly', 'akamai']):
                        network_info['cdn_usage'] += 1
                    
                    # Check for third-party services
                    if any(service in domain for service in ['googleapis', 'facebook', 'twitter', 'analytics']):
                        network_info['third_party_services'] += 1
                        
            except Exception:
                continue
        
        # Convert set to list for JSON serialization
        network_info['external_domains'] = list(network_info['external_domains'])
        
        return network_info
    
    def _generate_detailed_analysis(self, site_metrics: List[SecurityMetrics]) -> Dict[str, Any]:
        """Generate detailed analysis of security findings"""
        
        analysis = {
            'vulnerability_trends': {},
            'security_header_compliance': {},
            'common_weaknesses': [],
            'best_practices': []
        }
        
        # Analyze vulnerability trends
        all_vulns = []
        for metrics in site_metrics:
            all_vulns.extend(metrics.vulnerabilities)
        
        vuln_categories = {}
        for vuln in all_vulns:
            cat = vuln.category.value
            vuln_categories[cat] = vuln_categories.get(cat, 0) + 1
        
        analysis['vulnerability_trends'] = vuln_categories
        
        # Analyze security header compliance
        header_compliance = {}
        for metrics in site_metrics:
            for header in ['strict-transport-security', 'content-security-policy', 
                          'x-frame-options', 'x-content-type-options']:
                if header not in header_compliance:
                    header_compliance[header] = {'present': 0, 'missing': 0}
                
                if header in metrics.security_headers:
                    header_compliance[header]['present'] += 1
                else:
                    header_compliance[header]['missing'] += 1
        
        analysis['security_header_compliance'] = header_compliance
        
        # Identify common weaknesses
        if any(m.overall_score < 60 for m in site_metrics):
            analysis['common_weaknesses'].append("Low overall security scores across multiple sites")
        
        if any(m.critical_count > 0 for m in site_metrics):
            analysis['common_weaknesses'].append("Critical vulnerabilities present in multiple sites")
        
        # Identify best practices
        secure_sites = [m for m in site_metrics if m.overall_score >= 75]
        if secure_sites:
            analysis['best_practices'].append(f"{len(secure_sites)} sites demonstrate good security practices")
        
        return analysis
    
    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """Generate HTML report"""
        # This is a simplified HTML report - could be enhanced with CSS styling
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Security Evaluation Report</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .score {{ font-size: 24px; font-weight: bold; }}
                .critical {{ color: #d32f2f; }}
                .high {{ color: #f57c00; }}
                .medium {{ color: #fbc02d; }}
                .low {{ color: #388e3c; }}
                .secure {{ color: #1976d2; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ Security Evaluation Report</h1>
                <p>Generated on: {report.get('summary', {}).get('total_sites', 0)} sites analyzed</p>
            </div>
            
            <div class="section">
                <h2>📊 Summary</h2>
                <p>Total sites: {report.get('summary', {}).get('total_sites', 0)}</p>
                <p>Average score: {report.get('summary', {}).get('average_score', 0)}</p>
            </div>
            
            <div class="section">
                <h2>🏆 Site Rankings</h2>
                <table>
                    <tr>
                        <th>Rank</th>
                        <th>Site</th>
                        <th>Score</th>
                        <th>Risk Level</th>
                        <th>Vulnerabilities</th>
                    </tr>
        """
        
        for site in report.get('site_rankings', []):
            risk_class = site.get('overall_risk', 'medium')
            html += f"""
                    <tr>
                        <td>{site.get('rank', 'N/A')}</td>
                        <td>{site.get('site_name', 'Unknown')}</td>
                        <td class="score {risk_class}">{site.get('overall_score', 0)}</td>
                        <td>{site.get('overall_risk', 'N/A')}</td>
                        <td>C:{site.get('vulnerability_summary', {}).get('critical', 0)} H:{site.get('vulnerability_summary', {}).get('high', 0)} M:{site.get('vulnerability_summary', {}).get('medium', 0)}</td>
                    </tr>
            """
        
        html += """
                </table>
            </div>
            
            <div class="section">
                <h2>💡 Recommendations</h2>
                <ul>
        """
        
        for rec in report.get('recommendations', []):
            html += f"<li>{rec}</li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _generate_csv_summary(self, report: Dict[str, Any]) -> str:
        """Generate CSV summary report"""
        csv_lines = [
            "Rank,Site Name,Site URL,Overall Score,Risk Level,Critical,High,Medium,Low"
        ]
        
        for site in report.get('site_rankings', []):
            vuln_summary = site.get('vulnerability_summary', {})
            csv_lines.append(
                f"{site.get('rank', 'N/A')},"
                f"{site.get('site_name', 'Unknown')},"
                f"{site.get('site_url', 'Unknown')},"
                f"{site.get('overall_score', 0)},"
                f"{site.get('overall_risk', 'N/A')},"
                f"{vuln_summary.get('critical', 0)},"
                f"{vuln_summary.get('high', 0)},"
                f"{vuln_summary.get('medium', 0)},"
                f"{vuln_summary.get('low', 0)}"
            )
        
        return "\n".join(csv_lines) 