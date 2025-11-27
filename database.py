import pyrebase
import json

class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)
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
            "email": data['email'] 
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
                if value['id'] == id_string:
                    return False
    
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        if str(users.val()) == "None":
            return False

        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
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
        return self.db.child("user").child(user_id).get().val()
    
    def update_user(self, user_id: str, data: dict):
        return self.db.child("user").child(user_id).update(data)

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

