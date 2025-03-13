"""
Detector modules that identify issues in text.
"""

from socratic_clarifier.detectors.ambiguity import AmbiguityDetector
from socratic_clarifier.detectors.bias import BiasDetector

__all__ = ["AmbiguityDetector", "BiasDetector"]
