import os
from flask import Flask, render_template, request
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task

app = Flask(__name__)

# Replace with your actual Twelve Labs API key
TWELVE_LABS_API_KEY = ""
INDEX_ID = "670add2fe5620307b898c1b0"

client = TwelveLabs(api_key=TWELVE_LABS_API_KEY)
def print_page(page):
    for clip in page:
        print(f"video_id={clip.video_id} score={clip.score}")
        #print(clip)
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form['query']
        results = search_videos(query)
        return render_template('results.html', results=results)
    return render_template('index.html')

def search_videos(query):
    response = client.search.query(INDEX_ID, query_text=query, options=['visual'])
    results = []
    print_page(response.data)
    results.extend(response.data)
    
    while True:
        try:
            next_page = next(response)
            print_page(next_page)
            results.extend(next_page)
        except StopIteration:
            break
    
    return results


if __name__ == '__main__':
    app.run(debug=True)