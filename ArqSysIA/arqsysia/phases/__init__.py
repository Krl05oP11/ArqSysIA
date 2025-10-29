"""
Phases module for ArqSysIA.

This module contains both legacy phases (v1.0) and enhanced phases (v2.0)
with historical context support.
"""

# Legacy Phases (v1.0 - LLM-powered, for backwards compatibility)
# Note: These may be in the codebase from earlier sessions
# If they don't exist yet, these imports will fail - that's OK for now

try:
    from .analyzer import AnalyzerPhase
    from .codegen import CodeGenPhase
    from .validator import ValidatorPhase
    _has_legacy_phases = True
except ImportError:
    _has_legacy_phases = False

# Enhanced Phases (v2.0 with historical context)
from .enhanced_analyzer import EnhancedAnalyzer
from .enhanced_codegen import EnhancedCodeGen
from .enhanced_validator import EnhancedValidator

# Build __all__ dynamically
__all__ = [
    'EnhancedAnalyzer',
    'EnhancedCodeGen',
    'EnhancedValidator',
]

if _has_legacy_phases:
    __all__.extend([
        'AnalyzerPhase',
        'CodeGenPhase',
        'ValidatorPhase',
    ])
    
