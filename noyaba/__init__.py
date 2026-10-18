"""Noyaba v1.3 reference VM."""
LANGUAGE_VERSION = "1.3"
VM_VERSION = "1.0"
BYTECODE_VERSION = 1
from .vm import VM, run_source

__all__ = ["VM", "run_source", "LANGUAGE_VERSION", "VM_VERSION", "BYTECODE_VERSION"]
