# Changelog

All notable changes to ArqSysIA will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.1] - 2025-10-30

### 🎉 Session 15 - Refinement & Optimization

#### Added
- **Enhanced CLI with better UX:**
  - Input validation with clear error messages
  - Safety confirmations for important operations
  - Contextual tips and helpful messages
  - Project statistics and trend analysis
  - Project size calculation in settings
  - Better interrupt handling (Ctrl+C)
  - Summary statistics on exit

- **Improved Error Handling:**
  - Specific error messages by error type
  - Graceful degradation on failures
  - Better exception messages for debugging
  - Retry logic for failed operations
  
- **New Features:**
  - Iteration trend display in main menu (📈/📉/➡️)
  - Requirements summary (line count, word count)
  - Confirmation dialogs for destructive operations
  - Project name validation on CLI init
  - Maximum input limits (100 lines) for safety

#### Changed
- **CLI Optimization:**
  - Refactored `main.py` with 500+ lines of improvements
  - Better separation of concerns
  - Cleaner error handling flow
  - More informative status messages
  - Improved menu navigation

- **Test Suite Updates:**
  - Fixed all 96 tests to work with optimized CLI
  - Updated test fixtures for better reusability
  - Corrected `save_iteration()` signatures
  - Fixed trend calculation tests
  - Better test organization and documentation

- **Documentation:**
  - Complete rewrite of README.md with:
    - Quick start guide
    - Detailed CLI command reference
    - Architecture overview
    - Testing guide
    - Contribution guidelines
  - Updated requirements.txt with all dependencies
  - Added comprehensive inline documentation

#### Fixed
- Property access corrections in CLI:
  - `iteration.number` → `iteration.iteration_number`
  - `iteration.state.timestamp` → `iteration.created_at`
  - `result.iteration_number` → `result.iteration`
  - Proper score access via `outputs['validation']['overall_score']`
- DiffViewer now raises `ValueError` for invalid modes
- Better handling of empty projects
- Improved EOF detection in interactive inputs

#### Security
- Project name validation to prevent directory traversal
- Input sanitization for file operations
- Safe handling of user-provided feedback

---

## [1.0.0] - 2025-10-29

### 🚀 Initial Release - Sessions 6-14

#### Added
- **Core Architecture:**
  - ProjectState and Iteration data structures
  - IterativeOrchestrator for workflow coordination
  - VersionManager for iteration management
  - DecisionLogger for decision tracking
  - DiffEngine for iteration comparison

- **Enhanced Phases:**
  - EnhancedAnalyzer with historical context
  - EnhancedCodeGen with code memory
  - EnhancedValidator with trend analysis

- **Storage System:**
  - FileStorage backend with JSON persistence
  - Metadata management
  - Project isolation

- **CLI Interface:**
  - Interactive menu system
  - 7 main commands
  - IterationViewer for history visualization
  - DiffViewer for comparison

- **LLM Integration:**
  - OllamaClient for local LLM access
  - DeepSeek-R1 model support
  - Configurable model settings

- **Testing:**
  - 96 comprehensive tests
  - 100% test coverage goal
  - Integration tests
  - Unit tests for all components

#### Milestones
- ✅ Session 6: Base foundations
- ✅ Session 7: FileStorage (19 tests)
- ✅ Session 8: VersionManager (9 tests)
- ✅ Session 9: DecisionLogger (8 tests)
- ✅ Session 10: DiffEngine (9 tests)
- ✅ Session 11: Enhanced Phases (14 tests)
- ⏭️ Session 12: (Documented, not implemented)
- ✅ Session 13: Iterative Orchestrator (18 tests)
- ✅ Session 14: CLI Implementation (24 tests)

---

## [Unreleased]

### Planned Features
- Multiple LLM provider support (OpenAI, Anthropic)
- Export to standard formats (PlantUML, C4)
- Web UI interface
- REST API
- Git integration
- Architecture templates
- Existing code analysis
- Automatic documentation generation

---

## Version History Summary

| Version | Date | Description | Tests |
|---------|------|-------------|-------|
| 1.0.1 | 2025-10-30 | Refinement & Optimization | 96/96 ✅ |
| 1.0.0 | 2025-10-29 | Initial Release | 96/96 ✅ |

---

## Migration Guides

### Upgrading from 1.0.0 to 1.0.1

No breaking changes. All existing projects and data are fully compatible.

**Recommended actions:**
1. Update your local repository: `git pull`
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Run tests to verify: `pytest tests/ -v`

**New features to try:**
- Notice the trend indicators in the main menu
- Check out the improved error messages
- Try the new confirmation dialogs
- View project statistics in Settings

---

## Notes

### Testing
All versions maintain 100% test passage rate (96/96 tests).

### Backwards Compatibility
We maintain backwards compatibility for:
- Storage format (ProjectState, Iteration)
- API interfaces (public methods)
- CLI commands (all existing commands work)

### Breaking Changes
None in current versions. Any future breaking changes will be clearly marked with a major version bump (e.g., 2.0.0).

---

**For detailed commit history, see:** [GitHub Commits](https://github.com/yourusername/ArqSysIA/commits)
