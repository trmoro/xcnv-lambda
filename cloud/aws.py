import os
import boto
import boto.s3.connection

#Read credentials
f = open("cloud/credentials.config")

# S3
ACCESS_KEY = f.readline().replace("\n","").split(" ")[1]
SECRET_KEY = f.readline().replace("\n","").split(" ")[1]
REGION = f.readline().replace("\n","").split(" ")[1]
BUCKET = f.readline().replace("\n","").split(" ")[1]

#Close credentials file
f.close()

#Get S3 connection
def getS3():    
    conn = boto.s3.connect_to_region(REGION,
            aws_access_key_id = ACCESS_KEY,
            aws_secret_access_key = SECRET_KEY,
            calling_format = boto.s3.connection.OrdinaryCallingFormat(),
            )
    
    return conn, conn.get_bucket(BUCKET)


#Set S3 file
def setFile(bucket,file,data):
    key = bucket.new_key(file)
    key.set_contents_from_string(data)
