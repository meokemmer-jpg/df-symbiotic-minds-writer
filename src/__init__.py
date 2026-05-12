# df-symbiotic-minds-writer src package [CRUX-MK]
# LAZY-IMPORT pattern: heavy modules import only when accessed via __getattr__

__version__ = "0.1.0-skeleton"


def __getattr__(name):
    """Lazy import to avoid loading heavy modules at package import time."""
    if name == "ChapterGenerator":
        from .chapter_generator import ChapterGenerator
        return ChapterGenerator
    if name == "OutlineManager":
        from .outline_manager import OutlineManager
        return OutlineManager
    if name == "StyleGuide":
        from .style_guide import StyleGuide
        return StyleGuide
    if name == "AdapterOrchestrator":
        from .adapter_orchestrator import AdapterOrchestrator
        return AdapterOrchestrator
    if name == "AuditLogger":
        from .audit_logger import AuditLogger
        return AuditLogger
    raise AttributeError(f"module {__name__} has no attribute {name}")
