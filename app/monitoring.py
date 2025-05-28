from prometheus_client import start_http_server, Gauge
from evidently.report import Report
from evidently.metrics import DataDriftTable

DRIFT_GAUGE = Gauge('model_drift_score', 'Drift score between current and reference data')

def monitor_drift(current_data, reference_data):
    report = Report(metrics=[DataDriftTable()])
    report.run(current_data=current_data, reference_data=reference_data)
    drift_score = report.as_dict()['metrics'][0]['result']['drift_share']
    DRIFT_GAUGE.set(drift_score)
    return drift_score

# Iniciar servidor Prometheus
start_http_server(8001)