from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

# Vercel의 자동 CORS 정책과의 충돌 가능성을 없애기 위해
# @app.after_request 관련 코드를 제거했습니다.

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




