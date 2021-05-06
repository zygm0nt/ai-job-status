import yaml
import subprocess
import os

example = """
createTime: '2021-04-28T07:41:39Z'
endTime: '2021-04-28T08:40:59Z'
etag: 2423424234234
jobId: cool-project-job-123
labels:
  env: dev
  project: cool-project
  team: team-start
  user: user1
startTime: '2021-04-28T07:43:23Z'
state: SUCCEEDED
trainingInput:
  masterConfig:
    containerCommand:
    - make
    - ifpath=gs://...
    - ofpath=gs://...
    imageUri: eu.gcr.io/proj-name/img_name:some-version
  masterType: n1-highmem-16
  region: europe-west2
  scaleTier: CUSTOM
trainingOutput:
  consumedMLUnits: 1.85
"""


def execute_command(job_id):
    with open(os.devnull) as devnull:
        result = subprocess.run(
            ["gcloud",  "ai-platform", "jobs", "describe", job_id],
            stdout=subprocess.PIPE,
            stderr=devnull
        )
    return parse_output(result.stdout.decode('utf-8'))


def parse_output(output):
    try:
        return yaml.safe_load(output)
    except yaml.YAMLError as exc:
        raise exc
