# Author:       Gregory Ewing
# Contact:      gregjewi@umich.edu
# Date:         January 2019

# Description	Upload base_latest_recommend.png image to AWS s3 account


import boto3
bucket = 'YOUR_BUCKET_HERE'
obj = 'obj_filename.png'
obj_path = '/obj/path/'

resource = 's3'

def delete_obj(obj,bucket):
    f = s3.Object(bucket,obj)
    f.delete()
    
    return


s3 = boto3.resource(resource)
glwa_bucket = s3.Bucket(bucket)
img = open(obj_path + obj,'rb')

files = []
for file in glwa_bucket.objects.all():
    files.append(file.key)

if obj in files:
    delete_obj(obj,bucket)

s3.Bucket(bucket).put_object(Key=obj, Body=img, ACL='public-read')