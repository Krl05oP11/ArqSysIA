"""
Enhanced Analyzer Phase - Analysis with historical context from previous iterations.

This module provides an enhanced analyzer that leverages VersionManager,
DecisionLogger, and DiffEngine to build rich context from previous iterations.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from ..core.state import ProjectState, Decision, Iteration
from ..core.version_manager import VersionManager
from ..core.decision_logger import DecisionLogger
from ..core.diff_engine import DiffEngine


class EnhancedAnalyzer:
    """
    Analyzer with historical context support.
    
    Uses previous iterations, decisions, and diffs to provide
    richer context for architectural analysis.
    """
    
    def __init__(
        self,
        version_manager: VersionManager,
        decision_logger: DecisionLogger,
        diff_engine: DiffEngine
    ):
        """
        Initialize EnhancedAnalyzer.
        
        Args:
            version_manager: For loading previous iterations
            decision_logger: For querying past decisions
            diff_engine: For comparing iterations
        """
        self.version_manager = version_manager
        self.decision_logger = decision_logger
        self.diff_engine = diff_engine
    
    def analyze(
        self,
        requirements: str,
        project_name: str,
        current_iteration: int,
        user_feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform architectural analysis with historical context.
        
        Args:
            requirements: Current requirements/instructions
            project_name: Project identifier
            current_iteration: Current iteration number (1-based)
            user_feedback: Optional user feedback from previous iteration
            
        Returns:
            Dictionary with analysis results including context information
        """
        # Initialize result structure
        result = {
            'iteration': current_iteration,
            'timestamp': datetime.now().isoformat(),
            'requirements': requirements,
            'user_feedback': user_feedback,
            'has_context': current_iteration > 1,
            'context_summary': None,
            'previous_decisions': [],
            'diff_summary': None,
            'analysis': None  # Would be populated by LLM in real implementation
        }
        
        # If first iteration, return early (no context available)
        if current_iteration == 1:
            result['context_summary'] = "First iteration - no previous context"
            return result
        
        # Build historical context
        context = self._build_historical_context(
            project_name,
            current_iteration,
            requirements,
            user_feedback
        )
        
        result['context_summary'] = context['summary']
        result['previous_decisions'] = context['decisions']
        result['diff_summary'] = context['diff_summary']
        result['previous_iteration'] = context['previous_iteration']
        
        # In a real implementation, this would call an LLM with the enriched context
        # For now, we just return the context structure
        result['analysis'] = {
            'status': 'context_ready',
            'message': 'Historical context successfully built',
            'context_tokens_estimate': self._estimate_context_tokens(context)
        }
        
        return result
    
    def _build_historical_context(
        self,
        project_name: str,
        current_iteration: int,
        requirements: str,
        user_feedback: Optional[str]
    ) -> Dict[str, Any]:
        """
        Build comprehensive historical context from previous iterations.
        
        Args:
            project_name: Project identifier
            current_iteration: Current iteration number
            requirements: Current requirements
            user_feedback: Optional user feedback
            
        Returns:
            Dictionary with historical context components
        """
        context = {
            'summary': '',
            'decisions': [],
            'diff_summary': None,
            'previous_iteration': None
        }
        
        # 1. Load previous iteration
        try:
            prev_iteration = self.version_manager.get_iteration(current_iteration - 1)
            context['previous_iteration'] = {
                'iteration': prev_iteration.iteration_number,
                'created_at': prev_iteration.created_at.isoformat(),
                'status': prev_iteration.status,
                'scores': prev_iteration.final_scores
            }
        except FileNotFoundError:
            context['summary'] = f"Iteration {current_iteration - 1} not found"
            return context
        
        # 2. Query previous decisions
        decisions = self.decision_logger.get_decisions_for_iteration(current_iteration - 1)
        context['decisions'] = [
            {
                'phase': d.phase,
                'decision': d.decision,
                'rationale': d.rationale[:100] + '...' if len(d.rationale) > 100 else d.rationale
            }
            for d in decisions[:5]  # Limit to 5 most recent decisions
        ]
        
        # 3. Generate diff if we have 2+ previous iterations
        if current_iteration > 2:
            try:
                iter_before = self.version_manager.get_iteration(
                    current_iteration - 2
                )
                
                diff = self.diff_engine.compare_iterations(
                    iter_before.state,
                    prev_iteration.state
                )
                
                context['diff_summary'] = {
                    'architecture_changed': diff.architecture_changed,
                    'components_added': len(diff.components_added),
                    'components_removed': len(diff.components_removed),
                    'score_improvements': len(diff.score_improvements),
                    'score_regressions': len(diff.score_regressions),
                    'new_issues': len(diff.new_issues),
                    'resolved_issues': len(diff.resolved_issues)
                }
            except FileNotFoundError:
                context['diff_summary'] = "Previous iteration not available for diff"
        
        # 4. Build summary text
        summary_parts = [
            f"Context for iteration {current_iteration}:",
            f"- Previous iteration: {prev_iteration.iteration_number}",
            f"- Decisions made: {len(decisions)}",
            f"- Previous scores: {prev_iteration.final_scores}"
        ]
        
        if context['diff_summary']:
            summary_parts.append(f"- Recent changes: {context['diff_summary']}")
        
        if user_feedback:
            summary_parts.append(f"- User feedback: {user_feedback[:100]}...")
        
        context['summary'] = '\n'.join(summary_parts)
        
        return context
    
    def _estimate_context_tokens(self, context: Dict[str, Any]) -> int:
        """
        Estimate the number of tokens in the context.
        
        Simple estimation: 1 token ≈ 4 characters
        
        Args:
            context: Context dictionary
            
        Returns:
            Estimated token count
        """
        # Convert context to string and estimate
        import json
        context_str = json.dumps(context, indent=2)
        return len(context_str) // 4
    
    def build_prompt(
        self,
        requirements: str,
        context: Dict[str, Any]
    ) -> str:
        """
        Build enriched prompt with historical context.
        
        This method would be used when integrating with an actual LLM.
        
        Args:
            requirements: Current requirements
            context: Historical context from _build_historical_context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Header
        prompt_parts.append("# ARCHITECTURAL ANALYSIS WITH HISTORICAL CONTEXT")
        prompt_parts.append("")
        
        # Current requirements
        prompt_parts.append("## CURRENT REQUIREMENTS")
        prompt_parts.append(requirements)
        prompt_parts.append("")
        
        # Previous iteration summary
        if context.get('previous_iteration'):
            prev = context['previous_iteration']
            prompt_parts.append("## PREVIOUS ITERATION")
            prompt_parts.append(f"Iteration: {prev['iteration']}")
            prompt_parts.append(f"Status: {prev['status']}")
            prompt_parts.append(f"Scores: {prev['scores']}")
            prompt_parts.append("")
        
        # Previous decisions
        if context.get('decisions'):
            prompt_parts.append("## PREVIOUS DECISIONS")
            for i, dec in enumerate(context['decisions'], 1):
                prompt_parts.append(f"{i}. [{dec['phase']}] {dec['decision']}")
                prompt_parts.append(f"   Rationale: {dec['rationale']}")
            prompt_parts.append("")
        
        # Diff summary
        if context.get('diff_summary') and isinstance(context['diff_summary'], dict):
            diff = context['diff_summary']
            prompt_parts.append("## RECENT CHANGES")
            prompt_parts.append(f"Architecture changed: {diff['architecture_changed']}")
            prompt_parts.append(f"Components added: {diff['components_added']}")
            prompt_parts.append(f"Components removed: {diff['components_removed']}")
            prompt_parts.append(f"Score improvements: {diff['score_improvements']}")
            prompt_parts.append(f"New issues: {diff['new_issues']}")
            prompt_parts.append(f"Resolved issues: {diff['resolved_issues']}")
            prompt_parts.append("")
        
        # Instructions
        prompt_parts.append("## TASK")
        prompt_parts.append("Based on the requirements and historical context above:")
        prompt_parts.append("1. Propose an architectural pattern")
        prompt_parts.append("2. Define main components")
        prompt_parts.append("3. Select appropriate technologies")
        prompt_parts.append("4. Consider lessons learned from previous iterations")
        prompt_parts.append("5. Address any issues from previous iterations")
        
        return '\n'.join(prompt_parts)
                
