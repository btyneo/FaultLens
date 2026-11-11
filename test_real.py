from agents.retrieval import retrieve
from agents.anomaly import detect_anomalies        # Hamza's real code
from agents.diagnose import diagnose                # Hamza's real code
from agents.recommendation import make_recommendation, request_approval

# April 18, 2020 = documented air leak in the dataset
data = retrieve({"start": "2020-04-18T00:00:00Z", "end": "2020-04-18T23:59:59Z"})
print("Rows:", data.shape)

flags = detect_anomalies(data)
print("Flags:", len(flags))

result = diagnose(flags)
print("Diagnose:", result)

rec = make_recommendation(result, flags)
approved = request_approval(rec)
print("FINAL" if approved else "REJECTED")