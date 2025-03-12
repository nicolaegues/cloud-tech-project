
import infofile
import pika
import pickle


"""
be able to scale up in terms of data size
have plot get displayed (not saved as file)
last ex of k8s

what is a queue purge?

split data points as well. very uneven. 

"""

# ATLAS Open Data directory
atlas_dir = "https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/4lep/"


samples = {

    'data': {
        'list' : ['data_A','data_B','data_C','data_D'], # data is from 2016, first four periods of data taking (ABCD)
    },

    r'Background $Z,t\bar{t}$' : { # Z + ttbar
        'list' : ['Zee','Zmumu','ttbar_lep'],
        'color' : "#6b59d3" # purple
    },

    r'Background $ZZ^*$' : { # ZZ
        'list' : ['llll'],
        'color' : "#ff0000" # red
    },

    r'Signal ($m_H$ = 125 GeV)' : { # H -> ZZ -> llll
        'list' : ['ggH125_ZZ4lep','VBFH125_ZZ4lep','WH125_ZZ4lep','ZH125_ZZ4lep'],
        'color' : "#00cdff" # light blue
    },

}


def collect_urls(path, samples): 

    tasks = []

    for sample in samples: 
        for val in samples[sample]["list"]: 

            if sample == 'data': 
                prefix = "Data/" # Data prefix
            else: # MC prefix
                prefix = "MC/mc_"+str(infofile.infos[val]["DSID"])+"."

            fileString = path+prefix+val+".4lep.root"

            task = {"sample": sample, "value": val, "url": fileString}
            tasks.append(task)

    num_tasks = len(tasks)

    for task in tasks:
        task["total_tasks"] = num_tasks 

    return tasks


def publish_tasks(task_list):

    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
    channel.queue_declare(queue="task_queue", durable=True)
    
    for task in task_list:
        message = pickle.dumps(task)
        channel.basic_publish(
            exchange="",
            routing_key="task_queue",
            body=message,
            properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent)  #make message persistent
        )
   

        print(f"Published task (URL) for value {task["value"]} in sample {task["sample"]} ")
    
    #connection.close()

task_list =  collect_urls(atlas_dir, samples)
publish_tasks(task_list )



