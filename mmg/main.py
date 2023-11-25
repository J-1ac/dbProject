import psycopg2
import re

con = psycopg2.connect(
        database='mmg',
        user='sjlee',
        password='sjlee!2023',
        host='::1',
        port='5432'
    )

class User:
    def __init__(self, user_id, user_name, user_pw, user_role):
        self.user_id = user_id
        self.user_name = user_name
        self.user_pw = user_pw
        self.user_role = user_role

g_current_user = None

def print_welcome_menu():
    """
    welcome 메뉴 출력
    """
    print("---------------------\n"
          "Welcome to 뭐먹지?\n"
          "Choose Menu\n"
          "1. login\n"
          "2. sign in\n"
          "3. Quit.\n")
    return input("메뉴 선택: ")

def sign_in():
    """
    로그인
    입력 받은 계정과 암호를 DB에서 조회 하여 로그인
    로그인 성공시 g_current_user 갱신.
    """
    global g_current_user
    global con
    cursor = con.cursor()
    print("----로그인----")
    input_username = input("계정: ")
    input_password = input('암호: ')

    # 사용자 계정과 암호로 조회
    cursor.execute("select * from users where user_name = %s and user_pw = %s", (input_username, input_password))
    result = cursor.fetchall()

    if result:
        print("로그인 성공!")
        g_current_user = User(result[0][0], result[0][1], result[0][2], result[0][3])
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

def sign_up():
    """
    회원 가입
    권한에 따른 역할 부여 -> 암호:im~
    계정 중복 여부 확인
    암호 조건 충족 여부 확인 후 회원 가입 진행
    """
    global con
    cursor = con.cursor()
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
        print("암호는 8자 이상 영문 혹은 숫자, 특수기호이어야 하며, 공백을 포함해서는 안됩니다.")
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


def check_user():
    global g_current_user
    # 사용자 ID 및 비밀번호 확인
    input_user_name = input("현재 사용자 계정: ")
    input_password = input("암호: ")
    if input_user_name != g_current_user.user_name or input_password != g_current_user.user_pw:
        print("잘못된 사용자 ID 또는 비밀번호입니다.")
        return False

    # 올바른 사용자 ID 및 비밀번호인 경우
    print("현재 사용자 계정과 암호가 확인되었습니다.")
    return True

def is_unique_user_name(cursor, new_user_name):
    """
        새로운 사용자 계정이 unique한지 확인하는 함수
        :param cursor: 데이터베이스 커서
        :param new_user_name: 새로운 사용자 계정
        :return: unique하면 True, 중복이면 False
        """
    global con
    cursor = con.cursor()
    cursor.execute("select * from users where user_name = %s", (new_user_name,))
    existing_user = cursor.fetchone()
    return existing_user is None

def change_name():
    print("----계정 변경----")
    global g_current_user
    global con
    cursor = con.cursor()

    if not check_user():
        return

    while 1:
        # 새로운 사용자 계정이 입력
        new_user_name = input("새로운 사용자 ID: ")
        # 새로운 사용자 계정이 현재 사용자 ID와 동일한지 확인
        if new_user_name == g_current_user.user_name:
            print("현재 사용자 계정과 동일합니다. 다시 입력해주세요.")
        elif not is_unique_user_name(cursor, new_user_name):
            print("이미 존재하는 계정입니다. 다른 계정을 입력해주세요.")
        else:
            # 동일하지 않은 경우 데이터베이스 업데이트
            cursor.execute("update users set user_name = %s where user_id = %s", (new_user_name, g_current_user.user_id))
            print("사용자 계정이 성공적으로 변경되었습니다.")
            # 변경사항 저장
            con.commit()
            g_current_user.user_name = new_user_name
            return


def change_pw():
    print("----암호 변경----")
    global g_current_user
    global con
    cursor = con.cursor()

    if not check_user():
        return

    while 1:
        # 새로운 암호 입력
        new_user_pw = input("새로운 암호: ")
        # 유효성 검사: 암호는 8자 이상 영문 혹은 숫자, 특수기호이어야 하며, 공백을 포함해서는 안됨
        if new_user_pw == g_current_user.user_pw:
            print("현재 사용자 암호와 동일합니다. 다시 입력해주세요.")
        elif not is_valid_password(new_user_pw):
            print("암호는 8자 이상 영문 혹은 숫자, 특수기호이어야 하며, 공백을 포함해서는 안됩니다. 다시 입력하세요.")
        else:
            # 동일하지 않은 경우 데이터베이스 업데이트
            cursor.execute("update users set user_pw = %s where user_id = %s", (new_user_pw, g_current_user.user_id))
            print("사용자 암호가 성공적으로 변경되었습니다.")
            # 변경사항 저장
            con.commit()
            g_current_user.user_pw = new_user_pw
            break

def change_user():
    while 1:
        print("회원 정보 변경 메뉴입니다.\n"
              "1. 계정 변경\n"
              "2. 암호 변경\n"
              "3. 종료\n")
        user_input = input("메뉴 선택: ")
        if user_input == "1":
            change_name()
        elif user_input == "2":
            change_pw()
        elif user_input == "3":
            print("Bye")
            break
        else:
            print("Invalid Option! 1, 2, 3 중 선택해주세요.")


def find_restaurant():
    global con
    cursor = con.cursor()
    # TODO - 조회 순서 추가(평점순, 대기시간순...)
    print("가게 조회 메뉴입니다.\n")
    cursor.execute("select * from restaurants")
    restaurants = cursor.fetchall()

    print("가게 목록:")
    for restaurant in restaurants:
        print(f"가게번호: {restaurant[0]}, 가게이름: {restaurant[2]}, 주소: {restaurant[3]}, 평점: {restaurant[4]}")

    # 가게 선택 로직 추가
    selected_restaurant_id = input("가게의 세부정보를 보려면, 원하는 가게의 번호를 입력하세요 (종료: 0): ")

    if selected_restaurant_id == "0":
        print("가게 조회를 종료합니다.")
        return

    # 선택한 가게의 상세 정보 조회 및 출력
    cursor.execute("select * from restaurants where restaurant_id = %s", (selected_restaurant_id,))
    selected_restaurant = cursor.fetchone()
    cursor.execute("select count(*) from waitings where restaurant_id = %s", (selected_restaurant_id,))
    waiting_count = cursor.fetchone()[0]

    if selected_restaurant:
        print("---선택한 가게 정보---\n"
                f"가게 ID: {selected_restaurant[0]}\n"
                f"가게 이름: {selected_restaurant[2]}\n"
                f"가게 주소: {selected_restaurant[3]}\n"
                f"가게 평점: {selected_restaurant[4]}\n"
                f"현재 대기열: {waiting_count}\n"
                f"예상 대기 시간: {waiting_count*5+5}분\n")
        join_queue = input("대기열에 참가하시겠습니까? (참가: 1, 거부: 0): ")
        if join_queue == "1":
            cursor.execute("select * from waitings where user_id = %s", (g_current_user.user_id,))
            existing_entry = cursor.fetchone()
            if existing_entry:
                print("이미 다른 가게의 대기열에 참가 중입니다. 참가할 수 없습니다.")
            else:
                # 사용자의 우선순위 계산
                cursor.execute("select max(priority) from waitings where restaurant_id = %s", (selected_restaurant[0],))
                max_priority = cursor.fetchone()[0]

                if max_priority is None:
                    priority = 1
                else:
                    priority = max_priority + 1

                # 대기열 테이블에 사용자 추가
                cursor.execute("insert into waitings (user_id, restaurant_id, priority) values (%s, %s, %s)", (g_current_user.user_id, selected_restaurant[0], priority))
                con.commit()
        else:
            print("대기열 참가를 거부하셨습니다.")
    else:
        print("유효하지 않은 가게 번호입니다.")


def leave_waiting_queue(restaurant_id, priority):
    global con
    cursor = con.cursor()
    # 대기열에서 나가는 동작
    cursor.execute("delete from waitings where user_id = %s", (g_current_user.user_id,))
    con.commit()

    # 해당 유저보다 우선순위가 낮은 유저들의 우선순위를 1씩 감소시킴
    cursor.execute("update waitings set priority = priority - 1 where restaurant_id = %s and priority > %s", (restaurant_id, priority))
    con.commit()
    print("대기열에서 나가셨습니다.")


def check_waiting():
    global con
    cursor = con.cursor()
    print("대기열 조회 메뉴입니다.\n")
    cursor.execute("select w.user_id, w.restaurant_id, w.priority, r.restaurant_name, r.restaurant_address, r.avg_rating "
                    "from waitings w join restaurants r on w.restaurant_id = r.restaurant_id "
                    "where w.user_id = %s", (g_current_user.user_id,))
    user_waiting_info = cursor.fetchone()
    if user_waiting_info:
        user_id, restaurant_id, priority, restaurant_name, address, avg_rating = user_waiting_info
        print(f"현재 대기 상황:\n"
              f"가게 이름: {restaurant_name}\n"
              f"가게 주소: {address}\n"
              f"현재 대기 순위: {priority}\n"
              f"예상 대기시간: {priority*5}분\n")
        while True:
            print("대기열 메뉴:\n"
                  "1. 뒤로 가기\n"
                  "2. 대기열에서 나가기\n")
            user_input = input("메뉴 선택: ")
            if user_input == "1":
                print("뒤로 갑니다.")
                break
            elif user_input == "2":
                leave_waiting_queue(restaurant_id, priority)
                break
            else:
                print("Invalid Option!. 다시 선택해주세요.")
    else:
        print("현재 대기 중인 가게가 없습니다.")


def write_review():
    # TODO - 사장이 대기열에서 pop하면 리뷰권한습득 -> 리뷰작성가능. 새로운 relation?
    pass

def user_menu():
    """
    고객이 사용할 수 있는 메뉴 출력
    1. 회원 정보 변경 (계정, 암호 변경)
    2. 가게 조회 (기준에 따른 순위별 조회)
    3. 내 대기열 조회 (현재 참여중인 대기열 정보)
    """
    while 1:
        print("----------------------------\n"
              "유저가 사용할 수 있는 메뉴입니다.\n"
              f"hello user - {g_current_user.user_name}\n"
              "1. 회원 정보 변경\n"
              "2. 가게 조회\n"
              "3. 내 대기열 조회\n"
              "4. 후기 등록\n"
              "5. 종료")
        user_input = input("메뉴 선택: ")
        if user_input == "1":
            change_user()
        elif user_input == "2":
            find_restaurant()
        elif user_input == "3":
            check_waiting()
        elif user_input == "4":
            write_review()
        elif user_input == "5":
            print("Bye")
            break
        else:
            print("Invalid Option!\n 1, 2, 3, 4 중 선택해주세요.")


def owner_menu():
    """
    사장이 사용할 수 있는 메뉴 출력
    """
    #TODO - 사장의 메뉴 -> 가게 등록, 삭제, 시작, 마감 / 가게에 대한 대기열 관리 / 리뷰 신고
    print("----------------------------\n"
          "사장이 사용할 수 있는 메뉴입니다.\n"
          f"hello owner {g_current_user.user_name}\n")


def admin_menu():
    """
    관리자가 사용할 수 있는 메뉴 출력
    :return:
    """
    #TODO - 관리자의 메뉴 -> 악성 리뷰 삭제 / 고객 및 사장 임시정지
    print("----------------------------\n"
          "관리자가 사용할 수 있는 메뉴입니다.\n"
          f"hello admin {g_current_user.user_name}\n")

if __name__ == "__main__":
    while 1:
        m = print_welcome_menu()
        if m == "1":
            sign_in()
            if g_current_user is not None: break
        elif m == "2":
            sign_up()
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