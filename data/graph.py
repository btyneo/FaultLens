#dv_electric is the compressor's own outlet valve signal (per its sensors description) so its 
# grouped as compressor rather than air control panel even tho the function is downstream flow control 

component_graph = {
    "Compressor": {
        "sensors": ["TP2", "Motor_current", "Oil_temperature", "Oil_level", "COMP", "DV_eletric", "MPG"],
        "failure_modes": ["motor overload", "oil leak", "valve failure"],
    },
    "Air Control Panel": {
        "sensors": ["TP3", "H1", "Reservoirs", "LPS", "Caudal_impulses"],
        "failure_modes": ["pressure regulation failure", "air leak"],
    },
    "Air Dryer": {
        "sensors": ["DV_pressure", "Towers", "Pressure_switch"],
        "failure_modes": ["moisture carryover", "tower switching failure"],
    },
}


sensor_to_subsystem = {
    sensor: subsystem
    for subsystem, info in component_graph.items()
    for sensor in info["sensors"]
}

if __name__ == "__main__":
    all_sensors = [s for info in component_graph.values() for s in info["sensors"]]
    assert len(all_sensors) == len(set(all_sensors)), "a sensor appears in more than one subsystem"
    print(f"{len(all_sensors)} sensors mapped across {len(component_graph)} subsystems")