#!/usr/bin/env python3
"""
Example Python chart using matplotlib - Sales Data
Generates a sample sales trend chart with multiple series
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


def generate_sales_chart():
    """Generate a sample sales trend chart"""
    
    # Get output directory from environment
    output_dir = os.getenv("CHART_OUTPUT_DIR", ".")
    chart_name = os.getenv("CHART_NAME", "example-sales")
    
    output_path = Path(output_dir) / f"{chart_name}.png"
    
    # Sample data: quarterly sales
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    product_a = [45, 52, 61, 73]
    product_b = [38, 41, 48, 55]
    product_c = [29, 35, 42, 51]
    
    x = np.arange(len(quarters))
    width = 0.25
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bars
    bars1 = ax.bar(x - width, product_a, width, label='Product A', color='#2196F3', alpha=0.8)
    bars2 = ax.bar(x, product_b, width, label='Product B', color='#4CAF50', alpha=0.8)
    bars3 = ax.bar(x + width, product_c, width, label='Product C', color='#FF9800', alpha=0.8)
    
    # Customize chart
    ax.set_xlabel('Quarter', fontsize=12, fontweight='bold')
    ax.set_ylabel('Sales (Millions USD)', fontsize=12, fontweight='bold')
    ax.set_title('Quarterly Sales by Product Line - 2024', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(quarters)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${height}M',
                   ha='center', va='bottom', fontsize=9)
    
    add_value_labels(bars1)
    add_value_labels(bars2)
    add_value_labels(bars3)
    
    plt.tight_layout()
    
    # Save the chart
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"Chart saved to: {output_path}")
    
    plt.close()


if __name__ == "__main__":
    generate_sales_chart()
