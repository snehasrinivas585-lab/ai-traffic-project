# Data Source Classification for AI Traffic Management

## Overview

Traffic management systems rely on two fundamental categories of data: **Static** (infrastructure-level, rarely changing) and **Dynamic** (real-time, continuously streaming). This document classifies all relevant data sources.

---

## 1. Static Data Sources

Static data describes the physical road network and regulatory rules. It changes infrequently (monthly or on infrastructure updates).

| Data Source | Description | Format | Update Frequency |
|-------------|-------------|--------|-----------------|
| **Road Network Maps** | Topology of roads, intersections, lanes, turn restrictions | GeoJSON, Shapefiles, OSM XML | Quarterly |
| **Lane Configurations** | Number of lanes, dedicated bus/cycle lanes, turn lanes | Structured DB tables | On infrastructure change |
| **Speed Limits** | Posted speed limits per road segment | Key-value per segment | On regulation change |
| **Signal Placement** | GPS coordinates of all traffic signals | Lat/Long database | On new installation |
| **Intersection Geometry** | Number of approaches, pedestrian crossings, island positions | CAD / GeoJSON | On reconstruction |
| **Land Use Zones** | Residential, commercial, industrial, school zones | Zoning shapefiles | Annual review |
| **Public Transit Routes** | Bus routes, stop locations, scheduled frequencies | GTFS feed | Seasonal |

### Characteristics
- ✅ Highly reliable and accurate
- ✅ Easy to store and query
- ❌ Cannot capture real-time conditions
- ❌ May be outdated if not maintained

---

## 2. Dynamic Data Sources

Dynamic data captures real-time traffic conditions. It streams continuously and must be processed with minimal latency.

| Data Source | Description | Technology | Latency | Accuracy |
|-------------|-------------|-----------|---------|----------|
| **Inductive Loop Detectors** | Embedded in road surface; detect vehicle presence via electromagnetic field change | Copper wire loops | <1 sec | High (95%+) |
| **CCTV / Video Analytics** | Camera feeds processed by CV models to count vehicles, detect incidents | IP Cameras + YOLO/SSD | 2–5 sec | Moderate-High (85–92%) |
| **GPS Probe Data** | Anonymized location pings from ride-hailing apps (Ola, Uber) and fleet vehicles | GPS + cellular | 5–30 sec | High for speed estimation |
| **Radar / Microwave Sensors** | Overhead sensors measuring vehicle speed and count | Doppler radar | <1 sec | High (93%+) |
| **Infrared Sensors** | Detect vehicle presence via heat signatures | Passive IR | <1 sec | Moderate (80–88%) |
| **Bluetooth / Wi-Fi Scanners** | Detect MAC addresses to estimate travel time between two points | BT/Wi-Fi receivers | 10–60 sec | Moderate (needs filtering) |
| **Connected Vehicle Data (V2I)** | Vehicles broadcast speed, position, intent (future) | DSRC / C-V2X | <100 ms | Very High |
| **Weather APIs** | Temperature, rainfall, visibility affecting traffic flow | REST API (IMD, OpenWeather) | 5–15 min | High |
| **Social Media / Incident Reports** | Twitter/X alerts, Google Maps incident reports | NLP on text streams | Minutes | Low-Moderate |

### Characteristics
- ✅ Captures real-time conditions
- ✅ Enables adaptive and predictive control
- ❌ Requires robust infrastructure (network, power)
- ❌ Privacy concerns with GPS/Bluetooth data
- ❌ Variable accuracy across technologies

---

## 3. Data Integration Strategy

```
┌─────────────────────────────────────────────────┐
│                  DATA FUSION LAYER              │
├────────────────────┬────────────────────────────┤
│   STATIC LAYER     │     DYNAMIC LAYER          │
│                    │                            │
│  Road Network ──┐  │  Loop Detectors ──┐       │
│  Lane Config  ──┤  │  CCTV Analytics ──┤       │
│  Speed Limits ──┤  │  GPS Probes ──────┤       │
│  Signal Pos.  ──┤  │  Radar Sensors ───┤       │
│  Land Use     ──┘  │  Weather APIs ────┘       │
│        │           │       │                    │
│        ▼           │       ▼                    │
│   Graph DB /       │  Time-Series DB /          │
│   Spatial DB       │  Stream Processing         │
│        │           │       │                    │
│        └─────┬─────┘───────┘                    │
│              ▼                                  │
│    UNIFIED TRAFFIC STATE                        │
│    (per intersection, per time-step)            │
└─────────────────────────────────────────────────┘
```

---

## 4. Data Sources Used in This Project

For our simulation and ML models, we use the following **synthesized** data columns that represent what these sensors would provide:

| Column | Represents Data From | Type |
|--------|---------------------|------|
| `timestamp` | System clock | Dynamic |
| `junction_id` | Static road network | Static |
| `vehicle_count` | Inductive loops / CCTV | Dynamic |
| `avg_speed` | Radar / GPS probes | Dynamic |
| `weather` | Weather API | Dynamic |
| `day_of_week` | Calendar | Static |
| `is_holiday` | Calendar | Static |
| `hour` | System clock | Dynamic |
