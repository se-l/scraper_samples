import boto3
import pickle

class aws:
    key = 'AWS KEY'
    secret = 'AWS secre key'

def get_all_s3() -> list:
    all_objects = []
    trunc_object = s3.list_objects_v2(Bucket=bucket)
    all_objects += trunc_object['Contents']
    truncated = trunc_object['IsTruncated']
    while truncated:
        trunc_object = s3.list_objects_v2(Bucket=bucket,
                                          StartAfter=trunc_object['Contents'][-1]['Key'])
        all_objects += trunc_object['Contents']
        truncated = trunc_object['IsTruncated']

    with open(r'C:\target_dest', 'wb') as f:
        pickle.dump(all_objects, f)
    return all_objects


if __name__ == "__main__":

    bucket = 'bucket_name'
    photo = 'imagesfull/sample path.jpg'
    region = 'your region'

    s3 = boto3.client("s3", region_name=region,
                      aws_access_key_id=aws.key,
                      aws_secret_access_key=aws.secret)
    all_objects = get_all_s3()
    # AWSKEY = AwsKeys.seoul
    rek_client = boto3.client('rekognition', region_name=region,
                          aws_access_key_id=aws.key,
                          aws_secret_access_key=aws.secret
                          )

    response = rek_client.detect_text(Image={'S3Object': {'Bucket': bucket, 'Name': photo}})

    textDetections = response['TextDetections']
    print(response)
    print('Matching text')
    for text in textDetections:
        print('Detected text:' + text['DetectedText'])
        print('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
        print('Id: {}'.format(text['Id']))
        if 'ParentId' in text:
            print('Parent Id: {}'.format(text['ParentId']))
        print('Type:' + text['Type'])
