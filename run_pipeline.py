from agents.router import route
from agents.retrieval import retrieve                      
from agents.stub_diagnostics import detect_anomalies, diagnose

def run(question : str):
    # this calls route passing in question , whaterver route returns it will get stored in the new variable parsed
    parsed = route(question)
    print("Parsed:", parsed)

    # NEW: the router only gives the "request slip" (dates as text);
    # retrieval turns it into the actual sensor rows for that window
    data = retrieve(parsed["time_window"])
    print("Retrieved:", data.shape)
    if data.empty:                                          # NEW: make the no-data case visible
        print("No sensor data in this window")

    # CHANGED: detect_anomalies now gets the sensor slice, not parsed
    flags = detect_anomalies(data)
    print("Anomalies : ", flags)

    #flags goes into diagnose()
    result = diagnose(flags)
    print("Diagnose:", result )

    return result


if __name__ == "__main__":
    run("Were there any motor issues in the last 24 hours?")