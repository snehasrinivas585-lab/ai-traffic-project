-- ============================================================
-- Traffic Management System — Database Schema (3NF)
-- SQL DDL Statements
-- ============================================================

-- ─── Table: Junction ───────────────────────────────────────
-- Stores static information about each intersection.
-- Each junction has a unique ID, geographic coordinates, and metadata.

CREATE TABLE Junction (
    junction_id     INT             PRIMARY KEY,
    name            VARCHAR(100)    NOT NULL,
    latitude        DECIMAL(10, 6)  NOT NULL,
    longitude       DECIMAL(10, 6)  NOT NULL,
    num_approaches  INT             NOT NULL DEFAULT 4,
    zone            VARCHAR(50),

    CONSTRAINT chk_latitude  CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT chk_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT chk_approaches CHECK (num_approaches BETWEEN 2 AND 8)
);

-- ─── Table: Sensor ─────────────────────────────────────────
-- Stores sensor devices installed at junctions.
-- Each sensor belongs to exactly one junction (FK → Junction).

CREATE TABLE Sensor (
    sensor_id           INT             PRIMARY KEY,
    junction_id         INT             NOT NULL,
    sensor_type         VARCHAR(30)     NOT NULL,
    installation_date   DATE,
    status              VARCHAR(20)     NOT NULL DEFAULT 'active',
    accuracy_pct        DECIMAL(5, 2),

    CONSTRAINT fk_sensor_junction
        FOREIGN KEY (junction_id) REFERENCES Junction(junction_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT chk_sensor_type
        CHECK (sensor_type IN ('inductive_loop', 'cctv', 'radar', 'infrared', 'gps_probe')),

    CONSTRAINT chk_sensor_status
        CHECK (status IN ('active', 'maintenance', 'decommissioned'))
);

CREATE INDEX idx_sensor_junction ON Sensor(junction_id);

-- ─── Table: WeatherCondition ───────────────────────────────
-- Stores distinct weather snapshots.
-- Separated from TrafficReading to achieve 3NF (no transitive dependency).

CREATE TABLE WeatherCondition (
    weather_id      INT             PRIMARY KEY,
    condition       VARCHAR(30)     NOT NULL,
    temperature     DECIMAL(4, 1),
    humidity_pct    DECIMAL(5, 2),
    rain_mm         DECIMAL(5, 1)   DEFAULT 0,
    visibility_km   DECIMAL(4, 1),

    CONSTRAINT chk_weather_condition
        CHECK (condition IN ('Clear', 'Cloudy', 'Light Rain', 'Heavy Rain', 'Fog', 'Storm')),

    CONSTRAINT chk_temperature
        CHECK (temperature BETWEEN -10 AND 55),

    CONSTRAINT chk_humidity
        CHECK (humidity_pct BETWEEN 0 AND 100)
);

-- ─── Table: TrafficReading ─────────────────────────────────
-- Stores time-series traffic measurements.
-- Each reading references a sensor (FK → Sensor) and a weather snapshot (FK → WeatherCondition).
-- This is the core fact table, optimized for time-series queries.

CREATE TABLE TrafficReading (
    reading_id      BIGINT          PRIMARY KEY AUTO_INCREMENT,
    sensor_id       INT             NOT NULL,
    timestamp       DATETIME        NOT NULL,
    vehicle_count   INT             NOT NULL,
    avg_speed       DECIMAL(5, 1),
    occupancy_pct   DECIMAL(5, 2),
    weather_id      INT,

    CONSTRAINT fk_reading_sensor
        FOREIGN KEY (sensor_id) REFERENCES Sensor(sensor_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_reading_weather
        FOREIGN KEY (weather_id) REFERENCES WeatherCondition(weather_id)
        ON DELETE SET NULL,

    CONSTRAINT chk_vehicle_count
        CHECK (vehicle_count >= 0),

    CONSTRAINT chk_avg_speed
        CHECK (avg_speed >= 0),

    CONSTRAINT chk_occupancy
        CHECK (occupancy_pct BETWEEN 0 AND 100)
);

-- ─── Indexes for Time-Series Performance ───────────────────
-- Composite index on (sensor_id, timestamp) for efficient range queries
CREATE INDEX idx_reading_sensor_time ON TrafficReading(sensor_id, timestamp);

-- Index on timestamp alone for global time-range aggregations
CREATE INDEX idx_reading_timestamp ON TrafficReading(timestamp);

-- Index on weather_id for weather-based analytics
CREATE INDEX idx_reading_weather ON TrafficReading(weather_id);


-- ============================================================
-- 3NF Verification Notes:
-- ============================================================
-- 1NF ✅ All columns are atomic (no arrays, no repeating groups)
-- 2NF ✅ No partial dependencies (each non-key attribute depends
--         on the full primary key, not a subset)
-- 3NF ✅ No transitive dependencies:
--         - Weather data is in its own table, not embedded in TrafficReading
--         - Junction info is in its own table, not embedded in Sensor
--         - Each table represents a single real-world entity
-- ============================================================


-- ─── Sample Data Inserts ───────────────────────────────────

INSERT INTO Junction (junction_id, name, latitude, longitude, num_approaches, zone) VALUES
(1, 'Silk Board Junction',   12.9170, 77.6227, 4, 'South Bengaluru'),
(2, 'Hebbal Flyover',        13.0358, 77.5970, 4, 'North Bengaluru'),
(3, 'KR Puram Bridge',       13.0012, 77.6756, 4, 'East Bengaluru'),
(4, 'Marathahalli Bridge',   12.9565, 77.7009, 4, 'East Bengaluru');

INSERT INTO Sensor (sensor_id, junction_id, sensor_type, installation_date, status, accuracy_pct) VALUES
(101, 1, 'inductive_loop', '2023-01-15', 'active', 96.5),
(102, 1, 'cctv',           '2023-03-20', 'active', 89.2),
(103, 2, 'inductive_loop', '2023-02-10', 'active', 95.8),
(104, 2, 'radar',          '2023-06-01', 'active', 93.1),
(105, 3, 'cctv',           '2023-04-15', 'active', 88.7),
(106, 4, 'inductive_loop', '2023-01-20', 'active', 97.0),
(107, 4, 'gps_probe',      '2023-07-01', 'active', 91.5);

INSERT INTO WeatherCondition (weather_id, condition, temperature, humidity_pct, rain_mm, visibility_km) VALUES
(1, 'Clear',       28.5, 55.0,  0.0, 10.0),
(2, 'Cloudy',      26.0, 70.0,  0.0,  8.0),
(3, 'Light Rain',  24.0, 85.0,  5.2,  5.0),
(4, 'Heavy Rain',  22.5, 95.0, 35.0,  2.0),
(5, 'Fog',         18.0, 92.0,  0.0,  1.5);
