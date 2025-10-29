"""
Enhanced CodeGen Phase - Code generation with memory of previous code.

This module provides an enhanced code generator that can reuse successful
components and evolve code incrementally across iterations.
"""

from typing import Optional, Dict, List, Any
from datetime import datetime

from ..core.state import ProjectState, Iteration
from ..core.version_manager import VersionManager
from ..core.decision_logger import DecisionLogger


class EnhancedCodeGen:
    """
    Code generator with memory of previous implementations.
    
    Can reuse successful components, evolve code incrementally,
    and avoid regenerating what already works.
    """
    
    def __init__(
        self,
        version_manager: VersionManager,
        decision_logger: DecisionLogger
    ):
        """
        Initialize EnhancedCodeGen.
        
        Args:
            version_manager: For loading previous iterations
            decision_logger: For querying code-related decisions
        """
        self.version_manager = version_manager
        self.decision_logger = decision_logger
    
    def generate(
        self,
        analysis_result: Dict[str, Any],
        project_name: str,
        current_iteration: int,
        user_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate code with memory of previous implementations.
        
        Args:
            analysis_result: Results from analyzer phase
            project_name: Project identifier
            current_iteration: Current iteration number
            user_instructions: Optional specific instructions
            
        Returns:
            Dictionary with code generation results
        """
        result = {
            'iteration': current_iteration,
            'timestamp': datetime.now().isoformat(),
            'has_previous_code': current_iteration > 1,
            'reused_components': [],
            'modified_components': [],
            'new_components': [],
            'code_context': None,
            'generation_strategy': None
        }
        
        # If first iteration, simple generation
        if current_iteration == 1:
            result['generation_strategy'] = 'full_generation'
            result['code_context'] = "First iteration - generating from scratch"
            return result
        
        # Build code context from previous iterations
        code_context = self._build_code_context(
            project_name,
            current_iteration,
            analysis_result,
            user_instructions
        )
        
        result['code_context'] = code_context['summary']
        result['reused_components'] = code_context.get('reusable', [])
        result['modified_components'] = code_context.get('to_modify', [])
        result['new_components'] = code_context.get('to_create', [])
        result['generation_strategy'] = code_context.get('strategy', 'incremental')
        
        # In a real implementation, this would call an LLM
        # For now, return the context structure
        result['generation'] = {
            'status': 'context_ready',
            'message': 'Code context successfully built',
            'estimated_files': len(code_context.get('reusable', [])) + 
                             len(code_context.get('to_modify', [])) +
                             len(code_context.get('to_create', []))
        }
        
        return result
    
    def _build_code_context(
        self,
        project_name: str,
        current_iteration: int,
        analysis_result: Dict[str, Any],
        user_instructions: Optional[str]
    ) -> Dict[str, Any]:
        """
        Build code context from previous iterations.
        
        Identifies what code can be reused, what needs modification,
        and what needs to be created fresh.
        
        Args:
            project_name: Project identifier
            current_iteration: Current iteration number
            analysis_result: Current analysis results
            user_instructions: Optional user instructions
            
        Returns:
            Dictionary with code context
        """
        context = {
            'summary': '',
            'strategy': 'incremental',
            'reusable': [],
            'to_modify': [],
            'to_create': [],
            'previous_code_summary': None
        }
        
        # 1. Load previous iteration
        try:
            prev_iteration = self.version_manager.get_iteration(current_iteration - 1)
        except FileNotFoundError:
            context['summary'] = "No previous code found"
            context['strategy'] = 'full_generation'
            return context
        
        # 2. Extract previous code information
        prev_outputs = prev_iteration.state.outputs
        prev_codegen = prev_outputs.get('code_generation', {})
        prev_validation = prev_outputs.get('validation', {})
        
        context['previous_code_summary'] = {
            'files_generated': len(prev_codegen.get('files', [])),
            'issues_found': len(prev_validation.get('issues', [])),
            'scores': prev_validation.get('scores', {})
        }
        
        # 3. Query codegen decisions from previous iteration
        all_decisions = self.decision_logger.get_decisions_for_iteration(
            current_iteration - 1
        )
        codegen_decisions = [d for d in all_decisions if d.phase == 'codegen']
        
        # 4. Determine reuse strategy
        issues = prev_validation.get('issues', [])
        high_severity_issues = [i for i in issues if i.get('severity') == 'high']
        
        if high_severity_issues:
            context['strategy'] = 'partial_regeneration'
        elif prev_validation.get('scores', {}).get('code', 0) >= 8:
            context['strategy'] = 'minimal_changes'
        else:
            context['strategy'] = 'incremental'
        
        # 5. Categorize components
        prev_components = self._extract_components(prev_codegen)
        current_components = analysis_result.get('analysis', {}).get('main_components', [])
        
        # Components that exist and don't have issues can be reused
        for comp in prev_components:
            comp_issues = [i for i in issues if comp['name'] in i.get('component', '')]
            if not comp_issues and comp['name'] in current_components:
                context['reusable'].append(comp['name'])
            elif comp['name'] in current_components:
                context['to_modify'].append({
                    'name': comp['name'],
                    'reason': f"{len(comp_issues)} issues found"
                })
        
        # New components that need to be created
        for comp in current_components:
            if comp not in [c['name'] for c in prev_components]:
                context['to_create'].append(comp)
        
        # 6. Build summary
        summary_parts = [
            f"Code context for iteration {current_iteration}:",
            f"- Strategy: {context['strategy']}",
            f"- Previous files: {len(prev_components)}",
            f"- Reusable: {len(context['reusable'])}",
            f"- To modify: {len(context['to_modify'])}",
            f"- To create: {len(context['to_create'])}"
        ]
        
        if codegen_decisions:
            summary_parts.append(f"- Previous decisions: {len(codegen_decisions)}")
        
        context['summary'] = '\n'.join(summary_parts)
        
        return context
    
    def _extract_components(self, codegen_output: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract component information from previous code generation output.
        
        Args:
            codegen_output: Previous code generation output
            
        Returns:
            List of component dictionaries
        """
        components = []
        files = codegen_output.get('files', [])
        
        for file_info in files:
            if isinstance(file_info, dict):
                components.append({
                    'name': file_info.get('name', 'unknown'),
                    'type': file_info.get('type', 'file'),
                    'path': file_info.get('path', '')
                })
        
        return components
    
    def build_prompt(
        self,
        analysis_result: Dict[str, Any],
        code_context: Dict[str, Any]
    ) -> str:
        """
        Build enriched prompt with code context.
        
        This method would be used when integrating with an actual LLM.
        
        Args:
            analysis_result: Results from analyzer
            code_context: Code context from _build_code_context
            
        Returns:
            Formatted prompt string
        """
        prompt_parts = []
        
        # Header
        prompt_parts.append("# CODE GENERATION WITH MEMORY")
        prompt_parts.append("")
        
        # Strategy
        prompt_parts.append(f"## GENERATION STRATEGY: {code_context.get('strategy', 'incremental').upper()}")
        prompt_parts.append("")
        
        # Previous code summary
        if code_context.get('previous_code_summary'):
            prev = code_context['previous_code_summary']
            prompt_parts.append("## PREVIOUS CODE")
            prompt_parts.append(f"Files generated: {prev['files_generated']}")
            prompt_parts.append(f"Issues found: {prev['issues_found']}")
            prompt_parts.append(f"Code score: {prev['scores'].get('code', 'N/A')}/10")
            prompt_parts.append("")
        
        # Reusable components
        if code_context.get('reusable'):
            prompt_parts.append("## COMPONENTS TO REUSE (No changes needed)")
            for comp in code_context['reusable']:
                prompt_parts.append(f"- {comp}")
            prompt_parts.append("")
        
        # Components to modify
        if code_context.get('to_modify'):
            prompt_parts.append("## COMPONENTS TO MODIFY")
            for comp in code_context['to_modify']:
                name = comp['name'] if isinstance(comp, dict) else comp
                reason = comp.get('reason', 'updates needed') if isinstance(comp, dict) else 'updates needed'
                prompt_parts.append(f"- {name}: {reason}")
            prompt_parts.append("")
        
        # New components
        if code_context.get('to_create'):
            prompt_parts.append("## NEW COMPONENTS TO CREATE")
            for comp in code_context['to_create']:
                prompt_parts.append(f"- {comp}")
            prompt_parts.append("")
        
        # Architecture from analysis
        if analysis_result.get('analysis'):
            analysis = analysis_result['analysis']
            prompt_parts.append("## CURRENT ARCHITECTURE")
            prompt_parts.append(f"Pattern: {analysis.get('architecture_pattern', 'N/A')}")
            prompt_parts.append(f"Components: {', '.join(analysis.get('main_components', []))}")
            prompt_parts.append("")
        
        # Instructions
        prompt_parts.append("## TASK")
        prompt_parts.append("Generate code following the strategy above:")
        prompt_parts.append("1. Reuse unchanged components from previous iteration")
        prompt_parts.append("2. Modify components that need updates")
        prompt_parts.append("3. Create new components as needed")
        prompt_parts.append("4. Maintain consistency across the codebase")
        prompt_parts.append("5. Address issues from previous validation")
        
        return '\n'.join(prompt_parts)
                
