from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# 이 데코레이터는 Vercel에서 CORS를 자동으로 처리해주므로 필요 없을 수 있지만,
# 만약을 위해 남겨둡니다.
@app.after_request
def after_request(response):
    header = response.headers
    header['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "URL을 입력해주세요."}), 400

    try:
        query = urlparse(video_url).query
        if 'v' not in parse_qs(query):
            raise ValueError("유효한 YouTube 주소가 아닙니다.")
            
        video_id = parse_qs(query)["v"][0]

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        full_transcript = " ".join([item['text'] for item in transcript_list])
        
        return jsonify({"transcript": full_transcript})

    except Exception as e:
        # Vercel 로그에서 에러를 확인하기 쉽도록 print()를 추가합니다.
        print(f"An error occurred: {e}")
        return jsonify({"error": "자막을 가져올 수 없거나 처리 중 오류가 발생했습니다."}), 500


