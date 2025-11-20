import pyrebase
import json
class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f:
            config=json.load(f)
        firebase = pyrebase.initialize_app(config)
        self.db = firebase.database()
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