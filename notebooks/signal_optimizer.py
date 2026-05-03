def optimize_signal(north, south, east, west):

    lanes = {
        "North": north,
        "South": south,
        "East": east,
        "West": west
    }

    max_lane = max(lanes, key=lanes.get)

    green_time = lanes[max_lane] * 2

    return max_lane, green_time