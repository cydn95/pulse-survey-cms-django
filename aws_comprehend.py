import boto3
import json

#initialize comprehend module
comprehend = boto3.client(service_name='comprehend', region_name='us-east-2')

#here is the main part - comprehend.detect_sentiment is called
Text=["Testing"]
# Text = "I'm going to test this api"
sentimentData = comprehend.batch_detect_sentiment(TextList=Text, LanguageCode="en")
# sentimentData = comprehend.detect_sentiment(
    # Text=Text, LanguageCode="en")

qdata = {
    "Sentiment": "ERROR",
    "MixedScore": 0,
    "NegativeScore": 0,
    "NeutralScore": 0,
    "PositiveScore": 0,
}
print(sentimentData)
if "Sentiment" in sentimentData:
    qdata["Sentiment"] = sentimentData["Sentiment"]
if "SentimentScore" in sentimentData:
    if "Mixed" in sentimentData["SentimentScore"]:
        qdata["MixedScore"] = sentimentData["SentimentScore"]["Mixed"]
    if "Negative" in sentimentData["SentimentScore"]:
        qdata["NegativeScore"] = sentimentData["SentimentScore"]["Negative"]
    if "Neutral" in sentimentData["SentimentScore"]:
        qdata["NeutralScore"] = sentimentData["SentimentScore"]["Neutral"]
    if "Positive" in sentimentData["SentimentScore"]:
        qdata["PositiveScore"] = sentimentData["SentimentScore"]["Positive"]
