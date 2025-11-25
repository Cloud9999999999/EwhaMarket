from flask import Flask, render_template, flash, redirect, url_for, session, request
from database import DBhandler
import hashlib
import sys
import os
import math

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

# 리뷰 상세 
@application.route("/reviews/detail")
def reviews_detail():
    return render_template("reviews/detail.html")

# 상품 등록
@application.route("/products/enroll")
def products_enroll():
    return render_template("products/enroll.html")

# 상품 상세
@application.route("/products/detail/<name>")
def products_detail(name):
    data = DB.get_item_byname(str(name))
    return render_template("products/detail.html", name=name, data=data)

# 마이페이지
@application.route("/mypage")
def mypage_index():
    return render_template("mypage/index.html")

# 마이페이지-2 수정
@application.route("/mypage/edit-info", methods=['POST'])
def mypage_edit():
    username = request.form.get('username')
    user_id = session.get('id')
    email = request.form.get('email')
    number = request.form.get('number')
    password = request.form.get('password')
    checkpw = request.form.get('checkpw')
    
    error = []
    
    if not username:
        error.append("이름을 입력해주세요.")
    if not user_id:
        error.append("아이디를 입력해주세요.")
    if not email:
        error.append("이메일을 입력해주세요.")
    if not number:
        error.append("전화번호를 입력해주세요.")
    if not password:
        error.append("비밀번호를 입력해주세요.")
    
    if password != checkpw:
        error.append("비밀번호와 비밀번호 확인이 일치하지 않습니다.")
    
    
    if error:
        for msg in error:
            flash(msg)
        return render_template("index.html", username=username, user_id=user_id, email=email, number=number)
    
    
    # 실제 사용자 찾기
    user = db.child("users").child(user_id).get().val()
    if user is None:
        flash("해당 사용자를 찾을 수 없습니다.", "error")
        return redirect(url_for("index"))
    
    # DB 업데이트
    update_data = {
        "username": username,
        "email": email,
        "number": number,
        "password": password
    }
    
    db.child("users").child(user_id).update(update_data)

    flash("회원 정보가 수정되었습니다.", "success")
    return redirect(url_for("index"))
    
    
    #return render_template("mypage/edit-info.html")





# 로그인 / 회원가입
@application.route("/login")
def login():
    return render_template("auth/login.html")

@application.route("/login_confirm", methods=['POST'])
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

if __name__ == "__main__":
    application.run(host="0.0.0.0", debug=True)


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