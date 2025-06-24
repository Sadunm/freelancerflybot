#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resource Monitor Module
--------------------
Monitors system resources to prevent overloading.
"""

import os
import time
import logging
import threading
import psutil
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitors system resources to prevent overloading."""
    
    def __init__(self, threshold_cpu: float = 85.0, threshold_ram: float = 80.0, 
                 check_interval: int = 60, callback: Optional[Callable] = None):
        """
        Initialize resource monitor.
        
        Args:
            threshold_cpu: CPU usage threshold percentage
            threshold_ram: RAM usage threshold percentage
            check_interval: Check interval in seconds
            callback: Callback function to call when thresholds are exceeded
        """
        self.threshold_cpu = threshold_cpu
        self.threshold_ram = threshold_ram
        self.check_interval = check_interval
        self.callback = callback
        
        self.running = False
        self.thread = None
        
        self.last_check = {
            "timestamp": 0,
            "cpu_percent": 0,
            "ram_percent": 0,
            "overloaded": False
        }
        
        logger.info(f"Initialized resource monitor (CPU: {threshold_cpu}%, RAM: {threshold_ram}%, interval: {check_interval}s)")
    
    def start(self):
        """Start resource monitoring."""
        if self.running:
            logger.warning("Resource monitor already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
        logger.info("Started resource monitoring")
    
    def stop(self):
        """Stop resource monitoring."""
        if not self.running:
            logger.warning("Resource monitor not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
            self.thread = None
        
        logger.info("Stopped resource monitoring")
    
    def _monitor_loop(self):
        """Resource monitoring loop."""
        while self.running:
            try:
                # Check resources
                self._check_resources()
                
                # Sleep until next check
                time.sleep(self.check_interval)
            
            except Exception as e:
                logger.error(f"Error in resource monitor: {str(e)}")
                time.sleep(self.check_interval)
    
    def _check_resources(self):
        """Check system resources."""
        try:
            # Get CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Get RAM usage
            ram_percent = psutil.virtual_memory().percent
            
            # Check if thresholds are exceeded
            cpu_overloaded = cpu_percent > self.threshold_cpu
            ram_overloaded = ram_percent > self.threshold_ram
            overloaded = cpu_overloaded or ram_overloaded
            
            # Update last check
            self.last_check = {
                "timestamp": time.time(),
                "cpu_percent": cpu_percent,
                "ram_percent": ram_percent,
                "overloaded": overloaded
            }
            
            # Log resource usage
            if overloaded:
                logger.warning(f"System resources overloaded: CPU: {cpu_percent:.1f}% (threshold: {self.threshold_cpu}%), RAM: {ram_percent:.1f}% (threshold: {self.threshold_ram}%)")
            else:
                logger.debug(f"System resources: CPU: {cpu_percent:.1f}%, RAM: {ram_percent:.1f}%")
            
            # Call callback if thresholds are exceeded
            if overloaded and self.callback:
                self.callback(cpu_percent, ram_percent)
        
        except Exception as e:
            logger.error(f"Error checking resources: {str(e)}")
    
    def is_overloaded(self) -> bool:
        """
        Check if system resources are overloaded.
        
        Returns:
            bool: True if resources are overloaded, False otherwise
        """
        # Check if last check is recent enough
        if time.time() - self.last_check["timestamp"] > self.check_interval * 2:
            # Perform a new check if last check is too old
            self._check_resources()
        
        return self.last_check["overloaded"]
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """
        Get current resource usage.
        
        Returns:
            Dict[str, Any]: Resource usage information
        """
        # Check if last check is recent enough
        if time.time() - self.last_check["timestamp"] > self.check_interval * 2:
            # Perform a new check if last check is too old
            self._check_resources()
        
        return {
            "timestamp": self.last_check["timestamp"],
            "cpu_percent": self.last_check["cpu_percent"],
            "ram_percent": self.last_check["ram_percent"],
            "overloaded": self.last_check["overloaded"],
            "threshold_cpu": self.threshold_cpu,
            "threshold_ram": self.threshold_ram
        }
    
    def get_detailed_resource_info(self) -> Dict[str, Any]:
        """
        Get detailed resource information.
        
        Returns:
            Dict[str, Any]: Detailed resource information
        """
        try:
            # Get CPU info
            cpu_count = psutil.cpu_count(logical=True)
            cpu_physical_count = psutil.cpu_count(logical=False)
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            # Get memory info
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            # Get disk info
            disk_usage = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disk_usage[partition.mountpoint] = {
                        "total": usage.total,
                        "used": usage.used,
                        "free": usage.free,
                        "percent": usage.percent
                    }
                except Exception:
                    pass
            
            # Get network info
            net_io = psutil.net_io_counters()
            
            # Get process info
            process_count = len(psutil.pids())
            
            # Get current process info
            current_process = psutil.Process(os.getpid())
            current_process_info = {
                "pid": current_process.pid,
                "name": current_process.name(),
                "cpu_percent": current_process.cpu_percent(interval=1),
                "memory_percent": current_process.memory_percent(),
                "memory_info": {
                    "rss": current_process.memory_info().rss,
                    "vms": current_process.memory_info().vms
                },
                "threads": len(current_process.threads()),
                "create_time": current_process.create_time()
            }
            
            # Compile detailed info
            detailed_info = {
                "timestamp": time.time(),
                "cpu": {
                    "count": cpu_count,
                    "physical_count": cpu_physical_count,
                    "percent": cpu_percent,
                    "average_percent": sum(cpu_percent) / len(cpu_percent) if cpu_percent else 0,
                    "freq": {
                        "current": cpu_freq.current if cpu_freq else None,
                        "min": cpu_freq.min if cpu_freq else None,
                        "max": cpu_freq.max if cpu_freq else None
                    }
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent,
                    "swap": {
                        "total": swap.total,
                        "used": swap.used,
                        "free": swap.free,
                        "percent": swap.percent
                    }
                },
                "disk": disk_usage,
                "network": {
                    "bytes_sent": net_io.bytes_sent,
                    "bytes_recv": net_io.bytes_recv,
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout
                },
                "process": {
                    "count": process_count,
                    "current": current_process_info
                }
            }
            
            return detailed_info
        
        except Exception as e:
            logger.error(f"Error getting detailed resource info: {str(e)}")
            return {
                "error": str(e)
            }
    
    def set_thresholds(self, threshold_cpu: Optional[float] = None, threshold_ram: Optional[float] = None):
        """
        Set resource thresholds.
        
        Args:
            threshold_cpu: CPU usage threshold percentage
            threshold_ram: RAM usage threshold percentage
        """
        if threshold_cpu is not None:
            self.threshold_cpu = threshold_cpu
        
        if threshold_ram is not None:
            self.threshold_ram = threshold_ram
        
        logger.info(f"Updated resource thresholds (CPU: {self.threshold_cpu}%, RAM: {self.threshold_ram}%)")
    
    def set_check_interval(self, check_interval: int):
        """
        Set check interval.
        
        Args:
            check_interval: Check interval in seconds
        """
        self.check_interval = check_interval
        logger.info(f"Updated check interval: {check_interval}s")