#!/bin/bash

# copy shared files to all container directories
cp shared/* data_collector/
cp shared/* worker/
cp shared/* manager/

# build Docker images
docker-compose -f docker-compose.build.yml build

# deploy rabbitmq
kubectl apply -f rabbitmq-deployment.yaml

echo "Waiting for RabbitMQ to become ready..."
kubectl wait --for=condition=available --timeout=120s deployment/rabbitmq

# deploy the rest: manager, workers- and collector deployments, persistenvolume and persistenvolumeClaim, as well as the webserver deployment.
kubectl apply -f k8s/

echo "All components deployed successfully!"
kubectl get pods

#wait for the collector job to complete
kubectl wait --for=condition=complete --timeout=600s job/collector 

#port-forward the web server to view the plot
kubectl port-forward service/web-server 8080:80 &
PORT_FORWARD_PID=$!

echo ""
echo "Done. You can now view the plot at http://localhost:8080/final_plot.png"
echo ""
echo "Press any key to stop the port forwarding..."
echo ""

#wait for user to stop the port forwarding
read -n 1 -s -r  

kill $PORT_FORWARD_PID

read -p "Proceed with deletion? enter [y/n]: " user_input

if [[ "$user_input" == "y" ]]; then
    echo "Deleting K8 resources..."
    kubectl delete -f k8s/
    kubectl delete -f rabbitmq-deployment.yaml
    echo "K8 Resources deleted successfully."

fi