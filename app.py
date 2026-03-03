from flask import Flask, request, jsonify, render_template, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__, template_folder='.')

# ডাউনলোড করা ফাইল রাখার জন্য একটি ফোল্ডার
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/get-url', methods=['POST'])
def get_url():
    data = request.json
    video_url = data.get('url')
    res = data.get('resolution')

    if not video_url:
        return jsonify({'success': False, 'error': 'Link dewa hoyni'})

    # ফাইল নেম ইউনিক করার জন্য UUID ব্যবহার
    file_id = str(uuid.uuid4())
    output_template = f'{DOWNLOAD_FOLDER}/{file_id}.%(ext)s'

    # রেজোলিউশন অনুযায়ী ফরম্যাট সেটআপ
    # এটি ভিডিওর বেস্ট কোয়ালিটি এবং অডিওর বেস্ট কোয়ালিটি নিয়ে মার্জ করবে
    format_selection = f'bestvideo[height<={res}]+bestaudio/best[height<={res}]/best'
    
    ydl_opts = {
        'format': format_selection,
        'outtmpl': output_template,
        'merge_output_format': 'mp4',  # ভিডিও ও অডিও জোড়া লাগিয়ে mp4 করবে
        'cookiefile': 'cookies.txt',
        'quiet': True,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True) # এখানে ডাউনলোড হবে
            filename = f"{file_id}.mp4"
            
            # Render এর ডোমেইন অনুযায়ী ডাউনলোড ইউআরএল তৈরি
            download_link = f"{request.host_url}download/{filename}"
            
            return jsonify({
                'success': True, 
                'download_url': download_link,
                'title': info.get('title')
            })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download/<filename>')
def serve_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
