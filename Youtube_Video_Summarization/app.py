from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = Flask(__name__)

@app.route('/transcript')
def transcript():
    video_id = request.args.get('videoId')
    if not video_id:
        return jsonify({"error": "Missing 'videoId' parameter"}), 400

    # Eğer kullanıcı tam URL yerine video ID gönderirse, burada sadece ID olarak alınacak şekilde düzenleyebilirsiniz
    # Örnek: https://www.youtube.com/watch?v=5MgBikgcWnY -> sadece 5MgBikgcWnY alınır
    if "youtube.com" in video_id or "youtu.be" in video_id:
        # video_id parametresi URL ise video ID'yi ayıklama
        import re
        match = re.search(r"(?:v=|\/)([a-zA-Z0-9_-]{11})", video_id)
        if match:
            video_id = match.group(1)
        else:
            return jsonify({"error": "Invalid YouTube URL or unable to extract video ID"}), 400

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        full_text = " ".join([t['text'] for t in transcript_list])
        return jsonify({"transcript": full_text})
    except VideoUnavailable:
        return jsonify({"error": "The video is unavailable."}), 404
    except TranscriptsDisabled:
        return jsonify({"error": "Transcripts are disabled for this video."}), 404
    except NoTranscriptFound:
        return jsonify({"error": "No transcript found for this video."}), 404
    except Exception as e:
        # Diğer beklenmeyen hatalar için
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
