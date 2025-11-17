from flask import Flask, render_template, request, jsonify, send_file
import os, base64

# [수정됨] templates 폴더를 명시적으로 지정
app = Flask(__name__, template_folder="templates")

# -------------------- 기존 설정 --------------------
TOP_DIR = "static/tops"
BOTTOM_DIR = "static/bottoms"
OUTFIT_DIR = "static/outfits"
USER_IMG = "static/user.jpg"
RESULT_DIR = "static/results"
os.makedirs(RESULT_DIR, exist_ok=True)

from fashn_tryon import run_tryon
# ---------------------------------------------------
# (TTS 관련 API 키, client, /tts 라우트 전부 삭제)
# ('뷔페' 방식은 서버에 TTS 기능이 필요 없습니다)
# ---------------------------------------------------

@app.route("/")
def welcome():
    """ 
    [수정됨] 여기가 새로운 첫 페이지(흰 화면)입니다.
    """
    return render_template("welcome.html")

@app.route("/start")
def index():
    """ 
    [수정됨] 기존 index.html은 이제 /start 주소입니다.
    """
    return render_template("index.html")

@app.route("/capture")
def capture_page():
    return render_template("capture.html")

@app.route("/review")
def review_page():
    """ [추가됨] 누락된 /review 라우트 """
    return render_template("review.html")

@app.route("/select")
def select_page():
    tops = [f"{TOP_DIR}/{f}" for f in os.listdir(TOP_DIR)]
    bottoms = [f"{BOTTOM_DIR}/{f}" for f in os.listdir(BOTTOM_DIR)]
    return render_template("select.html", tops=tops, bottoms=bottoms)

@app.route("/upload", methods=["POST"])
def upload():
    data = request.get_json()
    img_data = data.get("image")
    header, encoded = img_data.split(",", 1)
    decoded = base64.b64decode(encoded)
    with open(USER_IMG, "wb") as f:
        f.write(decoded)
    return jsonify({"success": True})

@app.route("/tryon", methods=["POST"])
def tryon():
    data = request.get_json()
    top = data.get("top")
    bottom = data.get("bottom")
    mode = data.get("mode")
    
    import time
    timestamp = int(time.time())
    
    result_filename = ""
    garment_to_try = ""
    
    def format_path(path_str):
        if not path_str:
            return None
        if "/static/" in path_str:
            path_str = path_str.split("/static/", 1)[1]
        return os.path.join("static", path_str)

    top_path = format_path(top)
    bottom_path = format_path(bottom)

    if mode == "top" and top_path:
        result_filename = f"result_top_{timestamp}.jpg"
        garment_to_try = top_path
    elif mode == "bottom" and bottom_path:
        result_filename = f"result_bottom_{timestamp}.jpg"
        garment_to_try = bottom_path
    elif mode == "both" and top_path and bottom_path:
        try:
            top_file = os.path.basename(top_path)
            bottom_file = os.path.basename(bottom_path)
            top_num = top_file.replace("top", "").split(".")[0]
            bottom_num = bottom_file.replace("bottom", "").split(".")[0]
            outfit_name = f"set_{top_num}_{bottom_num}.png"
            outfit_path = os.path.join(OUTFIT_DIR, outfit_name)
            
            if not os.path.exists(outfit_path):
                return jsonify({"error": f"해당 조합의 'set' 파일이 없습니다: {outfit_path}"}), 400
                
            result_filename = f"result_set_{top_num}_{bottom_num}_{timestamp}.jpg"
            garment_to_try = outfit_path
        except Exception as e:
            print(f" आउटफिट 경로 생성 오류: {e}")
            return jsonify({"error": "파일 이름 규칙 오류"}), 400

    if not garment_to_try:
        return jsonify({"error": "합성할 옷 정보가 없습니다."}), 400

    result_path = run_tryon(USER_IMG, garment_to_try, result_filename)
    if result_path:
        url_path = result_path.replace(os.sep, "/")
        if not url_path.startswith("/"):
             url_path = "/" + url_path
        return jsonify({"result": url_path})
        
    return jsonify({"error": "합성 실패"}), 400

@app.route("/loading")
def loading_page():
    """ [추가됨] 누락된 /loading 라우트 """
    return render_template("loading.html")

@app.route("/result")
def result_page():
    image_path = request.args.get("image")
    if not image_path:
        return "결과 이미지가 없습니다.", 404
    return render_template("result.html", result_image=image_path)

if __name__ == "__main__":
    app.run(debug=True)