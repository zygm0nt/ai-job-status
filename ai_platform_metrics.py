import time
from google.cloud import monitoring_v3
import os

project_id = os.environ.get('PROJECT_ID')

client = monitoring_v3.MetricServiceClient()
project_name = f"projects/{project_id}"
now = time.time()
seconds = int(now)
nanos = int((now - seconds) * 10 ** 9)
interval = monitoring_v3.TimeInterval(
    {
        "end_time": {"seconds": seconds, "nanos": nanos},
        "start_time": {"seconds": (seconds - 1200), "nanos": nanos},
    }
)
results = client.list_time_series(
    request={
        "name": project_name,
        "filter": 'metric.type = "ml.googleapis.com/training/accelerator/memory/utilization"',
        "interval": interval,
        "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.HEADERS,
    }
)
for result in results:
    print(result)
