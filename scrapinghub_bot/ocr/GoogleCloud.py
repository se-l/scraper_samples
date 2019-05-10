import pickle
import datetime
from google.cloud import vision
from google.cloud import storage
from google.oauth2 import service_account
credentials = service_account.Credentials. from_service_account_file(r'google settings json')

class Path:
    scrapy_d = r'p1'
    data_img = r"p2"
    transformed = r'p3'
    transformed_tmp = r'p3'
    transformed_img = r'p4'
    s3_img_root = r's3_image_directory'

storage_client = storage.Client(credentials=credentials)
vision_client = vision.ImageAnnotatorClient(credentials=credentials)
bucket_name = r'your_bucket'
project_id = 'your_project_id'
bucket = storage_client.get_bucket(bucket_name)
blobs = bucket.list_blobs()

config = {
  "RESULT_TOPIC": "topic_name",
  "RESULT_BUCKET": bucket_name
}

def pp_ocr(blob_names):
    storage_client = storage.Client(
        credentials=credentials)
    vision_client = vision.ImageAnnotatorClient(credentials=credentials)
    bucket_name = bucket_name
    project_id = project_id
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()
    ocr_results = {}
    print('Started ocr...')
    for b in blobs:
        if b.name in blob_names:
            ocr_results[b.name.split('/')[1]] = ocr(b)
        else:
            continue
    print('writing to disk...')
    with open(r'C:\target\pp_{}.pickle'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')), 'wb') as f:
        pickle.dump(ocr_results, f)

def ocr(blob):
    result = {}
    whole_resp, text_concat = detect_text(bucket, filename=blob.name)
    result['response'] = whole_resp
    result['text_concat'] = text_concat
    return result

# [START functions_ocr_detect]
def detect_text(bucket, filename):
    # print('Looking for text in image {}'.format(filename))
    futures = []
    text_detection_response = vision_client.text_detection({
        'source': {'image_uri': 'gs://{}/{}'.format(bucket.name, filename)}
    })
    annotations = text_detection_response.text_annotations
    if len(annotations) > 0:
        text = annotations[0].description
    else:
        text = ''
    # print('Extracted text {} from image ({} chars).'.format(text, len(text)))
    return text_detection_response, text
# [END functions_ocr_detect]

# [START message_validatation_helper]
def validate_message(message, param):
    var = message.get(param)
    if not var:
        raise ValueError('{} is not provided. Make sure you have \
                          property {} in the request'.format(param, param))
    return var
# [END message_validatation_helper]

if __name__ == "__main__":
    # execute only if run as a script
    # main()
    pass