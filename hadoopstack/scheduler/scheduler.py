from multiprocessing import Process

from hadoopstack import config
from hadoopstack.dbOperations import db

import hadoopstack
import hadoopstack.services.cluster as cluster
import hadoopstack.services.job

def schedule(data, operation):
    """Schedules based on certain filters"""

    if operation == 'create':
        conf = config.read_conf()

        clouds = filter_quota(data, conf)
        if clouds == []:
            return False

        cloud = filter_priority(clouds)
        if cloud is None:
            return False

        data['job']['cloud'] = cloud['name']
        db.flush_data_to_mongo('job', data)

        update_quota(data, cloud, operation)
        Process(target = cluster.create, args = (data, cloud)).start()

    elif operation == 'delete':

        job_id = data['job']['id']

        conf = config.read_conf()
        for cloud in conf['clouds']:
            if cloud['name'] == data['job']['cloud']:
                break

        Process(target = cluster.delete, args = (job_id, cloud)).start()
        update_quota(data, cloud, operation)

    elif operation == 'add':

        job_id = data['id']
        job_obj = hadoopstack.services.job.info(job_id)

        conf = config.read_conf()
        for cloud in conf['clouds']:
            if cloud['name'] == job_obj['job']['cloud']:
                break

        job_obj['job'] = data

        update_quota(job_obj, cloud, operation)
        Process(target = cluster.add_nodes, args = (data, cloud, job_id)).start()

    elif operation == 'remove':

        job_id = data['id']
        job_obj = hadoopstack.services.job.info(job_id)

        conf = config.read_conf()
        for cloud in conf['clouds']:
            if cloud['name'] == job_obj['job']['cloud']:
                break

        job_obj['job'] = data

        Process(target = cluster.remove_nodes, args = (data, cloud, job_id)).start()
        update_quota(job_obj, cloud, operation)

    return True

def update_quota(data, cloud, operation):
    """Update the avaiable quota of a cloud"""

    if operation == 'create':
        ram, vcpus, instances = calculate_usage(cloud, data)
        cloud['quota']['available']['ram'] += ram
        cloud['quota']['available']['vcpus'] += vcpus
        cloud['quota']['available']['instances'] += instances

    if operation == 'delete':
        ram, vcpus, instances = calculate_usage(cloud, data)
        cloud['quota']['available']['ram'] -= ram
        cloud['quota']['available']['vcpus'] -= vcpus
        cloud['quota']['available']['instances'] -= instances

    if operation == 'add':
        ram, vcpus, instances = calculate_usage(cloud, data)
        cloud['quota']['available']['ram'] -= ram
        cloud['quota']['available']['vcpus'] -= vcpus
        cloud['quota']['available']['instances'] -= instances

    if operation == 'remove':
        ram, vcpus, instances = calculate_usage(cloud, data)
        cloud['quota']['available']['ram'] += ram
        cloud['quota']['available']['vcpus'] += vcpus
        cloud['quota']['available']['instances'] += instances

    conf = config.read_conf()
    
    for i in range(0, len(conf['clouds'])):
        if conf['clouds'][i]['id'] == cloud['id']:
            conf['clouds'][i] = cloud

    db.flush_data_to_mongo('conf', conf)

def filter_priority(clouds):
    """Returns the cloud with the hightes priority"""

    priority = int(clouds[0]['priority'])
    qualified_cloud = clouds[0]

    for cloud in clouds:
        if int(cloud['priority']) < priority:
            priority = int(cloud['priority'])
            qualified_cloud = cloud

    return qualified_cloud

def filter_quota(data, conf):
    """
    Return the list of cloud objects which satisfy the resource required.
    """

    qualified_clouds = list()

    for cloud in conf['clouds']:
        if cloud_satisfy_quota(cloud, data):
            qualified_clouds.append(cloud)

    return qualified_clouds

def cloud_satisfy_quota(cloud, data):
    """
    Based on the resources required by the job, check if the current
    cloud object satisfies the requirement
    """

    ram, vcpus, instances = calculate_usage(cloud, data)
    available_quota = cloud['quota']['available']

    if ((ram < available_quota['ram']) and
        (vcpus < available_quota['vcpus']) and
        (instances < available_quota['instances'])):

        return True

    else:
        return False

def calculate_usage(cloud, data):
    """
    This function calculates resource requirement of the job.
    """

    job_ram = 0
    job_vcpus = 0
    job_instances = 0

    if data['job'].has_key('master'):
        master_flavor = data['job']['master']['flavor'].replace('.', '_')
        job_ram += cloud['flavors'][master_flavor]['ram']
        job_vcpus += cloud['flavors'][master_flavor]['vcpus']
        job_instances += 1

    for slave in data['job']['slaves']:
        slave_flavor = slave['flavor'].replace('.', '_')
        job_ram += cloud['flavors'][slave_flavor]['ram']
        job_vcpus += cloud['flavors'][slave_flavor]['vcpus']
        job_instances += slave['instances']

    return job_ram, job_vcpus, job_instances
