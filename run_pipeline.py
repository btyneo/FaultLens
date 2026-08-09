from agents.router import route
from agents.stub_diagnostics import detect_anomalies, diagnose

def run(question : str):
    # this calls route passing in question , whaterver route returns it will get stored in the new variable parsed
    parsed = route(question)
    print("Parsed:", parsed)
    # parsed goes into detect_anomalies()
    flags = detect_anomalies(parsed)
    print("Anomalies : ", flags)
    
    #flags goes into diagnose()
    result = diagnose(flags)
    print("Diagnose:", result )
    
    return result


if __name__ == "__main__":
    run("Were there any motor issues in the last 24 hours?")