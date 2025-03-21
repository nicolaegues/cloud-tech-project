import pika
import pickle 

import infofile
import vector
import uproot
import time
import awkward as ak
import data_vars

lumi =  data_vars.variables["lumi"]

def perform_analysis(task):
    """
    Obtained from https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata/blob/master/13-TeV-examples/uproot_python/HZZAnalysis.ipynb. 

    Performs filtering of collision events and invariant mass calculations to demonstrate the Higgs-Boson dicovery process.,
    See notebook for more information. 

    
    """

    url = task["url"]
    sample = task["sample"]
    value = task["value"]
    start_idx = task["start_idx"]
    end_idx = task["end_idx"]

    # Define what variables are important to our analysis
    variables = ['lep_pt','lep_eta','lep_phi','lep_E','lep_charge','lep_type']
    weight_variables = ["mcWeight", "scaleFactor_PILEUP", "scaleFactor_ELE", "scaleFactor_MUON", "scaleFactor_LepTRIGGER"]

    MeV = 0.001
    GeV = 1.0



    # Cut lepton type (electron type is 11,  muon type is 13)
    def cut_lep_type(lep_type):
        sum_lep_type = lep_type[:, 0] + lep_type[:, 1] + lep_type[:, 2] + lep_type[:, 3]
        lep_type_cut_bool = (sum_lep_type != 44) & (sum_lep_type != 48) & (sum_lep_type != 52)
        return lep_type_cut_bool # True means we should remove this entry (lepton type does not match)

    # Cut lepton charge
    def cut_lep_charge(lep_charge):
        # first lepton in each event is [:, 0], 2nd lepton is [:, 1] etc
        sum_lep_charge = lep_charge[:, 0] + lep_charge[:, 1] + lep_charge[:, 2] + lep_charge[:, 3] != 0
        return sum_lep_charge # True means we should remove this entry (sum of lepton charges is not equal to 0)

    # Calculate invariant mass of the 4-lepton state
    # [:, i] selects the i-th lepton in each event
    def calc_mass(lep_pt, lep_eta, lep_phi, lep_E):
        p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_E})
        invariant_mass = (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).M * MeV # .M calculates the invariant mass
        return invariant_mass

    def calc_weight(weight_variables, sample, events):
        info = infofile.infos[sample]
        xsec_weight = (lumi*1000*info["xsec"])/(info["sumw"]*info["red_eff"]) #*1000 to go from fb-1 to pb-1
        total_weight = xsec_weight 
        for variable in weight_variables:
            total_weight = total_weight * events[variable]
        return total_weight

    # Open file
    tree = uproot.open(url + ":mini")

    # start the clock
    start = time.time() 
    sample_data = []

    # Loop over data in the tree
    for data in tree.iterate(variables + weight_variables, 
                                library="ak", 
                                entry_start= start_idx, 
                                entry_stop= end_idx,
                                step_size = 1000000): 
        
        # Number of events in this batch
        nIn = len(data) 
                                
        # Record transverse momenta (see bonus activity for explanation)
        data['leading_lep_pt'] = data['lep_pt'][:,0]
        data['sub_leading_lep_pt'] = data['lep_pt'][:,1]
        data['third_leading_lep_pt'] = data['lep_pt'][:,2]
        data['last_lep_pt'] = data['lep_pt'][:,3]

        # Cuts
        lep_type = data['lep_type']
        data = data[~cut_lep_type(lep_type)]
        lep_charge = data['lep_charge']
        data = data[~cut_lep_charge(lep_charge)]
        
        # Invariant Mass
        data['mass'] = calc_mass(data['lep_pt'], data['lep_eta'], data['lep_phi'], data['lep_E'])

        # Store Monte Carlo weights in the data
        if 'data' not in value: # Only calculates weights if the data is MC
            data['totalWeight'] = calc_weight(weight_variables, value, data)
            nOut = sum(data['totalWeight']) # sum of weights passing cuts in this batch 
        else:
            nOut = len(data)

        elapsed = time.time() - start # time taken to process
        print("\t\t nIn: "+str(nIn)+",\t nOut: \t"+str(nOut)+"\t in "+str(round(elapsed,1))+"s") # events before and after

        # Append data to the whole sample data list
        sample_data.append(data)

    


    results_data = ak.concatenate(sample_data)

    task["result_data"] = results_data

    results = task

    return results
    

def callback(ch, method, properties, body): 
    """
    This callback function is called automatically whenever a new message arrives in the task_queue. 
    It processes the message, performs the analysis, and publishes the result to the results_queue. 

    Parameters:
    - ch: The channel instance.
    - method: provides the delivery tag.
    - properties: Contains message properties.
    - body: The message body (pickled task data).
    """

    #deserialize the message
    task = pickle.loads(body)
    print(f"Received task for sample {task["sample"]}, value {task["value"]}, event indeces {task["start_idx"]} - {task["end_idx"]}")

    result = perform_analysis(task)

    #serialize the result to send it back
    results_message = pickle.dumps(result)

    #publish the result to the 'results_queue'
    ch.basic_publish(
        exchange = "",
        routing_key = "results_queue", 
        body = results_message, 
        properties = pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        )   
    )

    ch.basic_ack(delivery_tag = method.delivery_tag) 


connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
channel = connection.channel()
channel.queue_declare(queue='task_queue', durable=True)
channel.queue_declare(queue='results_queue', durable=True) 

channel.basic_qos(prefetch_count=1) #tells rabbitMQ not to give more than one message to a worker at a time.
channel.basic_consume(queue='task_queue', on_message_callback=callback) 

print("Worker waiting for tasks. To exit press CTRL+C")
channel.start_consuming()



