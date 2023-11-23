import psycopg2
import re

class User:
    def __init__(self, user_id, user_name, user_role):
        self.user_id = user_id
        self.user_name = user_name
        self.user_role = user_role

g_current_user = None

def print_welcome_menu():
    """
    welcome 메뉴 출력
    """
    while 1:
        print("---------------------\n"
              "Welcome to 뭐먹지?\n"
              "Choose Menu\n"
              "1. login\n"
              "2. sign in\n"
              "3. Quit.\n")
        result = input("메뉴 선택: ")
        return result

def sign_in(cursor):
    """
    로그인
    입력 받은 계정과 암호를 DB에서 조회 하여 로그인
    로그인 성공시 g_current_user 갱신.
    """
    global g_current_user
    print("----로그인----")
    input_username = input("계정: ")
    input_password = input('암호: ')

    # 사용자 계정과 암호로 조회
    cursor.execute("select * from users where user_name = %s and user_pw = %s", (input_username, input_password))
    result = cursor.fetchall()

    if result:
        print("로그인 성공!")
        g_current_user = User(result[0][0], result[0][1], result[0][3])
    else:
        print("로그인 실패. 계정 또는 암호를 확인하세요.")

def is_valid_password(password):
    """
    암호 조건 충족 여부 확인 함수
    :param password: 입력 받은 암호
    조건 : 최소 8자 이상, 공백 미포함
    :return: 사용 가능한 암호면 true / 사용 불가한 암호면 false
    """
    pattern = re.compile(r'^(?=.*[a-zA-Z\d@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    return bool(re.match(pattern, password))

def sign_up(cursor):
    """
    회원 가입
    권한에 따른 역할 부여 -> 암호:im~
    계정 중복 여부 확인
    암호 조건 충족 여부 확인 후 회원 가입 진행
    """
    print("----회원가입----")
    while 1:
        input_role = input("권한(1: 고객, 2: 사장, 3: 관리자): ")
        if input_role not in ("1", "2", "3"):
            print("1, 2, 3 중 선택해주세요.")
        else:
            role_mapping = {'1': 'user', '2': 'owner', '3': 'admin'}
            break
    input_username = input("계정: ")
    # 사용자 계정 중복 확인
    cursor.execute("select * from users where user_name = %s", (input_username,))
    existing_user = cursor.fetchone()
    if existing_user:
        print("이미 존재하는 계정입니다. 다른 계정을 선택해주세요.")
        return

    input_password = input("암호: ")
    # 암호 조건 확인
    if not is_valid_password(input_password):
        print("암호가 조건을 만족하지 않습니다.")
        return

    if input_role == "2":
        # 사장일 경우
        input_owner_password = input("사장 암호를 입력하세요: ")
        if input_owner_password != 'imowner':
            print("사장 암호가 일치하지 않습니다. 회원가입을 종료합니다.")
            return
    elif input_role == "3":
        # 관리자일 경우
        input_admin_password = input("관리자 암호를 입력하세요: ")
        if input_admin_password != 'imadmin':
            print("관리자 암호가 일치하지 않습니다. 회원가입을 종료합니다.")
            return
    db_role = role_mapping.get(input_role)
    cursor.execute("insert into users (user_name, user_pw, role) values (%s, %s, %s)", (input_username, input_password, db_role))
    con.commit()  # 변경사항 저장
    print("회원가입이 완료되었습니다.")

def user_menu():
    """
    고객이 사용할 수 있는 메뉴 출력
    """
    print("----------------------------\n"
          "유저가 사용할 수 있는 메뉴입니다.\n"
          f"hello user {g_current_user.user_name}\n")

def owner_menu():
    """
    사장이 사용할 수 있는 메뉴 출력
    """
    print("----------------------------\n"
          "사장이 사용할 수 있는 메뉴입니다.\n"
          f"hello owner {g_current_user.user_name}\n")


def admin_menu():
    """
    관리자가 사용할 수 있는 메뉴 출력
    :return:
    """
    print("----------------------------\n"
          "관리자가 사용할 수 있는 메뉴입니다.\n"
          f"hello admin {g_current_user.user_name}\n")

con = psycopg2.connect(
    database='mmg',
    user='sjlee',
    password='sjlee!2023',
    host='::1',
    port='5432'
)

cursor = con.cursor()

print("current db state: ")
cursor.execute("select * from users")
result = cursor.fetchall()
for r in result:
    print(r)

while 1:
    m = print_welcome_menu()
    if m == "1":
        sign_in(cursor)
        if g_current_user is not None: break
    elif m == "2":
        sign_up(cursor)
    elif m == "3":
        print("Bye")
        break
    else:
        print("Invalid Option!")

if g_current_user.user_role == "user":
    user_menu()
elif g_current_user.user_role == "owner":
    owner_menu()
elif g_current_user.user_role == "admin":
    admin_menu()