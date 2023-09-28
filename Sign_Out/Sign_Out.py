import cv2
import pytesseract
import mysql.connector
import re
from datetime import datetime, timedelta
import subprocess as s
import webbrowser
import time
import pyautogui
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import threading
from selenium import webdriver
import psutil
import pygetwindow as gw
from tkinter import Tk, simpledialog
pytesseract.pytesseract.tesseract_cmd = r'C:\\Tesseract\\tesseract.exe'
money = False
manual_payment = False
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dpsbn",
    database="cars")
import qrcode
from urllib.parse import urlencode, quote
def adddup():
    import mysql.connector as ms
    db = ms.connect(
    host="localhost",
    user="root",
    password="dpsbn",
    database="cars")
    import datetime
    today = datetime.date.today()
    ll=today.strftime("%Y-%m-%d")
    print(ll)
    cursor=db.cursor()
    q1="INSERT INTO rep (car_number,timestamp,money_paid) VALUES (%s,%s,%s)"
    v1=(car_number,ll,total_charge)
    cursor.execute(q1,v1)
    db.commit()
    db.close()
def get_manual_car_number():
    root = Tk()
    root.withdraw()
    car_number = simpledialog.askstring("Car Number", "Enter the car number:")
    return car_number
def generate_qr_code(car_number, money):
    # Encode car number and money as URL parameters
    params = {'car_number': car_number, 'money': money}
    url = 'https://eazepark.repl.co/?' + urlencode(params, quote_via=quote)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save('C:\EazePark\Sign_Out\qr.png')
dbno=[]
payment_event=False
def delete_car_number(car_number):
    cursor = db.cursor()
    query = "DELETE FROM car_no WHERE car_number = %s"
    cursor.execute(query, (car_number,))
    db.commit()
def is_edge_running():
    payment_confirmation_windows = [window for window in gw.getWindowsWithTitle('') if 'Payment Confirmation' in window.title]
    return len(payment_confirmation_windows) > 0
rr=False
def payment_verification():
    global rr
    global car_number_em
    global money_paid
    import imaplib
    import email
    import re
    username = "ineazepark@gmail.com"
    password = "hqkoabclvofhqlxt"
    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(username, password)
    mailbox = "inbox"
    mail.select(mailbox)
    status, email_ids = mail.search(None, "ALL")
    email_id_list = email_ids[0].split()[::-1]
    def extract_car_number_and_money_paid(email_content):
        global rr
        car_number_em = ""
        money_paid = ""
        car_number_match = re.search(r"Car Number: ([\w\s]+)(?=\s*Money Paid:|$)", email_content)
        money_paid_match = re.search(r"Money Paid: (\d+)", email_content)
        if car_number_match:
            car_number_em = car_number_match.group(1)
        if money_paid_match:
            money_paid = money_paid_match.group(1)
        return car_number_em.strip(), money_paid.strip()
    for email_id in email_id_list:
        status, email_data = mail.fetch(email_id, "(BODY[TEXT])")
        email_message = email.message_from_bytes(email_data[0][1])
        email_content = email_message.get_payload()
        car_number_em, money_paid = extract_car_number_and_money_paid(email_content)
        print(car_number_em,money_paid)
        print(car_number,total_charge)
        if car_number == car_number_em and money_paid == str(total_charge):
            rr = True
        break
    mail.logout()
    print(rr)
def prompt_manual_payment():
    global manual_payment
    answer = input("Was the payment made manually? (y/n): ").lower()
    if answer == 'y':
        manual_payment = True
def extract_car_number(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    thresholded = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    car_number = pytesseract.image_to_string(thresholded)
    return car_number.strip()
def calculate_charges(timestamp):
    current_time = datetime.now()
    time_difference = current_time - timestamp
    total_hours = int((time_difference.total_seconds() + 3599) / 3600)
    base_charge = 30
    additional_charge_per_hour = 10
    total_charge = base_charge + max(total_hours - 2, 0) * additional_charge_per_hour
    return total_hours, total_charge
car_number_detected = False
state_patterns = {
    'AN': r'AN\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Andaman and Nicobar Islands
    'AP': r'AP\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Andhra Pradesh
    'AR': r'AR\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Arunachal Pradesh
    'AS': r'AS\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Assam
    'BR': r'BR\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Bihar
    'CH': r'CH\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Chandigarh
    'CT': r'CT\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Chhattisgarh
    'DD': r'DD\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Dadra and Nagar Haveli and Daman and Diu
    'DL': r'DL\s\d{1,2}\s[A-Z]{1,2}\s\d{4}$',  # Delhi
    'DN': r'DN\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Dadra and Nagar Haveli and Daman and Diu
    'GA': r'GA\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Goa
    'GJ': r'GJ\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Gujarat
    'HP': r'HP\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Himachal Pradesh
    'HR': r'HR\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Haryana
    'JH': r'JH\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Jharkhand
    'JK': r'JK\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Jammu and Kashmir
    'KA': r'KA\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Karnataka
    'KL': r'KL\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Kerala
    'LA': r'LA\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Ladakh
    'LD': r'LD\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Lakshadweep
    'MH': r'MH\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Maharashtra
    'ML': r'ML\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Meghalaya
    'MN': r'MN\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Manipur
    'MP': r'MP\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Madhya Pradesh
    'MZ': r'MZ\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Mizoram
    'NL': r'NL\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Nagaland
    'OD': r'OD\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Odisha
    'PB': r'PB\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Punjab
    'PY': r'PY\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Puducherry
    'RJ': r'RJ\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Rajasthan
    'SK': r'SK\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Sikkim
    'TN': r'TN\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Tamil Nadu
    'TR': r'TR\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Tripura
    'TS': r'TS\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Telangana
    'UK': r'UK\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Uttarakhand
    'UP': r'UP\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # Uttar Pradesh
    'WB': r'WB\s\d{2}\s[A-Z]{1,2}\s\d{4}$',  # West Bengal
}
all_states_pattern = '|'.join(state_patterns.values())
all_regex = re.compile(all_states_pattern)
cap = cv2.VideoCapture(0)
manual_entry = False
while True:
    ret, frame = cap.read()    
    if not ret:
        break
    if manual_entry:
        manual_car_number = get_manual_car_number()
        if manual_car_number:
            car_number = manual_car_number.strip()
            print("Manual Car Number:", car_number)
            manual_entry = False  # Disable manual entry mode
    else:
        car_number = extract_car_number(frame)
        print("OCR Output:", car_number)
    if car_number and all_regex.match(car_number):
        cursor = db.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        query = "SELECT * from car_no where car_number=%s"
        cursor.execute(query, (car_number,))
        result = cursor.fetchone()
        payment_confirmation_event = threading.Event()
        if result:
            print("Detected Car Number:", car_number)
            db_timestamp = result[1]
            total_hours, total_charge = calculate_charges(db_timestamp)
            print(f"Total Hours: {total_hours}")
            print(f"Total Charges: {total_charge} Rs")
        break
    cv2.imshow('Car Number Detection', frame)
    key = cv2.waitKey(1)
    if key & 0xFF == ord('q') or car_number_detected:
        break
    if key == ord('m') or key==ord('M'):
        manual_entry = True
cap.release()
cv2.destroyAllWindows()
cursor.execute('select * from car_no')
a = cursor.fetchall()
for i in a:
    for j in i:
        dbno.append(j)
        break
if car_number not in dbno:
    s.run(["python","C:\\EazePark\\Sign_Out\\Sign_Out.py"])
money=str(total_charge)
generate_qr_code(car_number, money)
html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Payment Confirmation</title>
    <link rel="icon" href="static/favicon.ico">
    <style>
        body {{
            background-color: black;
            color: white;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        h1 {{
            font-size: 24px;
        }}
        p {{
            font-size: 18px;
        }}
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .content {{
            max-width: 80%;
        }}
        img {{
            max-width: 100%;
            height: auto;
            margin-top: 20px;
        }}
        button#confirmBtn {{
            background-color: blue;
            color: white;
            font-size: 20px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="content">
            <h1>Car Number and Charges</h1>
            <p>Car Number: {car_number}</p>
            <p>Total Charges: {total_charge} Rs</p>
            <img src="qr.png" alt="Car Image">
        </div>
    </div>
</body>
</html>
"""
import threading
def website():
    global money
    with open("C:\\EazePark\\Sign_Out\\payment_confirmation.html", "w") as html_file:
        html_file.write(html_content)
    time.sleep(3)
    import http.server
    import socketserver
    import webbrowser
    money = False
    class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            global money
            if "/payment_status" in self.path:
                money = True
                self.send_response(200)
                self.end_headers()
                return
            elif "/stop_server" in self.path:
                self.send_response(200)
                self.end_headers()
                self.server.shutdown()
            else:
                self.directory = "C:\\EazePark\\Sign_Out"
                super().do_GET()
    handler = MyRequestHandler
    port = 8080
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        webbrowser.open(f"http://localhost:8080/payment_confirmation.html")
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.start()
        while not rr:
            payment_verification()
            if rr:
                windows = [window for window in gw.getWindowsWithTitle('') if 'Payment Confirmation' in window.title]
                httpd.shutdown()
                money=True
                if windows:
                    windows[0].close()
    print(money)
website()
if money:
    adddup()
    time.sleep(5)
    payment_verification()
    if car_number_em==car_number and int(money_paid)==total_charge:
        payment_event=True
        driver=webdriver.Chrome()
        driver.get('file:///C:/EazePark/Sign_Out/templates/thank_you.html')
        import pygetwindow as gw
        window = gw.getWindowsWithTitle('Thank You - Google Chrome')[0]
        window.maximize()
        time.sleep(5)
        driver.quit()
    elif car_number_em==car_number and int(money_paid)!=total_charge:
        driver=webdriver.Chrome()
        driver.get('file:///C:/EazePark/Sign_Out/templates/moneyerr.html')
        import pygetwindow as gw
        window = gw.getWindowsWithTitle('Payment Error - Google Chrome')[0]
        window.maximize()
        time.sleep(20)
        driver.quit()
        website()
        payment_verification()
    elif car_number_em!=car_number:
        website()
        payment_verification()
    if payment_event:
        delete_car_number(car_number)
        s.run(["python","C:\\EazePark\\Sign_Out\\Sign_Out.py"])
    else:
        website()
        payment_verification()