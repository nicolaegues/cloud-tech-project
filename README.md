
This project presents a scalable version of the ATLAS HZZ analysis notebook (https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata/blob/master/13-TeV-examples/uproot_python/HZZAnalysis.ipynb) that leverages Docker containers, RabbitMQ, and Kubernetes. 

Note: The components.yaml file was downloaded from https://github.com/kubernetes-sigs/metrics-server for the implementation of the Kubernetes HorizontalPodAutoscaling, with a small section modified to fix an error. 


### Pre-requesites: 
- Docker Desktop must be installed on your PC
- Within Docker Desktop, Kubernetes must be enabled. 

### Before running: 
- As well as showing the final plot on a webserver, it is also stored within the "output_plots" directory. To prevent an error and enable this on your machine: 

    Open `k8s/pv-pvc.yaml`, and change the `hostPath` accordingly. The path is hereby slightly different than normal: 

    e.g. `/mnt/c/Users/nicol/OneDrive - University of Bristol/soft_eng/hzz_cloud_tech/output_plots` must be written as: `/run/desktop/mnt/host/c/Users/nicol/OneDrive - University of Bristol/soft_eng/hzz_cloud_tech/output_plots`

- Modify the variables in `shared/data_vars.py` as desired. This file, in addition to `infofile.py` will be automatically copied to all container folders when the deploy script is run (see below).

### How to run: 
type following into the command line: 

        bash deploy.sh

This will take care of the building of the images and the deployments (also automatically scaling the number of workers), finally allowing the user to pause and visit the webserver showing the results plot before proceeding to clean everything up (i.e., deleting all kubernetes resources).


### Commands used for the scalability evaluation:
To save the pod-count every 10 seconds in a log: 
        watch -n 10 'kubectl get pods --no-headers | wc -l >> pod_scaling.log && date "+%Y-%m-%d %H:%M:%S" >> pod_scaling.log'
To turn this log into a csv with a pod count and timestamp column: 
        paste -d ',' <(grep -E '^[0-9]+$' pod_scaling.log) <(grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}' pod_scaling.log) > pod_scaling.csv

To save the CPU usage every 10 seconds in a log: 
        watch -n 10 'kubectl get hpa >> hpa_metrics.log && date "+%Y-%m-%d %H:%M:%S" >> hpa_metrics.log'