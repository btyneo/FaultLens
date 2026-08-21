from agents.interfaces import AnomalyFlag

def detect_anomalies(data, window=240, threshold=3):
    sensor_anomalies = []
    for sensor in data:
        rolling_mean = data[sensor].rolling(window).mean()
        rolling_std = data[sensor].rolling(window).std()
        z_score = (data[sensor] - rolling_mean)/rolling_std
        anomalies = z_score[abs(z_score) > threshold]
        for timestamp, severity in anomalies.items():
            sensor_anomalies.append(AnomalyFlag(sensor, timestamp, abs(severity)))
        
    return sensor_anomalies