import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Create metrics directory if it doesn't exist
os.makedirs("visualizations", exist_ok=True)


def create_performance_visualization(case_data, case_name):
    """Create performance visualization for a given case data."""
    # Create a 2x2 grid of plots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16), dpi=300)
    fig.suptitle(f"{case_name} Analysis", fontsize=36, y=0.98)

    # Top Left: Total Requests
    ax1.bar(case_data["endpoint"].tolist(), case_data["requests"], color="skyblue")
    ax1.set_title("Total Requests", fontsize=28, pad=15)
    ax1.set_ylabel("Count", fontsize=24)
    ax1.set_xticks(range(len(case_data["endpoint"])))
    ax1.set_xticklabels(case_data["endpoint"].tolist(), rotation=45, ha="right", fontsize=20)
    for i, v in enumerate(case_data["requests"]):
        ax1.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=20)

    # Top Right: Response Time Heatmap
    metrics_for_heatmap = case_data[["median", "average", "95%ile", "99%ile", "min", "max"]]
    sns.heatmap(
        metrics_for_heatmap,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        xticklabels=["Median", "Average", "95%", "99%", "Min", "Max"],
        yticklabels=case_data["endpoint"].tolist(),
        ax=ax2,
        annot_kws={"size": 20},
    )
    ax2.set_title("Response Time Distribution (ms)", fontsize=28, pad=15)
    ax2.tick_params(axis="both", which="major", labelsize=20)

    # Bottom Left: Total Failures
    ax3.bar(case_data["endpoint"].tolist(), case_data["failures"], color="salmon")
    ax3.set_title("Total Failures", fontsize=28, pad=15)
    ax3.set_ylabel("Count", fontsize=24)
    ax3.set_xticks(range(len(case_data["endpoint"])))
    ax3.set_xticklabels(case_data["endpoint"].tolist(), rotation=45, ha="right", fontsize=20)
    for i, v in enumerate(case_data["failures"]):
        ax3.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=20)

    # Bottom Right: RPS
    ax4.bar(case_data["endpoint"].tolist(), case_data["RPS"], color="lightgreen")
    ax4.set_title("Requests Per Second", fontsize=28, pad=15)
    ax4.set_ylabel("RPS", fontsize=24)
    ax4.set_xticks(range(len(case_data["endpoint"])))
    ax4.set_xticklabels(case_data["endpoint"].tolist(), rotation=45, ha="right", fontsize=20)
    for i, v in enumerate(case_data["RPS"]):
        ax4.text(i, v, f"{v:.1f}", ha="center", va="bottom", fontsize=20)

    plt.tight_layout()
    plt.savefig(f"visualizations/{case_name.lower()}_analysis.png", dpi=300, bbox_inches="tight")
    plt.close()


# Case 1 Data
case1_data = {
    "endpoint": [
        "GET/100",
        "POST/",
        "GET/1",
        "PUT/*",
        "Aggr.",
    ],
    "requests": [6513, 1669, 4984, 3270, 16436],
    "failures": [1, 0, 2, 1, 4],
    "median": [12, 28, 18, 29, 18],
    "95%ile": [40, 61, 48, 85, 55],
    "99%ile": [58, 89, 70, 140, 85],
    "average": [15.55, 31.38, 21.84, 36.89, 23.34],
    "min": [2, 17, 1, 3, 1],
    "max": [160, 202, 167, 279, 279],
    "RPS": [33.6, 8.0, 31.6, 19.3, 92.5],
    "Failures/s": [0, 0, 0.1, 0, 0.1],
}

# Convert to DataFrame
case1_data = pd.DataFrame(case1_data)

# Create visualization for Case 1
create_performance_visualization(case1_data, "Case1")

# Case2 Analysis
case2_data = {
    "endpoint": [
        "GET/100",
        "POST/1",
        "GET/1",
        "PUT/*",
        "Aggr.",
    ],
    "requests": [966, 232, 789, 427, 2414],
    "failures": [4, 1, 1, 89, 95],
    "median": [2300, 15000, 1900, 13000, 2700],
    "95%ile": [5100, 31000, 4700, 30000, 23000],
    "99%ile": [7400, 38000, 6700, 36000, 33000],
    "average": [2469.06, 15774.84, 2117.8, 14454.87, 5728.82],
    "min": [43, 39, 61, 49, 39],
    "max": [9185, 40662, 10244, 43350, 43350],
    "RPS": [3.4, 1.5, 2.5, 1.5, 8.9],
    "Failures/s": [0, 0, 0, 0.4, 0.4],
}
case2_data = pd.DataFrame(case2_data)
create_performance_visualization(case2_data, "Case2")


# Case3 Analysis
case3_data = {
    "endpoint": [
        "GET/100",
        "POST/1",
        "GET/1",
        "PUT/*",
        "Aggr.",
    ],
    "requests": [5048, 1295, 3773, 2602, 12718],
    "failures": [5, 3, 2, 0, 10],
    "median": [270, 400, 200, 380, 280],
    "95%ile": [680, 1100, 610, 1100, 820],
    "99%ile": [830, 1500, 780, 1400, 1200],
    "average": [308.13, 468.75, 250.44, 456.38, 337.86],
    "min": [2, 1, 1, 58, 1],
    "max": [1447, 2051, 1497, 2350, 2350],
    "RPS": [29.3, 6.7, 23.2, 15.2, 74.4],
    "Failures/s": [0, 0, 0, 0, 0],
}
case3_data = pd.DataFrame(case3_data)
create_performance_visualization(case3_data, "Case3")


# Case4 Analysis
case4_data = {
    "endpoint": [
        "GET/100",
        "POST/1",
        "GET/1",
        "PUT/*",
        "Aggr.",
    ],
    "requests": [5798, 1422, 4358, 2918, 14496],
    "failures": [0, 1, 6, 2, 9],
    "median": [150, 160, 86, 160, 130],
    "95%ile": [410, 600, 320, 580, 440],
    "99%ile": [600, 830, 500, 830, 690],
    "average": [177.25, 222.84, 120.93, 217.75, 173.07],
    "min": [52, 1, 2, 1, 1],
    "max": [999, 1182, 914, 1181, 1182],
    "RPS": [32.5, 8.5, 24.6, 16.2, 81.8],
    "Failures/s": [0, 0, 0, 0, 0],
}
case4_data = pd.DataFrame(case4_data)
create_performance_visualization(case4_data, "Case4")
