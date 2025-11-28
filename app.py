from flask import Flask, render_template, flash, redirect, url_for, session, request
from database import DBhandler
import hashlib
import sys
import os
import math
from datetime import datetime             
import uuid                                
from werkzeug.utils import secure_filename


application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "image")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DB = DBhandler()

# 홈
@application.route("/")
def home():
    page = request.args.get("page", 0, type=int)

    # 1. DB에서 데이터 가져오기
    data = DB.get_items()
    if data is None:
        data = {}

    # 2. 전체 상품 수 및 페이지 수 계산
    item_counts = len(data)
    per_page = 8
    page_count = math.ceil(item_counts / per_page)

    # 3. 데이터 슬라이싱 (page 변수 사용)
    start_idx = per_page * page
    end_idx = per_page * (page + 1)

    data_list = list(data.items())
    current_page_data = data_list[start_idx:end_idx]

    # 4. 템플릿 렌더링
    return render_template(
        "index.html",
        datas=current_page_data,
        page=page,
        page_count=page_count,
        total=item_counts,
        limit=per_page
    )

# 리뷰 목록
@application.route("/reviews")
def reviews_index():
    return render_template("reviews/index.html")

# 리뷰 작성
@application.route("/reviews/write")
def reviews_write():
    return render_template("reviews/write-review.html")

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

    # ★ 로그인 필요 시 사용
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

    return jsonify({"success": True})
    
# 리뷰 상세 조회
@application.route("/reviews/detail/<review_id>")
def review_detail(review_id):

    review = DB.get_review_by_id(review_id)

    if not review:
        return "리뷰를 찾을 수 없습니다.", 404

    return render_template("reviews/detail.html", review=review)


# 상품 등록
@application.route("/products/enroll")
def products_enroll():
    return render_template("products/enroll.html")

# 상품 상세
@application.route("/products/detail/<name>")
def products_detail(name):
    data = DB.get_item_byname(str(name))

    user_id = session.get("id")
    is_favorite = False
    if user_id:
        is_favorite = DB.is_favorite(user_id, str(name))

    return render_template(
        "products/detail.html",
        name=name,
        data=data,
        is_favorite=is_favorite,
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

    return render_template("mypage/index.html", user=user)


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
    DB.update_user(user_id, update_data)
    session["username"] = username
    
    flash("회원 정보가 수정되었습니다.", "success")
    return redirect(url_for("mypage_index"))

# (->다시 수정들어가면 이전 정보가 안뜸.. firebase에 업데이트는 되어있음. 로그인을 안해서??)
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
    # 1. 이미지 파일 받기
    image_file = request.files.get("productImage")
    data = request.form
    
    # 2. 이미지 저장
    if image_file and image_file.filename != "":
        filename = image_file.filename
        save_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
        image_file.save(save_path)
    else:
        filename = "default.png"

    # 3. DB 저장 함수 호출
    product_name = data.get('productName')
    
    if DB.insert_item(product_name, data, filename):
        flash(f"상품 '{product_name}' 등록이 완료되었습니다.")
        return redirect(url_for('products_enroll'))
    else:
        flash("상품 등록에 실패했습니다.")
        return redirect(url_for('products_enroll'))

if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True)
