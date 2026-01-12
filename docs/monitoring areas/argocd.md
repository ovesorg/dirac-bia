# 🚀 Argo CD – GitOps Deployment & Operations Guide

## Overview

**Argo CD** is a **GitOps continuous delivery tool for Kubernetes**.  
It ensures that the state of applications running in the cluster always matches the **desired state defined in Git repositories**.

In our setup, Argo CD is the **single source of truth** for:
- Application deployments
- Environment consistency (dev, staging, prod)
- Rollbacks and drift detection
- Operational visibility of microservices

---

## What Argo CD Is Used For

Argo CD is used to:

- Deploy Kubernetes applications declaratively
- Sync Helm charts and manifests from GitHub
- Detect configuration drift
- Provide visibility into application health
- Enable safe rollbacks via Git
- Enforce GitOps best practices


## Core Argo CD Architecture

Argo CD consists of several components running inside Kubernetes:

| Component | Purpose |
|--------|--------|
| **argocd-server** | Web UI, API, authentication |
| **argocd-application-controller** | Reconciles desired vs live state |
| **argocd-repo-server** | Fetches Git repositories and renders manifests |
| **argocd-notifications-controller** | Sends alerts (Slack, email, webhooks) |
| **argocd-dex-server** | Identity provider (SSO integration) |

---

## GitOps Workflow (How It Works)

### 1. Desired State in Git
- Applications are defined in Git (Helm charts / YAML)
- Example repo: https://github.com/ovesorg/deployment-charts


### 2. Argo CD Watches Git
- Continuously monitors branches (e.g. `dev`)
- Detects any change in manifests or values

### 3. Manifest Rendering
- `argocd-repo-server`:
- Pulls the repository
- Renders Helm charts
- Produces final Kubernetes manifests

### 4. State Comparison
- `argocd-application-controller`:
- Compares **desired state (Git)** vs **live state (cluster)**
- Detects drift automatically

### 5. Sync & Reconciliation
- If Auto-Sync is enabled → Argo CD applies changes
- If Manual → user clicks **SYNC**
- Kubernetes resources are created, updated, or pruned

---

## Argo CD Applications View 

### Applications Tiles View

Each tile represents **one application** deployed via Argo CD.

Displayed information includes:

- **Application name**
- **Project** (usually `default`)
- **Git repository**
- **Target revision** (e.g. `dev`)
- **Path** inside the repo
- **Destination cluster**
- **Namespace**
- **Sync status**
- **Health status**
- **Last sync time**

---

## Application Status Indicators

### Sync Status

| Status | Meaning |
|-----|-------|
| **Synced** | Live state matches Git |
| **OutOfSync** | Drift detected |
| **Unknown** | Sync status not determined |

### Health Status

| Status | Meaning |
|------|--------|
| **Healthy** | All resources running normally |
| **Progressing** | Deployment in progress |
| **Degraded** | Pods failing or unhealthy |
| **Suspended** | Application paused |
| **Missing** | Resources missing in cluster |

---

## Typical Applications in Our Cluster

Argo CD manages:

- Infrastructure services:
- `grafana`
- `influxdb`
- `emqx`, `emqx-ce`
- `ha-proxy-ingress`
- Platform services:
- `api-gateway`
- `auth-microservice`
- `account-microservice`
- `event-microservice`
- Applications & dashboards:
- `aas-dashboard`
- `abs-platform`
- `ble-app`
- `cms-content-editor`

All are deployed **from the same Git repository** but different paths.

---

## Sync Operations

Each application tile provides actions:

### 🔄 Sync
- Applies Git state to the cluster
- Creates, updates, or deletes resources

### 🔁 Refresh
- Re-evaluates Git and cluster state
- No changes applied

### ❌ Delete
- Removes the application from Argo CD
- Can optionally prune Kubernetes resources

---

## How to View Application Logs

### 1. From Argo CD UI (High-Level)

Argo CD itself does **not show application container logs**, but it shows:
- Sync errors
- Resource status
- Kubernetes events
- Manifest diffs

To see logs:
1. Click an application
2. Open a resource (Pod, Deployment)
3. Inspect events and sync output

---

### 2. Viewing Argo CD System Logs (Recommended)

To troubleshoot Argo CD itself:

```bash
kubectl logs -n argocd deployment/argocd-server
kubectl logs -n argocd deployment/argocd-application-controller
kubectl logs -n argocd deployment/argocd-repo-server
kubectl logs -n argocd deployment/argocd-notifications-controller
