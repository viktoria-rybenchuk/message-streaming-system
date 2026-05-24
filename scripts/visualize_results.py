import json
import matplotlib.pyplot as plt
from pathlib import Path

reports_dir = Path('../reports')
experiments = [
    'exp1_1prod_1part_1cons',
    'exp2_1prod_1part_2cons',
    'exp3_1prod_2part_2cons',
    'exp4_1prod_5part_5cons',
    'exp5_1prod_10part_1cons',
    'exp6_1prod_10part_5cons',
    'exp7_1prod_10part_10cons',
    'exp8_2prod_10part_10cons'
]

labels = [
    '1P-1Pa-1C',
    '1P-1Pa-2C',
    '1P-2Pa-2C',
    '1P-5Pa-5C',
    '1P-10Pa-1C',
    '1P-10Pa-5C',
    '1P-10Pa-10C',
    '2P-10Pa-10C'
]

throughputs = []
max_latencies = []
avg_latencies = []
messages_per_sec = []

for exp in experiments:
    report_file = reports_dir / f'{exp}.json'
    try:
        with open(report_file) as f:
            data = json.load(f)
            throughputs.append(data['throughput']['mbps'])
            max_latencies.append(data['latency']['max_ms'])
            avg_latencies.append(data['latency']['avg_ms'])
            messages_per_sec.append(data['messages']['per_second'])
    except FileNotFoundError:
        print(f"Warning: {report_file} not found, skipping...")
        throughputs.append(0)
        max_latencies.append(0)
        avg_latencies.append(0)
        messages_per_sec.append(0)

fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))

ax1.bar(labels, throughputs, color='steelblue')
ax1.set_xlabel('Configuration')
ax1.set_ylabel('Throughput (Mbps)')
ax1.set_title('Throughput vs Configuration')
ax1.tick_params(axis='x', rotation=45)
ax1.grid(True, alpha=0.3)

ax2.bar(labels, max_latencies, color='coral')
ax2.set_xlabel('Configuration')
ax2.set_ylabel('Max Latency (ms)')
ax2.set_title('Max Latency vs Configuration')
ax2.tick_params(axis='x', rotation=45)
ax2.grid(True, alpha=0.3)

ax3.bar(labels, avg_latencies, color='mediumseagreen')
ax3.set_xlabel('Configuration')
ax3.set_ylabel('Avg Latency (ms)')
ax3.set_title('Average Latency vs Configuration')
ax3.tick_params(axis='x', rotation=45)
ax3.grid(True, alpha=0.3)

ax4.bar(labels, messages_per_sec, color='mediumpurple')
ax4.set_xlabel('Configuration')
ax4.set_ylabel('Messages/sec')
ax4.set_title('Message Rate vs Configuration')
ax4.tick_params(axis='x', rotation=45)
ax4.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('reports/experiment_results.png', dpi=300, bbox_inches='tight')
print("Graph saved to reports/experiment_results.png")
plt.show()