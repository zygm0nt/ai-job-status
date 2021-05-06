from dataclasses import dataclass
from typing import List, Dict
import datetime

from googleapiclient import discovery
from execute_and_parse_yaml import execute_command

import random


@dataclass
class JobStatus:
    status: str
    consumedMLUnits: float
    createTime: datetime.datetime
    startTime: datetime.datetime
    endTime: datetime.datetime
    labels: Dict[str, str]
    trainingInput: Dict[str, str]

    def get_elapsed_time(self):
        if not self.startTime:
            return 0
        if self.endTime:
            delta = self.endTime - self.startTime
        else:
            delta = datetime.datetime.utcnow() - self.startTime
        return str(datetime.timedelta(
            seconds=delta.total_seconds()
        ))

    def is_finished(self):
        return self.status in ["SUCCEEDED", "FAILED"]


ZeroJobStatus = JobStatus(
    status="NOT STARTED",
    consumedMLUnits=None,
    createTime=None,
    startTime=None,
    endTime=None,
    labels={},
    trainingInput={},
)


@dataclass
class JobMetrics:
    gpu_mem_utilization: float  # training/accelerator/memory/utilization
    gpu_utilization: float      # training/accelerator/utilization
    cpu_utilization: float      # training/cpu/utilization
    mem_utilization: float      # training/memory/utilization
    received_bytes_count: int   # training/network/received_bytes_count
    sent_bytes_count: int       # training/network/sent_bytes_count


class JobStatusProvider:
    def get_id(self):
        pass

    def get_status(self) -> JobStatus:
        pass

    def get_metrics(self) -> JobMetrics:
        pass


class DummyJobStatusProvider(JobStatusProvider):
    def __init__(self, app_id: str):
        self.app_id = app_id
        self.counter = random.randint(5, 20)

    def get_id(self):
        return self.app_id

    def _status(self):
        if self.counter > 0:
            return "RUNNING"
        else:
            return "SUCCESS"

    def get_status(self) -> JobStatus:
        self.counter -= 1
        job_status = JobStatus(
            status=self._status(),
            consumedMLUnits=31.5,
            createTime=datetime.datetime.now(),
            startTime=datetime.datetime.now(),
            endTime=datetime.datetime.now(),
            labels={'env': 'dev', 'project': 'some-project', 'team': 'cool-team', 'user': 'X', 'counter': self.counter},
            trainingInput={'scaleTier': 'CUSTOM', 'masterType': 'n1-highmem-16', 'region': 'europe-west1',
                           'masterConfig':
                               {'imageUri': 'eu.gcr.io/some-image/some-project:latest-X',
                                'containerCommand': ['make', 'gs://', 'compress']
                                }
                           },
        )
        try:
            status_changed = self.job_status.status != job_status.status
        except:
            status_changed = False
        self.job_status = job_status
        return self.app_id, status_changed, self.job_status

    def get_metrics(self) -> JobMetrics:
        return JobMetrics(
            gpu_mem_utilization=random.uniform(0.01, 1.0),
            gpu_utilization=random.uniform(0.01, 1.0),
            cpu_utilization=random.uniform(0.01, 1.0),
            mem_utilization=random.uniform(0.01, 1.0),
            received_bytes_count=random.randint(100, 1000),
            sent_bytes_count=random.randint(100, 1000),
        )


class AIPlatformJobStatusProvider(JobStatusProvider):

    def __init__(self, project_id: str, app_id: str):
        self.project_id = project_id
        self.app_id = app_id
        cloudml = discovery.build('ml', 'v1')

        projectId = f'projects/{project_id}'
        jobId = f'{projectId}/jobs/{app_id}'

        self.request = cloudml.projects().jobs().get(name=jobId)

    def get_id(self):
        return self.app_id

    def get_stats_request(self):
        return self.request.execute()

    def get_status(self) -> JobStatus:
        try:
            response = self.get_stats_request()
        except Exception as e:
            print(e)
            return self.app_id, False, ZeroJobStatus
        job_status = JobStatus(
            status=response['state'],
            consumedMLUnits=self._try_to_get_ml_units(response),
            createTime=self._optional_time(response, 'createTime'),
            startTime=self._optional_time(response, 'startTime'),
            endTime=self._optional_time(response, 'endTime'),
            labels=response['labels'],
            trainingInput=response['trainingInput'],
        )
        try:
            status_changed = self.job_status.status != job_status.status
        except:
            status_changed = False
        self.job_status = job_status
        return self.app_id, status_changed, self.job_status

    def get_metrics(self) -> JobMetrics:
        pass

    def _try_to_get_ml_units(self, response):
        try:
            return float(response['trainingOutput']['consumedMLUnits'])
        except:
            return -1

    def _optional_time(self, response, tag):
        if tag in response:
            return datetime.datetime.strptime(response[tag], '%Y-%m-%dT%H:%M:%SZ')
        else:
            return None


class GCloutAIPlatformJobStatusProvider(AIPlatformJobStatusProvider):

    def get_stats_request(self):
        return execute_command(self.app_id)
