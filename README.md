Description

docker, kubernetes, 

#### Pre-requesites: 
- you must have Docker Desktop installed on your PC
- Within Docker Desktop, Kubernetes must be enabled. 

#### Before running: 
- As well as showing the final plot on a webserver, it is also stored within the "output_plots" directory. To prevent an error and enable this on your machine: 
    - Open `k8s/pv-pvc.yaml`, and change the `hostPath` accordingly. The path is hereby slightly different than normal - e.g. `"/mnt/c/Users/nicol/OneDrive - University of Bristol/soft_eng/hzz_cloud_tech/output_plots"` must be written as `"/run/desktop/mnt/host/c/Users/nicol/OneDrive - University of Bristol/soft_eng/hzz_cloud_tech/output_plots"`.

- Modify the variables in "shared/data_vars.py" as desired. This file, in addition to "infofile.py" will be automatically copied to all container folders when the deploy script is run (see below).


#### How to run: 
type following into the command line: 
`bash deploy.sh`

This will take care of the building of the images and the deployments (also automatically scaling the number of workers), finally allowing the user to pause and visit the webserver showing the results plot before proceeding to clean everything up. 


comment the other scripts!