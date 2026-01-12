# 📊 Monitoring & Observability Overview

## Overview

Our platform uses a **Kubernetes-native monitoring stack** built around **Grafana** and **Prometheus** to provide real-time visibility into cluster health, application performance, and resource utilization.

This monitoring setup enables:
- Early detection of performance bottlenecks
- Capacity planning and cost optimization
- Troubleshooting of application and infrastructure issues
- Visibility across namespaces, pods, and workloads

---

## Core Components

### 1. Grafana

**Grafana** is the primary visualization and observability layer.

It provides:
- Dashboards for Kubernetes, nodes, and applications
- Time-series visualization of metrics
- Filtering by cluster, namespace, pod, and workload
- Near real-time monitoring (seconds-level granularity)

Grafana connects to Prometheus as its main data source.

---

### 2. Prometheus

**Prometheus** is responsible for:
- Scraping metrics from Kubernetes components
- Storing time-series data
- Powering Grafana dashboards via PromQL queries

Prometheus collects metrics from:
- Kubernetes API
- Kubelet
- cAdvisor
- Node Exporter
- Application-level exporters (where applicable)

---

### 3. Kubernetes Metrics Sources

The monitoring stack includes standard Kubernetes exporters:

| Exporter | Purpose |
|--------|--------|
| **kube-state-metrics** | Cluster object state (pods, deployments, replicas) |
| **node-exporter** | Node-level CPU, memory, disk, network |
| **cAdvisor** | Container CPU & memory usage |
| **kubelet metrics** | Pod and container runtime metrics |

---

## Grafana Dashboard Structure

The dashboards follow the **Kubernetes Mixin** standard layout.

### Available Dashboard Categories

#### Kubernetes Dashboards
Dashboards tagged with `kubernetes-mixin`.

- Kubernetes / Compute Resources / Cluster
- Kubernetes / Compute Resources / Namespace
- Kubernetes / Compute Resources / Pod
- Kubernetes / Compute Resources / Workload
- Kubernetes / Networking (Cluster, Namespace, Pod)
- Kubernetes / Scheduler
- Kubernetes / Controller Manager
- Kubernetes / Kubelet
- Kubernetes / Proxy
- Kubernetes / Persistent Volumes

#### Node Exporter Dashboards
Dashboards tagged with `node-exporter-mixin`.

- Node Exporter / Nodes
- Node Exporter / USE Method (Node, Cluster)

#### Prometheus Dashboards
Dashboards tagged with `prometheus-mixin`.

- Prometheus / Overview
- Prometheus / Targets
- Prometheus / Performance

---

## Namespace-Level Monitoring (Pods)

Dashboard:
**Kubernetes / Compute Resources / Namespace (Pods)**

### Filters Used
- **Data source:** `default`
- **Namespace:** `argocd`
- **Time range:** Last 1 hour (UTC)

This enables focused monitoring of system components without cross-namespace noise.

---

### CPU Usage

Shows:
- CPU usage per pod over time
- Comparison against CPU requests and quotas
- Spikes, trends, and sustained usage patterns

Observed pods:
- `argocd-application-controller`
- `argocd-repo-server`
- `argocd-server`
- `argocd-notifications-controller`

**Observation:**  
CPU usage remains low and stable, indicating healthy control-plane behavior.

---

### CPU Quota

Displays:
- Current CPU usage per pod
- CPU requests and limits

Used for:
- Identifying over-allocated resources
- Tuning requests for cost efficiency
- Detecting unexpected CPU consumption

---

## Memory Monitoring

### Memory Usage (Without Cache)

Shows:
- Actual memory actively used by containers
- Cache memory excluded for accuracy

Key observations:
- `argocd-application-controller` has the highest memory usage
- Other ArgoCD components remain lightweight
- No signs of memory leaks or abnormal growth

---

### Memory Quota & RSS

Breakdown includes:
- Total memory usage
- RSS (Resident Set Size)
- Cache memory usage

This helps distinguish:
- Real memory pressure vs cache usage
- Normal growth vs leaks

---

## Why This Monitoring Matters

### Operational Reliability
- Early detection of failures
- Faster incident response
- Reduced downtime

### Cost Optimization
- Right-sizing CPU and memory
- Avoiding over-provisioning
- Improving cluster efficiency

### Scalability & Performance
- Data-driven autoscaling decisions
- Healthy control-plane monitoring
- Predictable workload behavior

---

## Best Practices

- Always filter dashboards by **namespace**
- Compare **usage vs requests**, not just raw usage
- Monitor trends over longer time windows (6–24 hours)
- Correlate CPU, memory, and restart metrics
- Investigate sustained growth patterns

---

## Summary

This monitoring system provides:
- Full Kubernetes observability
- Pod and namespace-level insights
- Reliable metrics for production operations

Grafana and Prometheus together form the backbone of our monitoring strategy, enabling proactive operations, efficient troubleshooting, and informed scaling decisions.
