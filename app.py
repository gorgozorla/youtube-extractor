# 필요한 도구들을 불러옵니다.
from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

# Flask 앱(우리의 서버)을 생성합니다.
# Vercel 환경에서는 이 'app' 변수를 찾아서 실행합니다.
app = Flask(__name__)
CORS(app)

# Vercel에서는 파일 이름이 곧 주소가 되므로,
# /api/transcript 경로 대신 /app 경로로 만들어도 됩니다.
# 하지만 클라이언트와의 호환을 위해 유지합니다.
@app.route('/api/transcript', methods=['GET'])
def get_transcript():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({"error": "URL을 입력해주세요."}), 400

    try:
        query = urlparse(video_url).query
        params = parse_qs(query)
        video_id = params["v"][0]

        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['ko', 'en'])
        full_transcript = " ".join([item['text'] for item in transcript_list])
        
        return jsonify({"transcript": full_transcript})

    except Exception as e:
        return jsonify({"error": "자막을 가져올 수 없습니다. 자막이 없는 영상이거나 주소가 잘못되었을 수 있습니다."}), 500

# 로컬에서 테스트할 때만 필요하고, Vercel 배포 시에는 이 부분은 사용되지 않습니다.
if __name__ == '__main__':
    app.run(debug=True, port=5000)

