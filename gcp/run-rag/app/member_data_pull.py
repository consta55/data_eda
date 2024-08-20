from google.cloud import storage

def get_ai_summary(member_id:str):
    """This function returns the ai summary from the member 
    that is asking the query

    Args:
        member_id (str): the member's member ID
    """
    client = storage.Client()
    #BUCKET_NAME = 'DEMO_BUCKET'
    bucket = client.get_bucket('ai-health-summary')

    blobs = bucket.list_blobs(prefix=member_id)

    files = []
    for blob in blobs:
        files.append(blob.name)
        
    file_name = list(filter(lambda x: 'requisitions' in x, files))
    requisition_file = file_name[0]
    bucket_path = f"gs://ai-health-summary/{requisition_file}"

    """Downloads a blob into memory."""
    # The ID of your GCS bucket
    bucket_name = 'ai-health-summary'

    # The ID of your GCS object
    blob_name = requisition_file

    # Construct a client side representation of a blob.
    # Note `Bucket.blob` differs from `Bucket.get_blob` as it doesn't retrieve
    # any content from Google Cloud Storage. As we don't need additional data,
    # using `Bucket.blob` is preferred here.
    blob = bucket.blob(blob_name)
    contents = blob.download_as_bytes()
    return contents
