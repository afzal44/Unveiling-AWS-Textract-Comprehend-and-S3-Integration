import streamlit as st
import pandas as pd
import boto3
from io import BytesIO

# Replace these placeholders with your actual AWS access key and secret access key
st.set_page_config(
    page_title="Streamlining AWS: Uniting Comprehend, Textract, and S3 via Streamlit")

st.title("Streamlining AWS: Uniting Comprehend, Textract, and S3 via Streamlit")

st.sidebar.title("S3 File Upload")
st.sidebar.markdown("Upload a file to S3")

# connect to boto3 and initiate services
comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1', aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key)
textract = boto3.client('textract', region_name='ap-south-1', aws_access_key_id=access_key_id,
                        aws_secret_access_key=secret_access_key)
s3 = boto3.client('s3', aws_access_key_id=access_key_id,
                  aws_secret_access_key=secret_access_key)
with st.sidebar:
    # upload file to s3 bucket
    uploaded_file = st.file_uploader("Upload a file", type=["png", "jpeg", "tiff"])
    s3_bucket_name = 'hhc4u'


    # save uploaded file to s3 bucket
    if uploaded_file is not None:
        s3_src = boto3.resource('s3',aws_access_key_id=access_key_id,
                          aws_secret_access_key=secret_access_key)
        s3_src.Bucket(s3_bucket_name).put_object(
            Key=uploaded_file.name, Body=uploaded_file)
        st.write("File uploaded to S3 bucket.")


    # select file from s3 bucket
    
    response = s3.list_objects_v2(Bucket=s3_bucket_name)

    file_list = []
    # Check if there are any items in the s3 bucket, if there are, add them to the file_list, if there aren't display a message
    if 'Contents' in response:
        for obj in response['Contents']:
            file_list.append(obj['Key'])
    else:
        st.write("No files in S3 bucket")

    selected_file = st.selectbox("Select a file from S3 bucket", file_list, placeholder="Select a file from S3 bucket", index=None)
    st.write("You selected: ", selected_file)



# display thumbnail of the file

if selected_file is None:
    st.write("Please select a file from S3 bucket")
else:
    # download file from s3 bucket
    # s3 = boto3.client('s3')
    response = s3.get_object(Bucket=s3_bucket_name, Key=selected_file)
    file_stream = BytesIO(response['Body'].read())

    st.image(file_stream)

    
    # extract text from file
    st.header("Extracted text:")
    response = textract.detect_document_text(Document={'S3Object': {'Bucket': s3_bucket_name, 'Name': selected_file}})
    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            text += item["Text"] + "\n"
    st.write(text)
    
    # sentiment analysis
    st.header("Sentiment Analysis:")
    sentiment_response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
    sentiment = sentiment_response['Sentiment']
    sentiment_score = sentiment_response['SentimentScore']
    st.write("Sentiment: ", sentiment)
    st.write("Sentiment Score: ", sentiment_score)


    # key phrases
    key_phrases_response = comprehend.detect_key_phrases(Text=text, LanguageCode='en')
    key_phrases = key_phrases_response['KeyPhrases']
    st.write("Key Phrases:")
    df_key_phrases = pd.DataFrame(key_phrases)
    st.dataframe(df_key_phrases)

    # entities
    entities_response = comprehend.detect_entities(Text=text, LanguageCode='en')
    entities = entities_response['Entities']
    st.write("Entities: ")
    df_entities = pd.DataFrame(entities)
    st.dataframe(df_entities)
