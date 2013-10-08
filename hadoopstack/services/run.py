from hadoopstack.services.remote import Remote

HADOOP_GID='123'
HDFS_UID='201'
MAPRED_UID='202'
UMASK='0022'

def setup_s3fs(credentials, remote):
    """
    Creates /etc/passwd-s3fs containing AWS access and secret key in the
    following form.

    accesskey:secretaccesskey

    @param  credentials: AWS access key and secret ID
    @type   credentials: C{dict}

    @param  remote: Instance of remote.Remote class
    @type   remote: remote.Remote instance
    """

    pass_file_content = ':'.join([
                        credentials['ec2_access_key'],
                        credentials['ec2_secret_key']
                        ])

    remote.run("echo {0} | sudo tee -a /etc/passwd-s3fs".format(pass_file_content))
    remote.sudo("chmod 0400 /etc/passwd-s3fs")

def mount_bucket(bucket, remote):
    """
    Mount the remote bucket with input data using s3fs

    @param  bucket: Bucket name
    @type   bucket: C{str}

    @param  remote: Instance of remote.Remote class
    @type   remote: remote.Remote instance
    """

    remote.sudo("mkdir /media/{0}".format(bucket))
    remote.sudo("chown root:hadoop -R /media/{0}".format(bucket))
    remote.sudo("chmod 775 -R /media/{0}".format(bucket))
    remote.sudo("s3fs {0} -o uid={1},gid={2},umask={3},allow_other \
        /media/{0}".format(bucket, MAPRED_UID, HADOOP_GID, UMASK))

def copy_to_hdfs(input_uri, remote):
    """
    Copy the data stored at uri(s3) to local HDFS

    @param  input_uri: s3 address - s3://bucket/path/to/input/dir
    @type   input_uri: C{str}
    """
    bucket_name = input_uri.split('/')[2]
    input_path = input_uri.split('//')[1]

    remote.sudo("hadoop fs -mkdir tmp", user='mapred')
    remote.sudo("hadoop fs -copyFromLocal /media/{0}/ .".format(input_path),
        user='mapred')

def download_jar(jar_location, remote):
    """
    Download jar from a remote jar_location
    """

    uri_protocol = jar_location.split(':')[0]
    if uri_protocol == 's3':
        download_url = 'https://s3.amazonaws.com/{0}'.format(jar_location.split('//')[1])
    else:
        download_url = jar_location

    remote.run("wget {0} -O /tmp/file.jar".format(download_url))

def run_job(jar_location, args, input_uri, output_uri, remote):
    """
    Submits a job to a hadoop cluster
    """

    input_dir = input_uri.split('/')[-1]
    output_dir = output_uri.split('/')[-1]

    download_jar(jar_location, remote)
    remote.sudo("hadoop jar /tmp/file.jar {0} {1} {2}".format(args,
                                                input_dir, output_dir),
                                                user = 'mapred')

def submit_job(data, user, credentials):
    """
    Makes all preparation required prior to submitting a job.

    * Mount S3 bucket
    * Copy data to HDFS
    * Download jar

    and then finally submit the job.
    """

    job_name = data['job']['name']
    key_location = "/tmp/hadoopstack-" + job_name + ".pem"
    
    for node in data['job']['nodes']:
        if node['role'] == 'master':
            remote = Remote(node['ip_address'], user, key_location)

    if data['job']['input'] != 's3://':
        bucket_name = data['job']['input'].split('/')[2]
        setup_s3fs(credentials, remote)
        mount_bucket(bucket_name, remote)
        copy_to_hdfs(data['job']['input'], remote)

    run_job(
        data['job']['jar'],
        data['job']['args'],
        data['job']['input'],
        data['job']['output'],
        remote
        )
