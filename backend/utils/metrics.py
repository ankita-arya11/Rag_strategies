from typing import Dict, List, Any
from collections import defaultdict
import time


class MetricsTracker:
    """Track performance metrics for chunking and retrieval operations"""
    
    def __init__(self):
        self.chunking_metrics = defaultdict(list)
        self.retrieval_metrics = defaultdict(list)
        self.operation_history = []
    
    def record_chunking(self, strategy: str, latency_ms: float, chunk_count: int):
        """Record chunking operation metrics"""
        self.chunking_metrics[strategy].append({
            "latency_ms": latency_ms,
            "chunk_count": chunk_count,
            "timestamp": time.time()
        })
        
        self.operation_history.append({
            "type": "chunking",
            "strategy": strategy,
            "latency_ms": latency_ms,
            "timestamp": time.time()
        })
    
    def record_retrieval(self, strategy: str, latency_ms: float, result_count: int):
        """Record retrieval operation metrics"""
        self.retrieval_metrics[strategy].append({
            "latency_ms": latency_ms,
            "result_count": result_count,
            "timestamp": time.time()
        })
        
        self.operation_history.append({
            "type": "retrieval",
            "strategy": strategy,
            "latency_ms": latency_ms,
            "timestamp": time.time()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics"""
        summary = {
            "chunking": {},
            "retrieval": {},
            "total_operations": len(self.operation_history)
        }
        
        # Chunking statistics
        for strategy, metrics in self.chunking_metrics.items():
            if metrics:
                latencies = [m["latency_ms"] for m in metrics]
                chunk_counts = [m["chunk_count"] for m in metrics]
                summary["chunking"][strategy] = {
                    "count": len(metrics),
                    "avg_latency_ms": sum(latencies) / len(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies),
                    "avg_chunks": sum(chunk_counts) / len(chunk_counts)
                }
        
        # Retrieval statistics
        for strategy, metrics in self.retrieval_metrics.items():
            if metrics:
                latencies = [m["latency_ms"] for m in metrics]
                result_counts = [m["result_count"] for m in metrics]
                summary["retrieval"][strategy] = {
                    "count": len(metrics),
                    "avg_latency_ms": sum(latencies) / len(latencies),
                    "min_latency_ms": min(latencies),
                    "max_latency_ms": max(latencies),
                    "avg_results": sum(result_counts) / len(result_counts)
                }
        
        return summary
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent operations"""
        return self.operation_history[-limit:]
    
    def reset(self):
        """Reset all metrics"""
        self.chunking_metrics.clear()
        self.retrieval_metrics.clear()
        self.operation_history.clear()
