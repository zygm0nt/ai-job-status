# ai-job-status

## Running

To run the dashboard you need to have `gcloud` sdk installed, as the default version uses that CLI tool to fetch
jobs' statuses.

With that set up, you can start the thing:

```
pip install -r requirements.txt
export PROJECT_ID=your-project-id
python dashboard.py
```

## Multiple implementations of JobStatusProvider

There are multiple implementations of this class:

* `DummyJobStatusProvider` - only for testing purposes
* `AIPlatformJobStatusProvider` - this uses API calls - you need to get `json` auth file for the Service Account with
  all the necessary access rights to project your jobs are running in. **This method consumes Web API quotas, which 
  need to be configured for the given SA.**
* `GCloutAIPlatformJobStatusProvider` - and this implementation just calls `gcloud` to get the stats. It seems
  more constrained - there is no way to get the job statistics unfortunately. 

## Add job to tracking

Just send job's id to exposed port:

```
echo -n 'job_id' | nc localhost 3000
```

### Script that does it for you

Suppose you have a script for starting jobs, that spits out the job_id in its last line, than you could use
`parse_and_submit.sh` script to pass that id to dashboard:

```
script to submit job to ai-platform | ./parse_and_submit.sh
```


## How to monitor GCP jobs with API calls

* https://cloud.google.com/monitoring/api/metrics_gcp#gcp-ml
* https://stackoverflow.com/questions/59892910/is-there-a-way-to-be-notified-of-status-changes-in-google-ai-platform-training-j
* https://cloud.google.com/monitoring/custom-metrics/reading-metrics#timeseries-list-data

