"""
ER Diagram Generator (3NF)
Generates a visual Entity-Relationship diagram for the traffic management database.
Uses matplotlib to produce a professional diagram.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "er_diagram.png")


def draw_entity(ax, x, y, name, attributes, pk_attrs, fk_attrs=None, color="#2563eb"):
    """Draw a single entity box with attributes."""
    if fk_attrs is None:
        fk_attrs = []

    width = 2.8
    header_height = 0.45
    attr_height = 0.32
    total_height = header_height + len(attributes) * attr_height + 0.15

    # Entity box
    rect = mpatches.FancyBboxPatch(
        (x - width / 2, y - total_height),
        width, total_height,
        boxstyle="round,pad=0.1",
        facecolor="#0f172a",
        edgecolor=color,
        linewidth=2.5
    )
    ax.add_patch(rect)

    # Header background
    header_rect = mpatches.FancyBboxPatch(
        (x - width / 2 + 0.05, y - header_height - 0.05),
        width - 0.1, header_height,
        boxstyle="round,pad=0.05",
        facecolor=color,
        edgecolor="none",
        alpha=0.9
    )
    ax.add_patch(header_rect)

    # Entity name
    ax.text(x, y - header_height / 2 - 0.05, name,
            ha="center", va="center",
            fontsize=12, fontweight="bold", color="white",
            fontfamily="monospace")

    # Attributes
    for i, attr in enumerate(attributes):
        ay = y - header_height - 0.2 - i * attr_height

        # Prefix for PK/FK
        if attr in pk_attrs:
            prefix = "PK  "
            fw = "bold"
            acolor = "#fbbf24"
        elif attr in fk_attrs:
            prefix = "FK  "
            fw = "normal"
            acolor = "#38bdf8"
        else:
            prefix = "    "
            fw = "normal"
            acolor = "#cbd5e1"

        ax.text(x - width / 2 + 0.2, ay, f"{prefix}{attr}",
                ha="left", va="center",
                fontsize=9, fontweight=fw, color=acolor,
                fontfamily="monospace")

    return (x, y - total_height)


def draw_relationship_line(ax, start, end, label, start_card, end_card):
    """Draw a relationship line between two entities."""
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(
                    arrowstyle="-",
                    color="#475569",
                    lw=1.8,
                    connectionstyle="arc3,rad=0.05"
                ))

    # Label at midpoint
    mx = (start[0] + end[0]) / 2
    my = (start[1] + end[1]) / 2
    ax.text(mx, my + 0.15, label,
            ha="center", va="center",
            fontsize=8, color="#94a3b8",
            fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.2", facecolor="#0f172a", edgecolor="#334155"))

    # Cardinality
    ax.text(start[0] + (end[0] - start[0]) * 0.15,
            start[1] + (end[1] - start[1]) * 0.15 - 0.18,
            start_card, ha="center", fontsize=8, color="#f97316")
    ax.text(end[0] - (end[0] - start[0]) * 0.15,
            end[1] - (end[1] - start[1]) * 0.15 + 0.18,
            end_card, ha="center", fontsize=8, color="#f97316")


def generate_er_diagram():
    """Main function to generate the ER diagram."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    fig.patch.set_facecolor("#0a0e1a")
    ax.set_facecolor("#0a0e1a")

    # ─── Entity: Junction ───
    draw_entity(ax, 3, 9, "JUNCTION", [
        "junction_id INT PK",
        "name VARCHAR(100)",
        "latitude DECIMAL(10,6)",
        "longitude DECIMAL(10,6)",
        "num_approaches INT",
        "zone VARCHAR(50)"
    ], pk_attrs=["junction_id INT PK"], color="#8b5cf6")

    # ─── Entity: Sensor ───
    draw_entity(ax, 8, 9, "SENSOR", [
        "sensor_id INT PK",
        "junction_id INT FK",
        "sensor_type VARCHAR(30)",
        "installation_date DATE",
        "status VARCHAR(20)",
        "accuracy_pct DECIMAL(5,2)"
    ], pk_attrs=["sensor_id INT PK"],
       fk_attrs=["junction_id INT FK"], color="#0ea5e9")

    # ─── Entity: TrafficReading ───
    draw_entity(ax, 13, 9, "TRAFFIC_READING", [
        "reading_id BIGINT PK",
        "sensor_id INT FK",
        "timestamp DATETIME",
        "vehicle_count INT",
        "avg_speed DECIMAL(5,1)",
        "occupancy_pct DECIMAL(5,2)",
        "weather_id INT FK"
    ], pk_attrs=["reading_id BIGINT PK"],
       fk_attrs=["sensor_id INT FK", "weather_id INT FK"], color="#10b981")

    # ─── Entity: WeatherCondition ───
    draw_entity(ax, 13, 4.5, "WEATHER_CONDITION", [
        "weather_id INT PK",
        "condition VARCHAR(30)",
        "temperature DECIMAL(4,1)",
        "humidity_pct DECIMAL(5,2)",
        "rain_mm DECIMAL(5,1)",
        "visibility_km DECIMAL(4,1)"
    ], pk_attrs=["weather_id INT PK"], color="#f59e0b")

    # ─── Relationships ───
    # Junction → Sensor (1:N)
    draw_relationship_line(ax,
        (4.4, 7.5), (6.6, 7.5),
        "has", "1", "N")

    # Sensor → TrafficReading (1:N)
    draw_relationship_line(ax,
        (9.4, 7.5), (11.6, 7.5),
        "records", "1", "N")

    # WeatherCondition → TrafficReading (1:N)
    draw_relationship_line(ax,
        (13, 4.5), (13, 6.3),
        "during", "1", "N")

    # Title
    ax.text(8, 10, "Traffic Management System — ER Diagram (3NF)",
            ha="center", va="center",
            fontsize=18, fontweight="bold", color="white",
            fontfamily="sans-serif")

    ax.text(8, 9.6, "Third Normal Form • No transitive dependencies • Indexed for time-series queries",
            ha="center", va="center",
            fontsize=10, color="#64748b",
            fontfamily="sans-serif")

    # Legend
    legend_y = 2.8
    ax.text(3, legend_y, "Legend:", fontsize=10, fontweight="bold", color="#e2e8f0")
    ax.text(3, legend_y - 0.4, "🔑  Primary Key", fontsize=9, color="#fbbf24", fontfamily="monospace")
    ax.text(3, legend_y - 0.8, "🔗  Foreign Key", fontsize=9, color="#38bdf8", fontfamily="monospace")
    ax.text(3, legend_y - 1.2, "1 ─── N  One-to-Many", fontsize=9, color="#f97316", fontfamily="monospace")

    # 3NF Explanation
    ax.text(7, legend_y, "3NF Justification:", fontsize=10, fontweight="bold", color="#e2e8f0")
    explanations = [
        "• 1NF: All columns have atomic values, no repeating groups",
        "• 2NF: No partial dependencies (all non-key attrs depend on full PK)",
        "• 3NF: No transitive dependencies (weather separated from readings)"
    ]
    for i, exp in enumerate(explanations):
        ax.text(7, legend_y - 0.4 - i * 0.4, exp, fontsize=8.5, color="#94a3b8")

    ax.set_xlim(0.5, 15.5)
    ax.set_ylim(1, 10.5)
    ax.axis("off")

    plt.tight_layout()
    plt.savefig(OUTPUT_FILE, dpi=200, bbox_inches="tight",
                facecolor="#0a0e1a", edgecolor="none")
    plt.close()

    print(f"✅ ER Diagram saved to: {OUTPUT_FILE}")
    print("   Tables: Junction, Sensor, TrafficReading, WeatherCondition")
    print("   Normal form: 3NF")


if __name__ == "__main__":
    generate_er_diagram()
