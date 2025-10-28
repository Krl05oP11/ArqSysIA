"""
Diff Engine for comparing iterations and generating diffs.

This module provides functionality to compare two ProjectState objects
and generate detailed difference reports, similar to git diff.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

from .state import ProjectState, Decision


@dataclass
class DiffResult:
    """Result of comparing two iterations"""
    
    iteration_from: int
    iteration_to: int
    
    # Architecture changes
    architecture_changed: bool
    architecture_from: str
    architecture_to: str
    
    # Component changes
    components_added: List[str]
    components_removed: List[str]
    components_modified: List[str]
    
    # Score changes
    score_improvements: Dict[str, int] = field(default_factory=dict)
    score_regressions: Dict[str, int] = field(default_factory=dict)
    
    # Issues
    new_issues: List[Dict] = field(default_factory=list)
    resolved_issues: List[Dict] = field(default_factory=list)
    persisting_issues: List[Dict] = field(default_factory=list)
    
    # Decisions made between iterations
    decisions_made: List[Decision] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)


class DiffEngine:
    """Engine for comparing iterations and generating diffs"""
    
    def __init__(self):
        """Initialize DiffEngine"""
        pass
    
    def compare_iterations(
        self,
        state1: ProjectState,
        state2: ProjectState
    ) -> DiffResult:
        """
        Compare two ProjectState objects and generate a comprehensive diff.
        
        Args:
            state1: First state (older iteration)
            state2: Second state (newer iteration)
            
        Returns:
            DiffResult containing all detected differences
        """
        # Compare architecture
        arch_diff = self._compare_architecture(state1, state2)
        
        # Compare components
        comp_diff = self._compare_components(state1, state2)
        
        # Compare scores
        score_diff = self._compare_scores(state1, state2)
        
        # Compare issues
        issues_diff = self._compare_issues(state1, state2)
        
        # Extract decisions from state2
        decisions = getattr(state2, 'decisions', [])
        
        return DiffResult(
            iteration_from=state1.iteration,
            iteration_to=state2.iteration,
            architecture_changed=arch_diff['changed'],
            architecture_from=arch_diff['from'],
            architecture_to=arch_diff['to'],
            components_added=comp_diff['added'],
            components_removed=comp_diff['removed'],
            components_modified=comp_diff['modified'],
            score_improvements=score_diff['improvements'],
            score_regressions=score_diff['regressions'],
            new_issues=issues_diff['new'],
            resolved_issues=issues_diff['resolved'],
            persisting_issues=issues_diff['persisting'],
            decisions_made=decisions
        )
    
    def format_diff_text(self, diff: DiffResult) -> str:
        """
        Format a DiffResult as human-readable text (git diff style).
        
        Args:
            diff: DiffResult to format
            
        Returns:
            Formatted text representation of the diff
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append(f"DIFF: Iteration {diff.iteration_from} → {diff.iteration_to}")
        lines.append(f"Timestamp: {diff.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)
        lines.append("")
        
        # Architecture changes
        if diff.architecture_changed:
            lines.append("📐 ARCHITECTURE CHANGES:")
            lines.append(f"  - {diff.architecture_from}")
            lines.append(f"  + {diff.architecture_to}")
            lines.append("")
        else:
            lines.append("📐 ARCHITECTURE: No changes")
            lines.append("")
        
        # Component changes
        if diff.components_added or diff.components_removed or diff.components_modified:
            lines.append("🔧 COMPONENT CHANGES:")
            
            if diff.components_added:
                lines.append(f"  + Added ({len(diff.components_added)}):")
                for comp in diff.components_added:
                    lines.append(f"    + {comp}")
            
            if diff.components_removed:
                lines.append(f"  - Removed ({len(diff.components_removed)}):")
                for comp in diff.components_removed:
                    lines.append(f"    - {comp}")
            
            if diff.components_modified:
                lines.append(f"  ~ Modified ({len(diff.components_modified)}):")
                for comp in diff.components_modified:
                    lines.append(f"    ~ {comp}")
            
            lines.append("")
        else:
            lines.append("🔧 COMPONENTS: No changes")
            lines.append("")
        
        # Score changes
        if diff.score_improvements or diff.score_regressions:
            lines.append("📊 SCORE CHANGES:")
            
            if diff.score_improvements:
                lines.append(f"  ⬆️  Improvements:")
                for metric, delta in diff.score_improvements.items():
                    lines.append(f"    {metric}: +{delta}")
            
            if diff.score_regressions:
                lines.append(f"  ⬇️  Regressions:")
                for metric, delta in diff.score_regressions.items():
                    lines.append(f"    {metric}: {delta}")
            
            lines.append("")
        else:
            lines.append("📊 SCORES: No changes")
            lines.append("")
        
        # Issue changes
        if diff.new_issues or diff.resolved_issues:
            lines.append("🐛 ISSUE CHANGES:")
            
            if diff.new_issues:
                lines.append(f"  + New Issues ({len(diff.new_issues)}):")
                for issue in diff.new_issues[:3]:  # Show first 3
                    severity = issue.get('severity', 'unknown')
                    description = issue.get('description', 'No description')
                    lines.append(f"    [{severity}] {description}")
                if len(diff.new_issues) > 3:
                    lines.append(f"    ... and {len(diff.new_issues) - 3} more")
            
            if diff.resolved_issues:
                lines.append(f"  ✓ Resolved Issues ({len(diff.resolved_issues)}):")
                for issue in diff.resolved_issues[:3]:  # Show first 3
                    severity = issue.get('severity', 'unknown')
                    description = issue.get('description', 'No description')
                    lines.append(f"    [{severity}] {description}")
                if len(diff.resolved_issues) > 3:
                    lines.append(f"    ... and {len(diff.resolved_issues) - 3} more")
            
            if diff.persisting_issues:
                lines.append(f"  ⚠️  Persisting Issues ({len(diff.persisting_issues)})")
            
            lines.append("")
        else:
            lines.append("🐛 ISSUES: No changes")
            lines.append("")
        
        # Decisions
        if diff.decisions_made:
            lines.append(f"💡 DECISIONS MADE ({len(diff.decisions_made)}):")
            for decision in diff.decisions_made[:5]:  # Show first 5
                phase = decision.phase
                dec_text = decision.decision[:60] + "..." if len(decision.decision) > 60 else decision.decision
                lines.append(f"  [{phase}] {dec_text}")
            if len(diff.decisions_made) > 5:
                lines.append(f"  ... and {len(diff.decisions_made) - 5} more decisions")
            lines.append("")
        
        # Footer
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def _compare_architecture(self, s1: ProjectState, s2: ProjectState) -> Dict[str, Any]:
        """Compare architecture patterns between two states"""
        arch1 = self._get_architecture(s1)
        arch2 = self._get_architecture(s2)
        
        return {
            'changed': arch1 != arch2,
            'from': arch1,
            'to': arch2
        }
    
    def _compare_components(self, s1: ProjectState, s2: ProjectState) -> Dict[str, List[str]]:
        """Compare components between two states"""
        comps1 = set(self._get_components(s1))
        comps2 = set(self._get_components(s2))
        
        added = list(comps2 - comps1)
        removed = list(comps1 - comps2)
        common = comps1 & comps2
        
        # For now, we can't detect modifications without deeper analysis
        # This would require comparing component details
        modified = []
        
        return {
            'added': sorted(added),
            'removed': sorted(removed),
            'modified': sorted(modified)
        }
    
    def _compare_scores(self, s1: ProjectState, s2: ProjectState) -> Dict[str, Dict[str, int]]:
        """Compare scores/metrics between two states"""
        scores1 = self._get_scores(s1)
        scores2 = self._get_scores(s2)
        
        improvements = {}
        regressions = {}
        
        # Find common metrics
        all_metrics = set(scores1.keys()) | set(scores2.keys())
        
        for metric in all_metrics:
            score1 = scores1.get(metric, 0)
            score2 = scores2.get(metric, 0)
            delta = score2 - score1
            
            if delta > 0:
                improvements[metric] = delta
            elif delta < 0:
                regressions[metric] = delta
        
        return {
            'improvements': improvements,
            'regressions': regressions
        }
    
    def _compare_issues(self, s1: ProjectState, s2: ProjectState) -> Dict[str, List[Dict]]:
        """Compare issues between two states"""
        issues1 = self._get_issues(s1)
        issues2 = self._get_issues(s2)
        
        # Simple comparison by description
        # In a real scenario, we'd need issue IDs
        issues1_set = {self._issue_key(i) for i in issues1}
        issues2_set = {self._issue_key(i) for i in issues2}
        
        new_keys = issues2_set - issues1_set
        resolved_keys = issues1_set - issues2_set
        persisting_keys = issues1_set & issues2_set
        
        # Find actual issue objects
        new_issues = [i for i in issues2 if self._issue_key(i) in new_keys]
        resolved_issues = [i for i in issues1 if self._issue_key(i) in resolved_keys]
        persisting_issues = [i for i in issues2 if self._issue_key(i) in persisting_keys]
        
        return {
            'new': new_issues,
            'resolved': resolved_issues,
            'persisting': persisting_issues
        }
    
    def _get_architecture(self, state: ProjectState) -> str:
        """Extract architecture pattern from state"""
        outputs = getattr(state, 'outputs', {})
        analysis = outputs.get('analysis', {})
        return analysis.get('architecture_pattern', 'Unknown')
    
    def _get_components(self, state: ProjectState) -> List[str]:
        """Extract component list from state"""
        outputs = getattr(state, 'outputs', {})
        analysis = outputs.get('analysis', {})
        return analysis.get('main_components', [])
    
    def _get_scores(self, state: ProjectState) -> Dict[str, int]:
        """Extract scores from state"""
        outputs = getattr(state, 'outputs', {})
        validation = outputs.get('validation', {})
        return validation.get('scores', {})
    
    def _get_issues(self, state: ProjectState) -> List[Dict]:
        """Extract issues from state"""
        outputs = getattr(state, 'outputs', {})
        validation = outputs.get('validation', {})
        return validation.get('issues', [])
    
    def _issue_key(self, issue: Dict) -> str:
        """Generate a simple key for issue comparison"""
        severity = issue.get('severity', '')
        description = issue.get('description', '')
        return f"{severity}:{description}"
        
