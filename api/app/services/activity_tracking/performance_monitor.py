"""
Performance Monitor Service

Service to capture system resource usage during operations.
Uses psutil to monitor CPU, memory, disk I/O, and network usage.
"""

import time
import psutil
import threading
import asyncio
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager, contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone

from aphrodite_logging import get_logger


@dataclass
class PerformanceMetrics:
    """Container for performance metrics"""
    # System Performance
    cpu_usage_percent: Optional[float] = None
    memory_usage_mb: Optional[int] = None
    disk_io_read_mb: Optional[float] = None
    disk_io_write_mb: Optional[float] = None
    
    # Network Performance
    network_download_mb: Optional[float] = None
    network_upload_mb: Optional[float] = None
    network_latency_ms: Optional[int] = None
    
    # Processing Stages
    stage_timings: Dict[str, float] = field(default_factory=dict)
    bottleneck_stage: Optional[str] = None
    
    # Quality Metrics
    error_rate: Optional[float] = None
    throughput_items_per_second: Optional[float] = None
    
    # Environment
    server_load_average: Optional[float] = None
    concurrent_operations: Optional[int] = None
    
    # Internal tracking
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        return {
            'cpu_usage_percent': self.cpu_usage_percent,
            'memory_usage_mb': self.memory_usage_mb,
            'disk_io_read_mb': self.disk_io_read_mb,
            'disk_io_write_mb': self.disk_io_write_mb,
            'network_download_mb': self.network_download_mb,
            'network_upload_mb': self.network_upload_mb,
            'network_latency_ms': self.network_latency_ms,
            'stage_timings': self.stage_timings,
            'bottleneck_stage': self.bottleneck_stage,
            'error_rate': self.error_rate,
            'throughput_items_per_second': self.throughput_items_per_second,
            'server_load_average': self.server_load_average,
            'concurrent_operations': self.concurrent_operations
        }


class PerformanceMonitor:
    """Monitor system performance during operations"""
    
    def __init__(self):
        self.logger = get_logger("aphrodite.performance_monitor", service="performance")
        self._monitoring = False
        self._metrics = PerformanceMetrics()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        
        # Baseline measurements
        self._baseline_cpu = 0.0
        self._baseline_memory = 0
        self._baseline_disk_io = None
        self._baseline_network_io = None
        
        # Peak measurements
        self._peak_cpu = 0.0
        self._peak_memory = 0
        self._total_disk_read = 0.0
        self._total_disk_write = 0.0
        self._total_network_recv = 0.0
        self._total_network_sent = 0.0
        
        # Process reference
        self._process = psutil.Process()
    
    def start_monitoring(self) -> None:
        """Start performance monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._stop_event.clear()
        self._metrics = PerformanceMetrics()
        self._metrics.start_time = datetime.now(timezone.utc)
        
        # Get baseline measurements
        self._capture_baseline()
        
        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor_loop)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        
        self.logger.debug("Performance monitoring started")
    
    def stop_monitoring(self) -> PerformanceMetrics:
        """Stop performance monitoring and return metrics"""
        if not self._monitoring:
            return self._metrics
        
        self._monitoring = False
        self._stop_event.set()
        
        # Wait for monitoring thread to complete
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        
        # Capture final measurements
        self._capture_final_metrics()
        self._metrics.end_time = datetime.now(timezone.utc)
        
        self.logger.debug("Performance monitoring stopped")
        return self._metrics
    
    def _capture_baseline(self) -> None:
        """Capture baseline system metrics"""
        try:
            # CPU baseline (need to call twice for accurate measurement)
            psutil.cpu_percent(interval=0.1)
            self._baseline_cpu = psutil.cpu_percent()
            
            # Memory baseline
            memory_info = self._process.memory_info()
            self._baseline_memory = memory_info.rss // (1024 * 1024)  # MB
            
            # Disk I/O baseline
            try:
                disk_io = psutil.disk_io_counters()
                if disk_io:
                    self._baseline_disk_io = {
                        'read_bytes': disk_io.read_bytes,
                        'write_bytes': disk_io.write_bytes
                    }
            except Exception:
                self._baseline_disk_io = None
            
            # Network I/O baseline
            try:
                network_io = psutil.net_io_counters()
                if network_io:
                    self._baseline_network_io = {
                        'bytes_recv': network_io.bytes_recv,
                        'bytes_sent': network_io.bytes_sent
                    }
            except Exception:
                self._baseline_network_io = None
            
        except Exception as e:
            self.logger.warning(f"Failed to capture baseline metrics: {e}")
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop"""
        while not self._stop_event.is_set():
            try:
                # CPU monitoring
                cpu_percent = psutil.cpu_percent()
                if cpu_percent > self._peak_cpu:
                    self._peak_cpu = cpu_percent
                
                # Memory monitoring
                memory_info = self._process.memory_info()
                current_memory = memory_info.rss // (1024 * 1024)  # MB
                if current_memory > self._peak_memory:
                    self._peak_memory = current_memory
                
                # Disk I/O monitoring
                if self._baseline_disk_io:
                    try:
                        disk_io = psutil.disk_io_counters()
                        if disk_io:
                            read_delta = disk_io.read_bytes - self._baseline_disk_io['read_bytes']
                            write_delta = disk_io.write_bytes - self._baseline_disk_io['write_bytes']
                            self._total_disk_read = max(self._total_disk_read, read_delta / (1024 * 1024))
                            self._total_disk_write = max(self._total_disk_write, write_delta / (1024 * 1024))
                    except Exception:
                        pass
                
                # Network I/O monitoring
                if self._baseline_network_io:
                    try:
                        network_io = psutil.net_io_counters()
                        if network_io:
                            recv_delta = network_io.bytes_recv - self._baseline_network_io['bytes_recv']
                            sent_delta = network_io.bytes_sent - self._baseline_network_io['bytes_sent']
                            self._total_network_recv = max(self._total_network_recv, recv_delta / (1024 * 1024))
                            self._total_network_sent = max(self._total_network_sent, sent_delta / (1024 * 1024))
                    except Exception:
                        pass
                
                # Sleep for monitoring interval
                time.sleep(0.5)
                
            except Exception as e:
                self.logger.warning(f"Error in monitoring loop: {e}")
                time.sleep(1.0)
    
    def _capture_final_metrics(self) -> None:
        """Capture final metrics and populate the metrics object"""
        try:
            # Set peak values
            self._metrics.cpu_usage_percent = self._peak_cpu
            self._metrics.memory_usage_mb = self._peak_memory
            self._metrics.disk_io_read_mb = self._total_disk_read if self._total_disk_read > 0 else None
            self._metrics.disk_io_write_mb = self._total_disk_write if self._total_disk_write > 0 else None
            self._metrics.network_download_mb = self._total_network_recv if self._total_network_recv > 0 else None
            self._metrics.network_upload_mb = self._total_network_sent if self._total_network_sent > 0 else None
            
            # System load average
            try:
                load_avg = psutil.getloadavg()
                self._metrics.server_load_average = load_avg[0]  # 1-minute average
            except (AttributeError, OSError):
                # getloadavg() not available on Windows
                self._metrics.server_load_average = None
            
            # Count concurrent operations (approximate by checking process count)
            try:
                current_process = psutil.Process()
                parent_process = current_process.parent()
                if parent_process:
                    children = parent_process.children(recursive=True)
                    self._metrics.concurrent_operations = len(children)
            except Exception:
                self._metrics.concurrent_operations = None
            
            # Identify bottleneck stage
            if self._metrics.stage_timings:
                bottleneck = max(self._metrics.stage_timings.items(), key=lambda x: x[1])
                self._metrics.bottleneck_stage = bottleneck[0]
        
        except Exception as e:
            self.logger.warning(f"Failed to capture final metrics: {e}")
    
    def add_stage_timing(self, stage_name: str, duration_ms: float) -> None:
        """Add timing for a specific processing stage"""
        self._metrics.stage_timings[stage_name] = duration_ms
        self.logger.debug(f"Added stage timing: {stage_name} = {duration_ms}ms")
    
    def set_throughput(self, items_processed: int, duration_seconds: float) -> None:
        """Set throughput metrics"""
        if duration_seconds > 0:
            self._metrics.throughput_items_per_second = items_processed / duration_seconds
    
    def set_error_rate(self, errors: int, total_items: int) -> None:
        """Set error rate metrics"""
        if total_items > 0:
            self._metrics.error_rate = errors / total_items


@contextmanager
def monitor_performance():
    """Context manager for performance monitoring"""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    try:
        yield monitor
    finally:
        monitor.stop_monitoring()


@asynccontextmanager
async def monitor_performance_async():
    """Async context manager for performance monitoring"""
    monitor = PerformanceMonitor()
    monitor.start_monitoring()
    try:
        yield monitor
    finally:
        monitor.stop_monitoring()


def performance_monitoring_decorator(func):
    """Decorator to add performance monitoring to functions"""
    def wrapper(*args, **kwargs):
        with monitor_performance() as monitor:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                monitor.add_stage_timing(func.__name__, duration_ms)
                return result
            except Exception as e:
                monitor.set_error_rate(1, 1)
                raise
    return wrapper


def async_performance_monitoring_decorator(func):
    """Decorator to add performance monitoring to async functions"""
    async def wrapper(*args, **kwargs):
        async with monitor_performance_async() as monitor:
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                monitor.add_stage_timing(func.__name__, duration_ms)
                return result
            except Exception as e:
                monitor.set_error_rate(1, 1)
                raise
    return wrapper
