import os
from flask import Flask, render_template, request
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task

app = Flask(__name__)

# Replace with your actual Twelve Labs API key
TWELVE_LABS_API_KEY = "tlk_241Z16H2R70KP22J4CV3K22801XG"
TWELVE_LABS_API_URL = "https://api.twelvelabs.io/v1.1/search"
INDEX_ID = "66f1cde8163dbc55ba3bb220"

client = TwelveLabs(api_key=TWELVE_LABS_API_KEY)
def print_page(page):
    for clip in page:
        print(f"video_id={clip.video_id} score={clip.score}")
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_videos(query)
        return render_template('results.html', results=results)
    return render_template('index.html')

def search_videos(query):
    response = client.search.query(INDEX_ID,query_text=query,options=['visual'])
    print_page(response.data)
    while True:
        try:
            print_page(next(response))
        except StopIteration:
            break
    return response.data

if __name__ == '__main__':
    app.run(debug=True)