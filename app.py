from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

app = Flask(__name__)

@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "URL을 입력해주세요."}), 400

    try:
        # URL에 'v=' 파라미터가 있는지 확인하여 유효성을 검사합니다.
        query = urlparse(video_url).query
        if 'v' not in parse_qs(query):
            raise ValueError("유효한 YouTube 주소가 아닙니다.")
            
        video_id = parse_qs(query)["v"][0]

        # 유튜브 자막을 가져옵니다.
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        
        # 자막 리스트를 하나의 긴 텍스트로 합칩니다.
        full_transcript = " ".join([item['text'] for item in transcript_list])
        
        # 성공적으로 추출한 자막을 반환합니다.
        return jsonify({"transcript": full_transcript})

    except Exception as e:
        # Vercel 로그에서 에러를 쉽게 확인할 수 있도록 print()를 사용합니다.
        print(f"Error processing URL {video_url}: {e}")
        # 사용자에게 보여줄 에러 메시지를 반환합니다.
        return jsonify({"error": "자막을 가져올 수 없거나 처리 중 오류가 발생했습니다."}), 500





