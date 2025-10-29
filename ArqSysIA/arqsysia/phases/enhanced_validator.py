"""
Enhanced Validator Phase - Validation with historical trend analysis.

This module provides an enhanced validator that compares against previous
iterations, detects regressions, and analyzes trends in quality metrics.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from ..core.state import ProjectState, Iteration
from ..core.version_manager import VersionManager
from ..core.diff_engine import DiffEngine


class EnhancedValidator:
    """
    Validator with historical comparison and trend analysis.
    
    Compares current iteration against previous ones to detect
    regressions and analyze quality trends.
    """
    
    def __init__(
        self,
        version_manager: VersionManager,
        diff_engine: DiffEngine
    ):
        """
        Initialize EnhancedValidator.
        
        Args:
            version_manager: For loading previous iterations
            diff_engine: For comparing iterations
        """
        self.version_manager = version_manager
        self.diff_engine = diff_engine
    
    def validate(
        self,
        codegen_result: Dict[str, Any],
        analysis_result: Dict[str, Any],
        project_name: str,
        current_iteration: int
    ) -> Dict[str, Any]:
        """
        Validate with comparison to previous iterations.
        
        Args:
            codegen_result: Results from code generation phase
            analysis_result: Results from analyzer phase
            project_name: Project identifier
            current_iteration: Current iteration number
            
        Returns:
            Dictionary with validation results including trends
        """
        result = {
            'iteration': current_iteration,
            'timestamp': datetime.now().isoformat(),
            'has_comparison': current_iteration > 1,
            'trend_analysis': None,
            'regression_detection': None,
            'recommendations': [],
            'validation': None  # Would be populated by LLM
        }
        
        # If first iteration, no comparison possible
        if current_iteration == 1:
            result['trend_analysis'] = "First iteration - no historical data"
            return result
        
        # Build validation context with trends
        validation_context = self._build_validation_context(
            project_name,
            current_iteration,
            codegen_result,
            analysis_result
        )
        
        result['trend_analysis'] = validation_context['trends']
        result['regression_detection'] = validation_context['regressions']
        result['recommendations'] = validation_context['recommendations']
        result['comparison_summary'] = validation_context['comparison_summary']
        
        # In real implementation, this would call an LLM
        result['validation'] = {
            'status': 'context_ready',
            'message': 'Validation context with trends successfully built',
            'requires_attention': len(validation_context['regressions']) > 0
        }
        
        return result
    
    def _build_validation_context(
        self,
        project_name: str,
        current_iteration: int,
        codegen_result: Dict[str, Any],
        analysis_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build validation context with historical comparison.
        
        Args:
            project_name: Project identifier
            current_iteration: Current iteration number
            codegen_result: Current code generation results
            analysis_result: Current analysis results
            
        Returns:
            Dictionary with validation context
        """
        context = {
            'trends': {},
            'regressions': [],
            'recommendations': [],
            'comparison_summary': ''
        }
        
        # 1. Load previous iteration for comparison
        try:
            prev_iteration = self.version_manager.get_iteration(current_iteration - 1)
        except FileNotFoundError:
            context['comparison_summary'] = "No previous iteration for comparison"
            return context
        
        # 2. Analyze score trends (if we have scores)
        # Note: In real implementation, scores would come from actual validation
        # For now, we'll use mock scores or previous scores
        prev_scores = prev_iteration.final_scores
        
        # Mock current scores for demonstration
        # In real implementation, these would come from actual validation
        current_scores = {
            'architecture': prev_scores.get('architecture', 7),
            'code': prev_scores.get('code', 6),
            'security': prev_scores.get('security', 5)
        }
        
        context['trends'] = self._analyze_score_trends(prev_scores, current_scores)
        
        # 3. Detect regressions
        context['regressions'] = self._detect_regressions(prev_scores, current_scores)
        
        # 4. Load more historical data if available
        historical_scores = self._load_historical_scores(project_name, current_iteration)
        if len(historical_scores) >= 2:
            context['trends']['overall_trend'] = self._calculate_overall_trend(historical_scores)
        
        # 5. Generate recommendations based on trends
        context['recommendations'] = self._generate_recommendations(
            context['trends'],
            context['regressions'],
            prev_iteration
        )
        
        # 6. Build comparison summary
        summary_parts = [
            f"Validation comparison for iteration {current_iteration}:",
            f"- Previous iteration: {prev_iteration.iteration_number}",
            f"- Previous scores: {prev_scores}",
            f"- Current scores: {current_scores}",
            f"- Regressions detected: {len(context['regressions'])}"
        ]
        
        if context['trends'].get('overall_trend'):
            summary_parts.append(f"- Overall trend: {context['trends']['overall_trend']}")
        
        context['comparison_summary'] = '\n'.join(summary_parts)
        
        return context
    
    def _analyze_score_trends(
        self,
        prev_scores: Dict[str, int],
        current_scores: Dict[str, int]
    ) -> Dict[str, Any]:
        """
        Analyze trends between previous and current scores.
        
        Args:
            prev_scores: Scores from previous iteration
            current_scores: Scores from current iteration
            
        Returns:
            Dictionary with trend analysis
        """
        trends = {
            'improvements': {},
            'regressions': {},
            'stable': {},
            'summary': ''
        }
        
        all_metrics = set(prev_scores.keys()) | set(current_scores.keys())
        
        for metric in all_metrics:
            prev_score = prev_scores.get(metric, 0)
            curr_score = current_scores.get(metric, 0)
            delta = curr_score - prev_score
            
            if delta > 0:
                trends['improvements'][metric] = {
                    'previous': prev_score,
                    'current': curr_score,
                    'delta': delta
                }
            elif delta < 0:
                trends['regressions'][metric] = {
                    'previous': prev_score,
                    'current': curr_score,
                    'delta': delta
                }
            else:
                trends['stable'][metric] = {
                    'score': curr_score
                }
        
        # Build summary
        improvements_count = len(trends['improvements'])
        regressions_count = len(trends['regressions'])
        stable_count = len(trends['stable'])
        
        if improvements_count > regressions_count:
            trends['summary'] = f"Overall improving: {improvements_count} metrics up, {regressions_count} down"
        elif regressions_count > improvements_count:
            trends['summary'] = f"Overall declining: {regressions_count} metrics down, {improvements_count} up"
        else:
            trends['summary'] = f"Mixed results: {improvements_count} up, {regressions_count} down, {stable_count} stable"
        
        return trends
    
    def _detect_regressions(
        self,
        prev_scores: Dict[str, int],
        current_scores: Dict[str, int]
    ) -> List[Dict[str, Any]]:
        """
        Detect significant regressions in scores.
        
        Args:
            prev_scores: Previous iteration scores
            current_scores: Current iteration scores
            
        Returns:
            List of detected regressions
        """
        regressions = []
        
        for metric, prev_score in prev_scores.items():
            curr_score = current_scores.get(metric, 0)
            delta = curr_score - prev_score
            
            # Consider it a regression if score dropped by 2 or more points
            if delta <= -2:
                regressions.append({
                    'metric': metric,
                    'previous_score': prev_score,
                    'current_score': curr_score,
                    'delta': delta,
                    'severity': 'high' if delta <= -3 else 'medium'
                })
        
        return regressions
    
    def _load_historical_scores(
        self,
        project_name: str,
        current_iteration: int
    ) -> List[Dict[str, int]]:
        """
        Load scores from all previous iterations.
        
        Args:
            project_name: Project identifier
            current_iteration: Current iteration number
            
        Returns:
            List of score dictionaries, ordered by iteration
        """
        historical_scores = []
        
        for i in range(1, current_iteration):
            try:
                iteration = self.version_manager.get_iteration(i)
                historical_scores.append({
                    'iteration': i,
                    'scores': iteration.final_scores
                })
            except FileNotFoundError:
                continue
        
        return historical_scores
    
    def _calculate_overall_trend(
        self,
        historical_scores: List[Dict[str, Any]]
    ) -> str:
        """
        Calculate overall trend across multiple iterations.
        
        Args:
            historical_scores: List of historical score dictionaries
            
        Returns:
            String describing the overall trend
        """
        if len(historical_scores) < 2:
            return "insufficient_data"
        
        # Calculate average score for each iteration
        avg_scores = []
        for entry in historical_scores:
            scores = entry['scores']
            if scores:
                avg = sum(scores.values()) / len(scores)
                avg_scores.append(avg)
        
        if len(avg_scores) < 2:
            return "insufficient_data"
        
        # Simple trend: compare first half vs second half
        mid = len(avg_scores) // 2
        first_half_avg = sum(avg_scores[:mid]) / mid
        second_half_avg = sum(avg_scores[mid:]) / (len(avg_scores) - mid)
        
        difference = second_half_avg - first_half_avg
        
        if difference > 0.5:
            return "improving"
        elif difference < -0.5:
            return "declining"
        else:
            return "stable"
    
    def _generate_recommendations(
        self,
        trends: Dict[str, Any],
        regressions: List[Dict[str, Any]],
        prev_iteration: Iteration
    ) -> List[str]:
        """
        Generate recommendations based on trends and regressions.
        
        Args:
            trends: Trend analysis results
            regressions: Detected regressions
            prev_iteration: Previous iteration data
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Recommendations for regressions
        if regressions:
            high_severity = [r for r in regressions if r['severity'] == 'high']
            if high_severity:
                recommendations.append(
                    f"URGENT: {len(high_severity)} high-severity regressions detected. "
                    "Consider reverting changes or addressing issues before proceeding."
                )
            else:
                recommendations.append(
                    f"{len(regressions)} regressions detected. Review changes carefully."
                )
        
        # Recommendations based on overall trend
        overall_trend = trends.get('overall_trend')
        if overall_trend == 'declining':
            recommendations.append(
                "Overall quality trend is declining across iterations. "
                "Consider reviewing architectural decisions."
            )
        elif overall_trend == 'improving':
            recommendations.append(
                "Quality metrics are improving. Current approach is working well."
            )
        
        # Recommendations for specific metrics
        if trends.get('improvements'):
            best_improvement = max(
                trends['improvements'].items(),
                key=lambda x: x[1]['delta']
            )
            recommendations.append(
                f"Best improvement: {best_improvement[0]} "
                f"(+{best_improvement[1]['delta']} points)"
            )
        
        if not recommendations:
            recommendations.append("No significant issues detected. Continue with current approach.")
        
        return recommendations
    
    def build_prompt(
        self,
        codegen_result: Dict[str, Any],
        validation_context: Dict[str, Any]
    ) -> str:
        """
        Build enriched prompt with validation context.
        
        This method would be used when integrating with an actual LLM.
        
        Args:
            codegen_result: Results from code generation
            validation_context: Context from _build_validation_context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Header
        prompt_parts.append("# VALIDATION WITH HISTORICAL COMPARISON")
        prompt_parts.append("")
        
        # Trend analysis
        trends = validation_context.get('trends', {})
        if trends:
            prompt_parts.append("## SCORE TRENDS")
            prompt_parts.append(f"Summary: {trends.get('summary', 'N/A')}")
            
            if trends.get('improvements'):
                prompt_parts.append("\nImprovements:")
                for metric, data in trends['improvements'].items():
                    prompt_parts.append(
                        f"- {metric}: {data['previous']} → {data['current']} "
                        f"(+{data['delta']})"
                    )
            
            if trends.get('regressions'):
                prompt_parts.append("\nRegressions:")
                for metric, data in trends['regressions'].items():
                    prompt_parts.append(
                        f"- {metric}: {data['previous']} → {data['current']} "
                        f"({data['delta']})"
                    )
            
            prompt_parts.append("")
        
        # Regression detection
        regressions = validation_context.get('regressions', [])
        if regressions:
            prompt_parts.append("## DETECTED REGRESSIONS")
            for reg in regressions:
                prompt_parts.append(
                    f"- {reg['metric']} [{reg['severity']}]: "
                    f"{reg['previous_score']} → {reg['current_score']} "
                    f"(delta: {reg['delta']})"
                )
            prompt_parts.append("")
        
        # Recommendations
        recommendations = validation_context.get('recommendations', [])
        if recommendations:
            prompt_parts.append("## RECOMMENDATIONS")
            for i, rec in enumerate(recommendations, 1):
                prompt_parts.append(f"{i}. {rec}")
            prompt_parts.append("")
        
        # Instructions
        prompt_parts.append("## TASK")
        prompt_parts.append("Validate the current implementation considering:")
        prompt_parts.append("1. Architecture consistency and completeness")
        prompt_parts.append("2. Code quality and potential issues")
        prompt_parts.append("3. Security vulnerabilities")
        prompt_parts.append("4. Comparison with previous iteration")
        prompt_parts.append("5. Address any detected regressions")
        prompt_parts.append("6. Provide actionable recommendations")
        
        return '\n'.join(prompt_parts)
                
