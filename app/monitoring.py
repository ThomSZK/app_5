import os
from prometheus_client import Gauge, CollectorRegistry

# Configuração segura para container Docker
if not os.path.exists('/app/prometheus_data'):
    os.makedirs('/app/prometheus_data', exist_ok=True)

os.environ['PROMETHEUS_MULTIPROC_DIR'] = '/app/prometheus_data'

registry = CollectorRegistry()

DRIFT_SCORE = Gauge(
    'data_drift_score',
    'Score de drift de dados',
    registry=registry
)

def calculate_drift(current_data, reference_data):
    try:
        # Implementação simplificada para testes
        drift_value = 0.5  # Valor fictício para testes
        DRIFT_SCORE.set(drift_value)
        return drift_value
    except Exception as e:
        print(f"Erro no cálculo de drift: {str(e)}")
        return 0.0