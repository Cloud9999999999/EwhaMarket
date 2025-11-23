from flask import Flask, render_template,flash, redirect, url_for, session, request
from database import DBhandler
import hashlib
import sys
application = Flask(__name__)
application.config["SECRET_KEY"] = "helloosp"
DB = DBhandler()
# 홈
@application.route("/")
def home():
    return render_template("index.html")

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
@application.route("/products/detail")
def products_detail():
    return render_template("products/detail.html")

# 마이페이지
@application.route("/mypage")
def mypage_index():
    return render_template("mypage/index.html")

# 마이페이지 수정
@application.route("/mypage/edit")
def mypage_edit():
    return render_template("mypage/edit-info.html")

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
