import pyrebase
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "databaseURL": os.getenv("FIREBASE_DB_URL"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID")
}


class DBhandler:
    def __init__(self):
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
        
    # ----------------------------------------------------
    # 회원 관련 함수
    # ----------------------------------------------------
    #회원 추가
    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "email": data['email'],
            "username" : data['username'],
            "number": data['number']
        }
        
        #중복체크
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            return True
        else:
            return False

        #중복체크
    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        
        if str(users.val()) == "None": 
            return True
        else:
            for res in users.each():
                value = res.val()
                user_id = value.get('id')
                if user_id is None:
                    continue
                if user_id == id_string:
                    return False
        return True
    
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        if str(users.val()) == "None":
            return False

        for res in users.each():
            value = res.val()
            user_id = value.get('id')
            user_pw = value.get('pw')
            if user_id is None or user_pw is None:
                continue
            if user_id == id_ and user_pw == pw_:
                return True
            
        return False
    
    # ----------------------------------------------------
    # 상품 관련 함수
    # ----------------------------------------------------
    def insert_item(self, name, data, img_path):
        city = data.get('city', '')
        district = data.get('district', '')
        full_addr = f"{city} {district}".strip()

        item_info = {
            "seller": data.get('sellerId'),
            "addr": full_addr,
            "category": data.get('category'),
            "price": data.get('price'),
            "status": data.get('status', '새 상품'),
            "description": data.get('description'),
            "img_path": img_path
        }
        
        self.db.child("item").child(name).set(item_info)
        
        print(f"Item Saved: {name}")
        return True
    
    def get_items(self):
        items = self.db.child("item").get().val()
        return items
    
    def get_item_byname(self, name):
        items = self.db.child("item").get()
        target_value=""
        for res in items.each():
            key_value = res.key()
            if key_value == name:
                target_value=res.val()
        return target_value
    
    
    # ----------------------------------------------------
    # 마이페이지
    # ----------------------------------------------------
    # 회원 정보/사용자 관련
    def get_user(self, user_id: str):
        users = self.db.child("user").get()
        if not users.val():
            return None

        for res in users.each():
            value = res.val()
            if value.get("id") == user_id:
                return value

        return None
    
    def update_user(self, user_id: str, data: dict):
        users = self.db.child("user").get()
        if not users.val():
            return False

        for res in users.each():
            key = res.key()
            value = res.val()
            if value.get("id") == user_id:
                self.db.child("user").child(key).update(data)
                return True

        return False
    
    # 회원 정보 수정
    

    # ----------------------------------------------------
    # 리뷰 관련 함수
    # ----------------------------------------------------
    def insert_review(self, review_data):
        self.db.child("reviews").push(review_data)
        return True
    def get_all_reviews(self):
        return self.db.child("reviews").get().val()

    def get_review_by_id(self, rid):
        return self.db.child("reviews").child(rid).get().val()

    def get_review_by_id(self, review_id): #상세조회용 함수
        reviews = self.db.child("reviews").get()

        if not reviews.val():
            return None

        for r in reviews.each():
            if r.key() == review_id:
                return r.val()

        return None