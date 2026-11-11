from agents.router import route
from agents.retrieval import retrieve                      
from agents.diagnose import diagnose
from agents.anomaly import  detect_anomalies

from agents.recommendation import make_recommendation, request_approval

def run(question : str):
    # this calls route passing in question , whaterver route returns it will get stored in the new variable parsed
    parsed = route(question)
    print("Parsed:", parsed)

    # NEW: the router only gives the "request slip" (dates as text);
    # retrieval turns it into the actual sensor rows for that window
    data = retrieve(parsed["time_window"])
    print("Retrieved:", data.shape)
    if data.empty:
        print("No sensor data in this window - cannot diagnose.")
        return {"recommendation": None, "approved": False}

    # CHANGED: detect_anomalies now gets the sensor slice, not parsed
    flags = detect_anomalies(data)
    print("Anomalies:", len(flags), "flags")

    #flags goes into diagnose()
    result = diagnose(flags)
    print("Diagnose:", result )
    
    rec = make_recommendation(result, flags)
    approved = request_approval(rec)
    
    if approved:
        print("FINAL: recommendation approved.")
    else:
        print("REJECTED: recommendation discarded, nothing is final.")
    
    return {"recommendation": rec, "approved": approved}

    return result

    

if __name__ == "__main__":
    run("Were there any issues on March 10, 2020?")