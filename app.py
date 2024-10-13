import os
from urllib.parse import quote
from flask import Flask, render_template, request
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_client import AtlasClient

app = Flask(__name__)

# Replace with your actual Twelve Labs API key
TWELVE_LABS_API_KEY = "tlk_2GXN4TQ02EEHC527VTMFX1C1DQXX"
INDEX_ID = "670add2fe5620307b898c1b0"

DB_NAME = 'hype'

COLLECTION_NAME = 'videos'
db_uri ="mongodb+srv://hype:hype@pictora.mgro1.mongodb.net/?retryWrites=true&w=majority&appName=pictora"
client = TwelveLabs(api_key=TWELVE_LABS_API_KEY)
# Create a new client and connect to the server
atlas_client = AtlasClient (db_uri, DB_NAME)
atlas_client.ping()
def serialize_clip(clip):
    """Convert clip object to a dictionary."""
    return {
        'video_id': clip.video_id,
        'score': float(clip.score),
        'start_time': clip.start,
        'end_time': clip.end,
        'thumbnail_url': clip.thumbnail_url,
    }
def print_page(page):
    for clip in page:
        print(f"video_id={clip.video_id} score={clip.score}")
        #print(clip)
@app.route('/', methods=['GET', 'POST'])
def search_page():
    query = request.args.get('query', '')
    return render_template('search_results.html', query=query)
@app.route('/api/search', methods=['POST'])
def search_videos():
    data = request.get_json()
    query = data.get('query', '')
    response = client.search.query(INDEX_ID, query_text=query, options=['visual','text_in_video'])
    results = []
    print_page(response.data)
    results.extend(map(serialize_clip, response.data))
    
    while True:
        try:
            next_page = next(response)
            print_page(next_page)
            results.extend(map(serialize_clip, next_page))
        except StopIteration:
            break
    return results
@app.route('/videos', methods=['GET'])
def get_videos():
    videos = atlas_client.find(COLLECTION_NAME)
    return render_template('videos.html', videos=videos)
@app.route('/ids', methods=['GET'])
def get_ids():
    v_list=client.index.video.list(INDEX_ID,page_limit=50)
    print(len(v_list))
    return render_template('ids.html', ids=v_list)
@app.route('/player')
def video_player():
    video_folder = 'videos'
    video_files = [f for f in os.listdir(video_folder) if f.endswith('.mp4')]
    video_paths = ['/static/videos/' + f for f in video_files]
    
    return render_template('rateplayer.html', videos=video_paths)


if __name__ == '__main__':
    app.run(debug=True)