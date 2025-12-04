from flask import Flask, render_template, flash, redirect, url_for, session, request, jsonify
from database import DBhandler
import hashlib
import sys
import os
import math
from datetime import datetime             
import uuid         
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()



application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "image", "products")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB = DBhandler()

LEVEL_THRESHOLDS = [50, 100, 150, 200, 250]


def calc_level_info(total_points: int):
    level = 1
    bar_max = LEVEL_THRESHOLDS[0]

    for idx, th in enumerate(LEVEL_THRESHOLDS):
        if total_points < th:
            level = idx + 1
            bar_max = th
            break
    else:
        level = len(LEVEL_THRESHOLDS) + 1
        bar_max = total_points + 50

    remaining = max(0, bar_max - total_points)
    return level, bar_max, remaining

# 홈
@application.route("/")
def home():
    page = request.args.get("page", 0, type=int)
    sort_type = request.args.get("sort", "new")

    data = DB.get_items()
    if data is None:
        data = {}
    
    items_list = []
    for key, value in data.items():
        value['name'] = key
        if "id" in session:
            value['is_liked'] = DB.is_heart(session['id'], key)
        else:
            value['is_liked'] = False
        items_list.append(value)

    if sort_type == "low":
        items_list.sort(key=lambda x: int(x.get('price', 0)))
    elif sort_type == "high":
        items_list.sort(key=lambda x: int(x.get('price', 0)), reverse=True)
    elif sort_type == "popular":
        items_list.sort(key=lambda x: int(x.get('like_count', 0)), reverse=True)
    else:
        items_list.sort(key=lambda x: x.get('reg_date', ''), reverse=True)

    item_counts = len(items_list)
    per_page = 8
    page_count = math.ceil(item_counts / per_page)
    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    current_page_data = items_list[start_idx:end_idx]

    return render_template(
        "index.html",
        datas=current_page_data,
        page=page,
        page_count=page_count,
        total=item_counts,
        limit=per_page,
        sort_type=sort_type
    )
    
@application.route("/show_heart/<name>", methods=['GET'])
def show_heart(name):
    if "id" not in session:
        return jsonify({"msg": "로그인이 필요합니다."}), 401

    user_id = session["id"]
    my_heart, new_count = DB.toggle_heart(user_id, name)
    DB.add_heart_point(user_id)

    return jsonify({'my_heart': my_heart, 'like_count': new_count})

# 리뷰 목록
@application.route("/reviews")
def reviews_index():
    return render_template("reviews/index.html")

# 리뷰 작성
@application.route("/reviews/write")
def reviews_write():
    product = request.args.get("product")  # 상품명
    img_path = request.args.get("img")     # 이미지 경로

    if not product:
        return "product is required", 400

    # 이미지 없으면 기본 이미지 사용
    if not img_path:
        img_path = "default.png"

    return render_template(
        "reviews/write-review.html",
        product=product,
        img_path=img_path
    )

# 리뷰 전체 조회 API
@application.route("/api/reviews", methods=["GET"])
def get_all_reviews():
    reviews = DB.get_all_reviews()

    if not reviews:
        return jsonify([]), 200
    
    # Firebase는 dict 형태라서 리스트로 변환
    review_list = []
    for rid, rdata in reviews.items():
        rdata["id"] = rid
        review_list.append(rdata)

    return jsonify(review_list), 200

# 리뷰 상세 조회 API
@application.route("/api/reviews/<review_id>", methods=["GET"])
def get_review_detail(review_id):
    review = DB.get_review_by_id(review_id)

    if review:
        review["id"] = review_id
        return jsonify(review), 200
    
    return jsonify({"error": "review not found"}), 404

#리뷰 등록 
@application.route("/reviews/submit", methods=['POST'])
def review_submit_post():

    # 로그인 필요 시 사용
    user_id = session.get("id", "guest")

    # 1) form 데이터 읽기
    product_id = request.form.get("product_id")
    rating = request.form.get("rating")
    title = request.form.get("title", "")
    content = request.form.get("content", "")

    if not product_id or not rating or not content:
        return jsonify({"success": False, "error": "필수 항목 누락"}), 400

    # 2) 이미지 처리
    images = request.files.getlist("images")
    saved_paths = []

    for img in images:
        if img.filename != "":
            filename = secure_filename(f"{uuid.uuid4().hex}_{img.filename}")
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            img.save(save_path)
            saved_paths.append(f"/static/image/{filename}")

    # 3) DB 저장
    review_data = {
        "product_id": product_id,
        "user_id": user_id,
        "rating": float(rating),
        "title": title,
        "content": content,
        "images": saved_paths,
        "created_at": str(datetime.utcnow())
    }

    DB.insert_review(review_data)   

    if user_id != "guest":
        DB.add_review_point(user_id)   

    return jsonify({"success": True})
    
# 리뷰 상세 조회
@application.route("/reviews/detail/<review_id>")
def review_detail(review_id):

    review = DB.get_review_by_id(review_id)

    if not review:
        return "리뷰를 찾을 수 없습니다.", 404

    return render_template("reviews/detail.html", review=review)

#내 리뷰만 보기 
@application.route("/api/my-reviews", methods=["GET"])
def get_my_reviews():
    user_id = session.get("id")
    if not user_id:
        return jsonify({"error": "not logged in"}), 401

    reviews = DB.get_reviews_by_user(user_id)
    return jsonify(reviews), 200

# 리뷰 삭제 API
@application.route("/api/reviews/<review_id>", methods=["DELETE"])
def delete_review(review_id):
    # 로그인 여부 확인
    user_id = session.get("id")
    if not user_id:
        return jsonify({"success": False, "error": "not logged in"}), 401

    review = DB.get_review_by_id(review_id)

    if not review:
        return jsonify({"success": False, "error": "review not found"}), 404

    # 본인 리뷰인지 확인
    if review["user_id"] != user_id:
        return jsonify({"success": False, "error": "permission denied"}), 403

    # 삭제 실행
    DB.delete_review(review_id)

    return jsonify({"success": True}), 200

# 상품 등록
@application.route("/products/enroll")
def products_enroll():
    # 로그인 여부 확인
    if "id" not in session:
        flash("상품을 등록하려면 로그인이 필요합니다.")
        return redirect(url_for("login"))
        
    return render_template("products/enroll.html")

# 상품 상세
@application.route("/products/detail/<name>")
def products_detail(name):
    data = DB.get_item_byname(str(name))

    is_liked = False
    if "id" in session:
        is_liked = DB.is_heart(session['id'], str(name))

    return render_template(
        "products/detail.html",
        name=name,
        data=data,
        is_liked=is_liked,
    )


# 마이페이지
@application.route("/mypage")
def mypage_index():
    user_id = session.get("id")
    if not user_id:
        flash("로그인 후 이용 가능합니다.")
        return redirect(url_for("login"))

    user = DB.get_user(user_id)

    if not user:
        flash("사용자 정보를 찾을 수 없습니다.")
        return redirect(url_for("home"))
    
    # 내가 등록한 상품 가져오기 & 최신순 정렬
    my_items = DB.get_items_byseller(user_id)
    my_items.sort(key=lambda x: x.get('reg_date', ''), reverse=True)

    #찜한 상품 목록
    favorites = DB.get_favorite_items(user_id)

    # 레벨바 계산 관련
    stats = DB.get_user_stats(user_id)
    review_count = stats["review_count"]
    item_count = stats["item_count"]
    heart_count = stats["heart_count"]
    total_points = review_count * 50 + item_count * 80 + heart_count * 15
    level, bar_max, remaining_points = calc_level_info(total_points)

    return render_template(
        "mypage/index.html",
        user=user,
        my_items=my_items,
        favorites=favorites,
        level=level,
        total_points=total_points,
        bar_max=bar_max,
        remaining_points=remaining_points,
    )

    # 참여도 레벨(상품 등록: 30pts, 리뷰 등록: 50pts)
    
    
# 마이페이지 - 상품 등록 내역 보기
@application.route("/mypage/products")
def my_products():
    user_id = session.get("id")
    
    if not user_id: return redirect(url_for("login"))
    my_items = DB.get_items_byseller(user_id)
    my_items.sort(key=lambda x: x.get('reg_date', ''), reverse=True)
    
    return render_template("mypage/my_products.html", my_items=my_items)


# 마이페이지-2 (회원 정보 수정 페이지)
@application.route("/mypage/edit-info", methods=['GET', 'POST'])
def mypage_edit():
    user_id = session.get("id")    # 로그인한 사용자의 id
    if not user_id:
        return redirect(url_for("login"))
    
    # 페이지 요청(GET): 수정 폼 표시
    if request.method == "GET":
        user = DB.get_user(user_id) or {}
        
        return render_template(
            "mypage/edit-info.html",
            username=user.get("username") or "",
            user_id=user_id,
            email=user.get("email") or "",
            number=user.get("number") or "",
            password="",
            checkpw="",
            total=0,
            page_count=0,
        )
    
    # POST: 수정 저장
    username = request.form.get('username')
    form_id  = request.form.get('id')
    email    = request.form.get('email')
    number   = request.form.get('number')
    password = request.form.get('password')
    checkpw  = request.form.get('checkpw')
    
    errors = []
    if not username:
        errors.append("이름을 입력해주세요.")
    if not form_id:
        errors.append("아이디를 입력해주세요.")
    if form_id != user_id:
        errors.append("아이디 값이 올바르지 않습니다.")
    if not email:
        errors.append("이메일을 입력해주세요.")
    if not number:
        errors.append("전화번호를 입력해주세요.")
    if not password:
        errors.append("비밀번호를 입력해주세요.")
    if password != checkpw:
        errors.append("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
    
    if errors:
        for msg in errors:
            flash(msg, "error")
        return render_template(
            "mypage/edit-info.html",
            username=username or "",
            user_id=user_id,
            email=email or "",
            number=number or "",
            password=password or "",
            checkpw=checkpw or "",
            total=0,
            page_count=0,
        )

    pw_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    update_data = {
        "username": username,
        "email": email,
        "number": number,
        "pw": pw_hash,
    }
    
    # user 사진 변경
    uploaded = request.files.get("profile_img")
    if uploaded and uploaded.filename:
        safe_name = secure_filename(uploaded.filename)
        filename = f"{user_id}_{safe_name}"
        
        save_dir = os.path.join(application.root_path, "static", "image", "myprofile")
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, filename)
        uploaded.save(save_path)

        update_data["profile_img"] = f"image/myprofile/{filename}"
    
    
    #-- DB에 업데이트
    DB.update_user(user_id, update_data)
    session["username"] = username
    
    flash("회원 정보가 수정되었습니다.", "success")
    return redirect(url_for("mypage_index"))

# ----------------------------------------------------


# 로그인 / 회원가입
@application.route("/login")
def login():
    return render_template("auth/login.html")

@application.route("/", methods=['POST'])
def login_user():
    id_=request.form['id']
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.find_user(id_,pw_hash):
        session['id']=id_
        return redirect(url_for('home'))
    else:
        flash("아이디 혹은 비밀번호가 틀렸습니다.")
        return render_template("auth/login.html")

@application.route("/signup")
def signup():
    return render_template("auth/signup.html")

@application.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_confirm=request.form['pw_confirm']

    #비밀번호 일치 확인
    if pw != pw_confirm:
        flash("비밀번호가 일치하지 않습니다.")
        return render_template("auth/signup.html")
    #해싱
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

    if DB.insert_user(data,pw_hash):
        return render_template("auth/login.html")
    else:
        flash("이미 존재하는 아이디입니다.")
        return render_template("auth/signup.html")

@application.route("/logout")
def logout_user():
    session.clear()
    return redirect(url_for('home'))



# ----------------------------------------------------
# 상품 등록 POST 처리 함수
# ----------------------------------------------------
@application.route("/reg_item_submit_post", methods=['POST'])
def reg_item_submit_post():
    # 로그인 확인
    if "id" not in session:
        return redirect(url_for("login"))

    # 1. 이미지 파일 받기
    image_file = request.files.get("productImage")
    data = request.form
    product_name = data.get('productName')
    seller_id = session.get('id')
    
    # 2. 이미지 저장
    if image_file and image_file.filename != "":
        file_ext = os.path.splitext(image_file.filename)[1]
        secure_name = str(uuid.uuid4()) + file_ext 
        
        save_path = os.path.join(application.config['UPLOAD_FOLDER'], secure_name)
        image_file.save(save_path)
        
        img_path = secure_name
    else:
        img_path = "default.png"

    # 3. DB 저장 함수 호출
    product_name = data.get('productName')
    seller_id = session.get('id')  # 세션에서 판매자 ID 가져오기
    
    # DB 함수 호출 시 seller_id를 추가로 전달
    if DB.insert_item(product_name, data, img_path, seller_id):
        flash(f"상품 '{product_name}' 등록이 완료되었습니다.")
        return redirect(url_for('products_enroll'))
    else:
        flash("상품 등록에 실패했습니다.")
        return redirect(url_for('products_enroll'))

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=5001, debug=True)
