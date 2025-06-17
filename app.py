from flask import Flask, request, jsonify, send_from_directory
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
import re
import os

app = Flask(__name__)

# Replace with your actual YouTube Data API Key if you plan to use it for other purposes.
# For simply fetching public subtitles, youtube-transcript-api usually doesn't require a key.
# It's recommended to store this in an environment variable for production.
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', 'YOUR_YOUTUBE_API_KEY_HERE')

# Helper function to extract YouTube video ID from a URL
def get_video_id(url):
    """
    Extracts the YouTube video ID from various YouTube URL formats.
    """
    # Standard YouTube URL
    match = re.search(r'(?:v=|\/embed\/|\/watch\?v=|\/youtu.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    # YouTube Shorts URL
    match = re.search(r'youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})', url)
    if match:
        return match.group(1)
    return None

@app.route('/')
def index():
    """
    Serves the main HTML page.
    """
    return send_from_directory('.', 'index.html')

@app.route('/extract_subtitles', methods=['POST'])
def extract_subtitles():
    """
    API endpoint to extract subtitles from a given YouTube video URL.
    """
    data = request.get_json()
    youtube_url = data.get('youtube_url')

    if not youtube_url:
        return jsonify({'error': 'YouTube URL이 제공되지 않았습니다.'}), 400

    video_id = get_video_id(youtube_url)
    if not video_id:
        return jsonify({'error': '유효한 유튜브 비디오 URL이 아닙니다.'}), 400

    try:
        # Fetch transcripts. Default language is English.
        # You can specify language preferences, e.g., ['ko', 'en'] for Korean, then English
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to find a Korean transcript first, then fallback to English, then auto-generated
        transcript_found = False
        transcript = None

        # Prioritize explicitly available Korean transcript
        for t in transcript_list:
            if t.language_code == 'ko' and not t.is_generated:
                transcript = t.fetch()
                transcript_found = True
                break
        
        # If no explicit Korean, try explicit English
        if not transcript_found:
             for t in transcript_list:
                if t.language_code == 'en' and not t.is_generated:
                    transcript = t.fetch()
                    transcript_found = True
                    break

        # If still not found, try auto-generated Korean
        if not transcript_found:
            for t in transcript_list:
                if t.language_code == 'ko' and t.is_generated:
                    transcript = t.fetch()
                    transcript_found = True
                    break
        
        # Finally, fallback to any auto-generated English
        if not transcript_found:
            for t in transcript_list:
                if t.language_code == 'en' and t.is_generated:
                    transcript = t.fetch()
                    transcript_found = True
                    break
        
        # If no transcript found after all attempts, raise an error
        if not transcript_found or transcript is None:
            raise NoTranscriptFound(f"No suitable transcript found for video ID: {video_id}")


        return jsonify({'subtitles': transcript}), 200

    except NoTranscriptFound:
        return jsonify({'error': '이 비디오에는 자막을 사용할 수 없습니다.', 'details': f'Video ID: {video_id}'}), 404
    except TranscriptsDisabled:
        return jsonify({'error': '이 비디오는 자막이 비활성화되어 있습니다.', 'details': f'Video ID: {video_id}'}), 403
    except VideoUnavailable:
        return jsonify({'error': '비디오를 사용할 수 없거나 찾을 수 없습니다.', 'details': f'Video ID: {video_id}'}), 404
    except Exception as e:
        # Catch any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return jsonify({'error': f'자막을 추출하는 중 오류가 발생했습니다: {str(e)}'}), 500

if __name__ == '__main__':
    # For local development:
    # app.run(debug=True, port=5000)
    # For Vercel deployment, this block is not directly executed as Vercel uses a WSGI server.
    pass # No need to run app.run() here for Vercel





