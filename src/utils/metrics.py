import time
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Metrics:
    operation: str
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def stop(self):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        return self
    
    def add_metadata(self, **kwargs):
        self.metadata.update(kwargs)
        return self
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "duration_ms": self.duration_ms,
            "timestamp": datetime.now().isoformat(),
            "metadata": self.metadata
        }

class MetricsCollector:
    def __init__(self):
        self.metrics = []
    
    def track(self, operation: str) -> Metrics:
        m = Metrics(operation=operation)
        self.metrics.append(m)
        return m
    
    def get_summary(self) -> Dict[str, Any]:
        if not self.metrics:
            return {}
        
        operations = {}
        for m in self.metrics:
            if m.operation not in operations:
                operations[m.operation] = []
            if m.duration_ms:
                operations[m.operation].append(m.duration_ms)
        
        summary = {}
        for op, durations in operations.items():
            if durations:
                summary[op] = {
                    "count": len(durations),
                    "avg_ms": sum(durations) / len(durations),
                    "min_ms": min(durations),
                    "max_ms": max(durations),
                    "total_ms": sum(durations)
                }
        
        return summary
    
    def clear(self):
        self.metrics.clear()

metrics_collector = MetricsCollector()