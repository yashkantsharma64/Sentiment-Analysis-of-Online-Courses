from flask import Flask, jsonify, request, render_template
from googleapiclient.discovery import build
from langdetect import detect
import textblob
import re
import requests
from bs4 import BeautifulSoup

api_key = 'AIzaSyCZFh7SJyEQexNtDpqQQwIZubYYMyNdB6Q'




def extract_youtube_video_comments(video_id):
    youtube = build('youtube', 'v3', developerKey=api_key)

    video_response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id
    ).execute()
    comments = []
    while len(comments) <= 100:
        for item in video_response['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            try:
                if detect(comment) == 'en':
                    comments.append(comment)
            except:
                pass
            # reply_count = item['snippet']['totalReplyCount']
            # if reply_count > 0:
            #     for reply in item['replies']['comments']:
            #         reply_text = reply['snippet']['textDisplay']
            #         try:
            #             if detect(reply_text) == 'en':
            #                 comments.append(reply_text)
            #         except:
            #             # Handle the exception (e.g., skip the comment)
            #             pass
                    # print(f"Comment: {comment}, Reply: {reply_text}\n")

        # Handle pagination
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                pageToken=video_response['nextPageToken']
            ).execute()
        else:
            break
    return comments

def extract_video_id(youtube_link):
    # Regular expression pattern to match YouTube video IDs
    pattern = r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, youtube_link)
    if match:
        return match.group(1)  # Extract the video ID from the matched pattern
    else:
        return None

def analyze_yt_comments(video_id):
    # Enter the video ID
    #'PCfiqY05BpA'
    comments = extract_youtube_video_comments(video_id)

    sentiment, positive, negative, neutral = analyze_sentiment(comments)
    print("Sentiment Analysis of the video comments:")
    avg_sentiment = sum(sentiment) / len(sentiment)

    # Print overall review
    if avg_sentiment > 0:
        return "Positive", avg_sentiment, positive, negative, neutral
    elif avg_sentiment == 0:
        return "Neutral", avg_sentiment, positive, negative, neutral
    else:
        return "Negative", avg_sentiment, positive, negative, neutral

def analyze_sentiment(comments):
    sentiments = []
    positive = negative = neutral = 0
    for comment in comments:
        analysis = textblob.TextBlob(comment)
        sentiments.append(analysis.sentiment.polarity)
        if(analysis.sentiment.polarity > 0):
            positive += 1
        elif(analysis.sentiment.polarity < 0):
            negative += 1
        else:
            neutral += 1
    return sentiments, positive, negative, neutral

def extract_comments(soup):
    comments = []
    # Find the HTML elements containing comments
    comment_elements = soup.find_all('div', class_='tutor-review-comment')

    for comment in comment_elements:
        comments.append(comment.text.strip())
        # print(comment.text.strip())
    return comments

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def home():
    return render_template('index.html')

@app.route('/yt.html')
def yt():
    return render_template('yt.html')

@app.route('/st.html')
def st():
    return render_template('st.html')


@app.route('/yt.html/submit', methods=['GET','POST'])
def yt_sentiment():
    if request.method == 'POST':
        data = request.json
        if data:
            video_id = data.get('input')
            video_id = extract_video_id(video_id)
            print("Received video ID:", video_id)
            status, score, positive, negative, neutral = analyze_yt_comments(video_id)
            print(status, score)
            return jsonify({
                "status": status,
                "score": score,
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            })  # Return a JSON response if needed
        else:
            return jsonify(error='No data provided'), 400  # Return an error response if data is missing
    else:
        return jsonify(error='Method not allowed'), 405


@app.route('/st.html/submit', methods=['POST'])
def st_sentiment():
    if request.method == 'POST':
        data = request.json
        if data:
            web_id = data.get('input')
            r = requests.get(web_id)
            soup = BeautifulSoup(r.content, 'html.parser')
            comments = extract_comments(soup)
            score, positive, negative, neutral = analyze_sentiment(comments)
            avg_sentiment = sum(score) / len(score)

            if avg_sentiment > 0:
                status = 'Positive'
            elif avg_sentiment < 0:
                status = 'Negative'
            else:
                status = 'Neutral'
            print(status, score)
            return jsonify({
                "status": status,
                "score": avg_sentiment,
                "positive": positive,
                "negative": negative,
                "neutral": neutral
            })  # Return a JSON response if needed
        else:
            return jsonify(error='No data provided'), 400  # Return an error response if data is missing
    else:
        return jsonify(error='Method not allowed'), 405

if __name__ == '__main__':
    app.run(debug=True)