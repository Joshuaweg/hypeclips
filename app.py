from flask import Flask, render_template, request, jsonify
import os
from twelvelabs import TwelveLabs
from twelvelabs.models.task import Task
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from db_client import AtlasClient
import json

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
    db_results = atlas_client.find(COLLECTION_NAME, filter={'video_id': clip.video_id})
    #print(db_results[0]['upvote'])
    if len(db_results) == 0:
        atlas_client.insert(COLLECTION_NAME, {'video_id': clip.video_id, 'upvote': 0, 'downvote': 0})
        db_results = atlas_client.find(COLLECTION_NAME, filter={'video_id': clip.video_id})
    upvote = db_results[0]['upvote']
    downvote = db_results[0]['downvote']
    id_to_url = json.loads(open("video_urls.json").read())
    url = ""
    if clip.video_id not in id_to_url:
        url = ""
    else:
        url = id_to_url[clip.video_id]
        
    return {
        'video_id': clip.video_id,
        'score': float(clip.score),
        'start_time': clip.start,
        'end_time': clip.end,
        'thumbnail_url': clip.thumbnail_url,
        'video_url': url,
        'upvote': upvote,
        'downvote': downvote

    }
def print_page(page):
    for clip in page:
        print(f"video_id={clip.video_id} score={clip.score}")
        #print(clip)
@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": str(e)}), 500
@app.route('/', methods=['GET', 'POST'])
def search_page():
    try:
        query = request.args.get('query', '')
        return render_template('search_results.html', query=query)
    except Exception as e:
        app.logger.error(e)
        return jsonify({"error": str(e)}), 500
@app.route('/api/search', methods=['POST'])
def search_videos():
    data = request.get_json()
    query = data.get('query', '')
    response = client.search.query(INDEX_ID, query_text=query, options=['visual','text_in_video'],page_limit=1)
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
@app.route('/url')
def get_url():
    v_list = client.index.video.list(INDEX_ID, page_limit=50)
    id_to_url = {}
    for vid in v_list:
        print(vid.id)
        test = client.index.video.retrieve(index_id=INDEX_ID, id=vid.id)
        url = test.hls.video_url
        id_to_url[vid.id] = url
    print(id_to_url)
    return render_template('index.html')
@app.route('/api/vote', methods=['POST'])
def update_votes():
    data = request.get_json()
    video_id = data.get('videoId', '')
    vote = data.get('voteType', '')
    print(video_id)
    print(vote)

    # Get the current vote counts
    video = atlas_client.database[COLLECTION_NAME].find_one({'video_id': video_id})
    upvotes = video.get('upvote', 0)
    downvotes = video.get('downvote', 0)

    if vote == 'upvote':
        upvotes += 1
        atlas_client.update(COLLECTION_NAME, {'video_id': video_id}, {'$inc': {'upvote': 1}})
    elif vote == 'downvote':
        downvotes += 1
        atlas_client.update(COLLECTION_NAME, {'video_id': video_id}, {'$inc': {'downvote': 1}})

    return jsonify({
        'status': 'success',
        'upvotes': upvotes,
        'downvotes': downvotes
    })



if __name__ == '__main__':
     app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))