# main.py

from flask import Flask, request, jsonify, session, send_from_directory
from datetime import datetime
import uuid
import os

from firebase_init import db, bucket

app = Flask(__name__)
app.secret_key = "ewha-market-secret"

# ---------------------------
# FE 디렉토리 경로
# ---------------------------
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FE_DIR = os.path.join(BASE_DIR, "FE")

# ---------------------------
# FE 파일 라우팅
# ---------------------------
@app.route("/styles/<path:filename>")
def serve_styles(filename):
    return send_from_directory(os.path.join(FE_DIR, "styles"), filename)

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory(os.path.join(FE_DIR, "assets"), filename)

@app.route("/reviews/<path:filename>")
def serve_reviews(filename):
    return send_from_directory(os.path.join(FE_DIR, "reviews"), filename)

@app.route("/auth/<path:filename>")
def serve_auth(filename):
    return send_from_directory(os.path.join(FE_DIR, "auth"), filename)

@app.route("/products/<path:filename>")
def serve_products(filename):
    return send_from_directory(os.path.join(FE_DIR, "products"), filename)

# ---------------------------
# 리뷰 등록 API (POST)
# ---------------------------
@app.route("/api/reviews", methods=["POST"])
def create_review():

    # 1) 로그인 체크
    #user_id = session.get("id")
    #if not user_id:
    #    return jsonify({"success": False, "error": "로그인이 필요합니다."}), 401
    # 임시로 로그인 없이 리뷰 작성
    user_id = "test_user"

    # 2) 폼 파라미터 읽기
    product_id = request.form.get("product_id")
    rating = request.form.get("rating")
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()

    if not product_id or not rating or not content:
        return jsonify({
            "success": False,
            "error": "product_id, rating, content는 필수입니다."
        }), 400

    try:
        rating = float(rating)
    except ValueError:
        return jsonify({"success": False, "error": "rating은 숫자여야 합니다."}), 400

    # 3) 이미지 업로드
    image_files = request.files.getlist("images")
    image_urls = []

    for file in image_files:
        if not file or file.filename == "":
            continue

        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "jpg"

        filename = f"reviews/{product_id}/{uuid.uuid4().hex}.{ext}"
        blob = bucket.blob(filename)
        blob.upload_from_file(file, content_type=file.content_type)
        blob.make_public()

        image_urls.append(blob.public_url)

    # 4) Firestore 저장
    review_data = {
        "product_id": product_id,
        "user_id": user_id,
        "rating": rating,
        "title": title,
        "content": content,
        "image_urls": image_urls,
        "created_at": datetime.utcnow()
    }

    doc = db.collection("reviews").add(review_data)
    review_id = doc[1].id

    return jsonify({
        "success": True,
        "message": "리뷰가 성공적으로 등록되었습니다!",
        "review_id": review_id
    }), 201


if __name__ == "__main__":
    app.run(debug=True)
