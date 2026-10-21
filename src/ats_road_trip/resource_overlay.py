"""In-memory staged resources retaining original source ownership metadata."""
from collections import ChainMap
from pathlib import Path
from .package import ResourceStack, Resource, virtual_path

class _MemoryPackage:
    def __init__(self, values):
        self.path = Path('<staged-compatibility>')
        self.values = values
        self.files = {name:name for name in values}
    def read(self, path, *, max_bytes=8*1024*1024):
        value = self.values[virtual_path(path)]
        if len(value)>max_bytes: raise ValueError('Staged resource exceeds read limit')
        return value
    def prefetch(self, names, **kwargs):
        return None

class OverlayResourceStack(ResourceStack):
    """Read composed bytes while existing paths retain their original provider.

    Ownership is intentionally separate from the effective staged payload.
    New private resources are supplied by a memory package. No files are written.
    """
    def __init__(self, base, overrides):
        if not isinstance(overrides, dict): raise ValueError('Resource overrides must be a dictionary')
        self.base = base
        self.values = {}
        for name, value in overrides.items():
            if virtual_path(name)!=name or type(value) is not bytes:
                raise ValueError('Overrides require canonical paths and bytes')
            self.values[name] = value
        memory = _MemoryPackage(self.values)
        new = {name:(memory,Resource(str(memory.path),name,name))
               for name in self.values if name not in base.resources}
        self.resources = ChainMap(new, base.resources)
        self.packages = [*base.packages, memory]
        self.overrides = list(getattr(base, 'overrides', []))
    def read(self, path, *, max_bytes=8*1024*1024):
        path=virtual_path(path)
        if path not in self.values: return self.base.read(path,max_bytes=max_bytes)
        value=self.values[path]
        if len(value)>max_bytes: raise ValueError('Staged resource exceeds read limit')
        return value
