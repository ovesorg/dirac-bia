#!/usr/bin/env python3
"""
Example Python chart using matplotlib
Generates a sample performance metrics chart
"""

import os
import sys
from pathlib import Path

try:
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("Error: matplotlib and numpy are required")
    print("Install with: pip install matplotlib numpy")
    sys.exit(1)


def generate_performance_chart():
    """Generate a sample performance metrics chart"""
    
    # Get output directory from environment
    output_dir = os.getenv("CHART_OUTPUT_DIR", ".")
    chart_name = os.getenv("CHART_NAME", "example-performance")
    
    output_path = Path(output_dir) / f"{chart_name}.png"
    
    # Sample data: response times over hours
    hours = np.arange(0, 24, 1)
    response_times = 100 + 50 * np.sin(hours / 4) + np.random.normal(0, 10, 24)
    throughput = 1000 + 200 * np.cos(hours / 3) + np.random.normal(0, 50, 24)
    
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Response time chart
    ax1.plot(hours, response_times, marker='o', linewidth=2, color='#2196F3', label='Response Time')
    ax1.axhline(y=150, color='red', linestyle='--', alpha=0.7, label='SLA Threshold')
    ax1.set_xlabel('Hour of Day', fontsize=11)
    ax1.set_ylabel('Response Time (ms)', fontsize=11)
    ax1.set_title('API Response Time - 24 Hour Period', fontsize=13, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    ax1.set_xlim(0, 23)
    
    # Throughput chart
    ax2.bar(hours, throughput, color='#4CAF50', alpha=0.7, label='Requests/min')
    ax2.set_xlabel('Hour of Day', fontsize=11)
    ax2.set_ylabel('Throughput (req/min)', fontsize=11)
    ax2.set_title('API Throughput - 24 Hour Period', fontsize=13, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.legend()
    ax2.set_xlim(-0.5, 23.5)
    
    plt.tight_layout()
    
    # Save the chart
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")
    
    plt.close()


if __name__ == "__main__":
    generate_performance_chart()
