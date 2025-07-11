# 📊 Citadel AI Program Timeline Visualizations

This document provides Python code to generate visual timeline charts for the Citadel AI Infrastructure deployment program. The visualizations include both high-level phase overviews and detailed project breakdowns.

## 📋 Overview

The Citadel AI Program consists of 4 main phases spanning 16 weeks:

- **Phase 1**: Infrastructure Foundation (Weeks 1-4)
- **Phase 2**: Service Expansion (Weeks 5-8)
- **Phase 3**: Operations & Quality (Weeks 9-12)
- **Phase 4**: Integration & Validation (Weeks 13-16)

## 🛠️ Prerequisites

Install required Python packages:

```bash
pip install pandas matplotlib
```

## 📈 Phase Overview Gantt Chart

This chart shows the high-level program phases and their timelines.

```python
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta

# Define the phases and their durations
phases = [
    {"Phase": "Phase 1: Infrastructure Foundation", "Start": "2025-07-14", "End": "2025-08-08"},
    {"Phase": "Phase 2: Service Expansion", "Start": "2025-08-11", "End": "2025-09-05"},
    {"Phase": "Phase 3: Operations & Quality", "Start": "2025-09-08", "End": "2025-10-03"},
    {"Phase": "Phase 4: Integration & Validation", "Start": "2025-10-06", "End": "2025-10-31"}
]

# Create DataFrame
df = pd.DataFrame(phases)
df["Start"] = pd.to_datetime(df["Start"])
df["End"] = pd.to_datetime(df["End"])
df["Duration"] = df["End"] - df["Start"]

# Plot Gantt chart
fig, ax = plt.subplots(figsize=(12, 6))

# Color scheme for phases
phase_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']

for i, row in df.iterrows():
    ax.barh(row["Phase"], row["Duration"].days, left=row["Start"], 
            height=0.5, color=phase_colors[i], alpha=0.7,
            label=f'Duration: {row["Duration"].days} days')

# Format x-axis
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=7))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.xticks(rotation=45)

# Labels and layout
ax.set_title("Citadel AI Program Timeline - Phase Overview", fontsize=16, fontweight='bold')
ax.set_xlabel("Timeline", fontsize=12)
ax.set_ylabel("Phases", fontsize=12)

# Add duration annotations
for i, row in df.iterrows():
    duration_text = f"{row['Duration'].days} days"
    ax.text(row['Start'] + row['Duration']/2, i, duration_text, 
            ha='center', va='center', fontweight='bold', color='white')

plt.tight_layout()
plt.grid(axis='x', alpha=0.3)
plt.show()
```

## 📊 Detailed Project Timeline

This chart provides a detailed breakdown of all 10 projects with resource categorization and color coding.

```python
# Define projects with corresponding phases, dates, and resource labels
projects = [
    {"Project": "Project 1: SQL DB Server", "Start": "2025-07-14", "End": "2025-07-25", "Resource": "Data Infra"},
    {"Project": "Project 2: Vector DB Server", "Start": "2025-07-14", "End": "2025-08-01", "Resource": "Data Infra"},
    {"Project": "Project 3: Primary LLM Server", "Start": "2025-07-21", "End": "2025-08-08", "Resource": "AI Core"},
    {"Project": "Project 4: Secondary LLM Server", "Start": "2025-08-11", "End": "2025-08-22", "Resource": "AI Core"},
    {"Project": "Project 5: Orchestration Server", "Start": "2025-08-11", "End": "2025-08-29", "Resource": "Workflow"},
    {"Project": "Project 6: Development Server", "Start": "2025-08-18", "End": "2025-09-05", "Resource": "Dev Tools"},
    {"Project": "Project 7: Test Server", "Start": "2025-09-08", "End": "2025-09-19", "Resource": "QA"},
    {"Project": "Project 8: Metrics Server", "Start": "2025-09-08", "End": "2025-09-26", "Resource": "Monitoring"},
    {"Project": "Project 9: DevOps Server", "Start": "2025-09-15", "End": "2025-10-03", "Resource": "Ops"},
    {"Project": "Project 10: System Integration", "Start": "2025-10-06", "End": "2025-10-31", "Resource": "System Integration"}
]

# Create DataFrame
proj_df = pd.DataFrame(projects)
proj_df["Start"] = pd.to_datetime(proj_df["Start"])
proj_df["End"] = pd.to_datetime(proj_df["End"])
proj_df["Duration"] = proj_df["End"] - proj_df["Start"]

# Assign colors based on resource types
resource_colors = {
    "Data Infra": "#1f77b4",      # Blue
    "AI Core": "#ff7f0e",         # Orange
    "Workflow": "#2ca02c",        # Green
    "Dev Tools": "#d62728",       # Red
    "QA": "#9467bd",              # Purple
    "Monitoring": "#8c564b",      # Brown
    "Ops": "#e377c2",             # Pink
    "System Integration": "#7f7f7f"  # Gray
}

# Plot detailed project timeline
fig, ax = plt.subplots(figsize=(16, 10))

# Create bars for each project
bars = []
for i, row in proj_df.iterrows():
    bar = ax.barh(row["Project"], row["Duration"].days, left=row["Start"],
                  height=0.6, color=resource_colors[row["Resource"]], 
                  alpha=0.8, edgecolor='black', linewidth=0.5)
    bars.append(bar)

# Milestone marker lines for each phase end
milestones = [
    {"date": "2025-08-08", "label": "Phase 1 Complete"},
    {"date": "2025-09-05", "label": "Phase 2 Complete"},
    {"date": "2025-10-03", "label": "Phase 3 Complete"},
    {"date": "2025-10-31", "label": "Phase 4 Complete"}
]

for milestone in milestones:
    ax.axvline(pd.to_datetime(milestone["date"]), color='red', 
               linestyle='--', linewidth=2, alpha=0.7)
    # Add milestone labels
    ax.text(pd.to_datetime(milestone["date"]), len(projects), milestone["label"], 
            rotation=90, ha='right', va='bottom', fontweight='bold', color='red')

# Formatting
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=7))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
plt.xticks(rotation=45)

# Title and labels
ax.set_title("Citadel AI Deployment Timeline - Detailed Project Breakdown", 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel("Timeline", fontsize=12)
ax.set_ylabel("Projects", fontsize=12)

# Create legend for resource types
legend_elements = []
for resource, color in resource_colors.items():
    from matplotlib.patches import Patch
    legend_elements.append(Patch(facecolor=color, label=resource))

ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1),
          title="Resource Categories", title_fontsize=12, fontsize=10)

# Add duration annotations on bars
for i, row in proj_df.iterrows():
    duration_text = f"{row['Duration'].days}d"
    ax.text(row['Start'] + row['Duration']/2, i, duration_text, 
            ha='center', va='center', fontweight='bold', color='white', fontsize=9)

plt.tight_layout()
plt.grid(axis='x', alpha=0.3)
plt.subplots_adjust(right=0.85)  # Make room for legend
plt.show()
```

## 📋 Resource Category Definitions

| Resource Type | Description | Projects |
|---------------|-------------|----------|
| **Data Infra** | Database and data storage infrastructure | SQL DB, Vector DB |
| **AI Core** | AI model serving and inference engines | Primary LLM, Secondary LLM |
| **Workflow** | Task orchestration and routing systems | Orchestration Server |
| **Dev Tools** | Development environment and multimodal AI | Development Server |
| **QA** | Testing and quality assurance infrastructure | Test Server |
| **Monitoring** | Observability and metrics collection | Metrics Server |
| **Ops** | Operations management and automation | DevOps Server |
| **System Integration** | End-to-end system integration | System Integration |

## 🎯 Key Milestones

- **Week 4 (Aug 8)**: Core data services and primary AI inference operational
- **Week 8 (Sep 5)**: Complete AI portfolio and multimodal development enabled  
- **Week 12 (Oct 3)**: CI/CD, observability, and operations infrastructure active
- **Week 16 (Oct 31)**: Fully integrated Citadel AI Operating System deployed

## 📝 Usage Instructions

1. Copy the code blocks into separate Python files or Jupyter notebook cells
2. Run the phase overview chart first to see high-level timeline
3. Run the detailed project timeline to see resource allocation and dependencies
4. Use the milestone markers to track progress against planned delivery dates
