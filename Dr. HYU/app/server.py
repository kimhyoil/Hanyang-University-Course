from flask import Flask, render_template, request
from db import search_customerInfo, insert_customerInfo, set_type, get_hosp_list, visited_record
from db import add_favorite_hospital, update_hospInfo_table, update_pharmInfo_table, get_pharm_list
from db import get_favorite_hospital_list, add_reservation, get_hospital_name, reservation_list
from db import cancel_reservation
import json
from pprint import pprint
# from apicall import hosp_list, pharm_list

app = Flask(__name__)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# 로그인 화면
@app.route('/')
def index():            
    return render_template("sign-in.html")       

# 로그인 정보가 올바른지 확인
@app.route("/sign-in", methods=["GET", "POST"])                        
def sign_in():           
    email = request.form.get('email')
    tmp = email.split('@')
    local = tmp[0]
    print(tmp)
    domain = tmp[1]
    password = request.form.get('password')
    res = search_customerInfo(local, domain, password)
    print(res)
    if res == []: return "회원정보가 없습니다. 회원가입을 해주세요."
    if res[0][0] == "patient": return render_template("patient-main.html")
    if res[0][0] == "hospital": return render_template("hospital-main.html")
    if res[0][0] == "pharmacy" : return render_template("pharmacy-main.html")
    return "error"
    #  res의 type종류에 따라 다른 화면 송출
    #  type이 없다면 설정
    #  login data가 없다면 alert  

# 회원가입 화면
@app.route('/sign-up')
def sing_up():
    return render_template("sign-up.html")    

# 입력받은 정보를 고객목록에 추가(회원가입)
@app.route('/add-customer', methods=["GET", "POST"])
def add_customer():
    req = request.get_json()
    email = req['email']
    tmp = email.split('@')
    local = tmp[0]
    tmp = tmp[1].split('\n')
    domain = tmp[0]
    password = req['password']
    name = req['name']
    phone_number = req['phone_number']
    type = req['type']
    tmp = insert_customerInfo(name, phone_number, local, domain, password, type)
    if tmp == "회원정보존재":
        return "가입실패"
    else:
        return "가입성공"

#환자 메인 페이지로 이동
@app.route('/patient-main')
def patient():            
    return render_template("patient-main.html")   

@app.route('/hospital_list', methods=["POST"])
def hospital_list():
    # lat lng 필요
    req = request.get_json()
    lat = req["lat"]
    lng = req["lng"]
    res = update_hospInfo_table(lat, lng)
    if res == -1: return -1;
    list = get_hosp_list()
    return json.dumps(list)

@app.route('/pharmacy_list', methods=["POST"])
def pharmacy_list():
    req = request.get_json()
    lat = req["lat"]
    lng = req["lng"]
    res = update_pharmInfo_table(lat, lng)
    if res == -1: return -1;
    list = get_pharm_list()
    return json.dumps(list)

@app.route('/patient-privacy-info', methods=["POST"])
def patient_privacy_info():
    email = request.get_json()
    local = email['local']
    domain = email['domain']
    return json.dumps(visited_record(local, domain))

@app.route('/add_favorite', methods=["POST"])
def add_favorite():
    req = request.get_json()
    name = req['hospital_name']
    local = req['local']
    domain = req['domain']
    add_favorite_hospital(name, local, domain)
    return json.dumps(get_favorite_hospital_list(local, domain))

@app.route('/add_reservation', methods=["POST"])
def add_reservation_info():
    name = request.form.get('name')
    phone_number = request.form.get('phone_number')
    date = request.form.get('date')
    institution = request.form.get('institution_name')
    add_reservation(name, phone_number, date, institution) 
    return render_template("patient-main.html")

# 병원관리자가 예약 list를 보는 것
@app.route('/reservation_list', methods=["POST"])
def reservation_patient():
    req = request.get_json()
    local = req['local']
    domain = req['domain']
    tmp = get_hospital_name(local, domain)
    print("병원이름")
    print(tmp)
    if(tmp == []):
        print("xxxx")
        return tmp
    institution_name = tmp[0][0]
    return json.dumps(reservation_list(institution_name))
    
@app.route('/cancel_reservation', methods=["POST"])
def delete_reservation():
    print("cancel")
    req = request.get_json()
    local = req['local']
    domain = req['domain']
    phone_number = req['phone_number']
    date = req['date']
    tmp = get_hospital_name(local, domain)
    institution_name = tmp[0][0]
    cancel_reservation(institution_name, phone_number, date)
    print("cancel")
    
    return json.dumps(reservation_list(institution_name))   #취소하고 다시 reload

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

if __name__ == ("__main__"):
  app.run(debug=True, host='0.0.0.0', port=5000)