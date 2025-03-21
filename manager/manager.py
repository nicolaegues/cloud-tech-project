
import infofile
import pika
import pickle
import uproot
import data_vars


# ATLAS Open Data directory
atlas_dir = data_vars.variables["atlas_dir"]
fraction =  data_vars.variables["fraction"]
batch_size =  data_vars.variables["batch_size"]
samples = data_vars.samples

def collect_tasks(path, samples, fraction, batch_size ): 
    """
    Collects a series of tasks to be distributed to workers, by gathering all the data sample URLs and extracting the start- and end-indices of event batches within each sample. 
    
    """

    tasks = []
    for sample in samples: 
        for val in samples[sample]["list"]: 

            if sample == 'data': 
                prefix = "Data/" # Data prefix
            else: # MC prefix
                prefix = "MC/mc_"+str(infofile.infos[val]["DSID"])+"."

            url = path+prefix+val+".4lep.root"

            tree = uproot.open(url + ":mini")
            num_events = tree.num_entries
            num_events = int(num_events*fraction) #accounts for potential reduced size

            for start_idx in range(0, num_events, batch_size):
                end_idx = min(start_idx + batch_size, num_events)

                task = {"sample": sample, "value": val, "url": url, "start_idx": start_idx, "end_idx": end_idx}
                tasks.append(task)

    #give each task this additional information, for the collector container to then know how many total tasks to await.
    num_tasks = len(tasks)
    for task in tasks:
        task["total_tasks"] = num_tasks 

    return tasks


def publish_tasks(task_list):
    """
    Publishes a list of tasks to a RabbitMQ queue.

    Parameters:
    - task_list (list): A list of dictionaries, whereby each dictionary represents a task.

    The function connects to RabbitMQ, declares a queue named "task_queue",
    and publishes each task as a serialized message to the queue.
    """

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)
    
    for task in task_list:
        message = pickle.dumps(task)
        channel.basic_publish(
            exchange="",
            routing_key="task_queue",
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)  #make messages persist even if RabbitMQ restarts
        )
   

        print(f"Published task for sample {task["sample"]}, value {task["value"]}, event indeces {task["start_idx"]} - {task["end_idx"]}")
    

task_list =  collect_tasks(atlas_dir, samples, fraction, batch_size)
publish_tasks(task_list )



