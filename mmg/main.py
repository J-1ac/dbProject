import psycopg2
import re

# TODO -> 로그아웃 기능 추가?
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
          "1. sign in\n"
          "2. sign up\n"
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
    # TODO - 비밀번호 해쉬화
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
            print("회원 정보 변경을 종료합니다.")
            break
        else:
            print("Invalid Option!\n 1, 2, 3 중 선택해주세요.")


def find_restaurant():
    global con
    cursor = con.cursor()
    # TODO - 조회 순서 추가(평점순, 대기시간순...)
    print("가게 조회 메뉴입니다.\n")
    cursor.execute("select * from restaurants where open_status = true order by restaurant_id")
    restaurants = cursor.fetchall()

    print("가게 목록:")
    if not restaurants:
        print("텅")
        return

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

    if not selected_restaurant:
        return print("존재하지 않는 가게입니다.")

    if selected_restaurant[5] == False:
        return print("닫혀있는 가게입니다.")

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
                print("Invalid Option!\n 다시 선택해주세요.")
    else:
        print("현재 대기 중인 가게가 없습니다.")


def write_review():
    global con
    cursor = con.cursor()
    # 현재 고객의 작성 가능한 리뷰 목록 가져오기
    cursor.execute("select re.review_id, r.restaurant_name, r.restaurant_address, r.avg_rating, r.restaurant_id "
                   "from reviews re "
                   "join restaurants r on re.restaurant_id = r.restaurant_id "
                   "where user_id = %s and review_rating is null and review_comment is null",
                   (g_current_user.user_id,))
    reviewable_list = cursor.fetchall()

    if not reviewable_list:
        return print("작성 가능한 리뷰가 없습니다.")

    print("작성 가능한 리뷰 목록:")
    for review in reviewable_list:
        print(f"리뷰 ID: {review[0]}, 가게 이름: {review[1]}, 가게 주소: {review[2]}, 평균 평점:{review[3]}")

    # 리뷰 작성할 가게 선택
    selected_review_id = input("리뷰를 작성할 가게의 리뷰 ID를 입력하세요 (종료: 0): ")

    if selected_review_id == "0":
        return print("리뷰 작성을 종료합니다.")

    # 선택한 리뷰의 유효성 검사 및 작성
    selected_review = None
    for review in reviewable_list:
        if str(review[0]) == selected_review_id:
            selected_review = review
            break

    if selected_review:
        rating = input("별점을 입력하세요 (0~5): ")
        comment = input("코멘트를 입력하세요 (15자 이상): ")

        if not (rating.isdigit() and 0 <= int(rating) <= 5):
            return print("별점은 0에서 5 사이의 숫자여야 합니다.")
        if len(comment) < 15:
            return print("코멘트는 15자 이상이어야 합니다.")

        # 리뷰 작성
        cursor.execute("update reviews set review_rating = %s, review_comment = %s where review_id = %s",
                       (rating, comment, selected_review_id))
        # 해당 가게의 평균 평점 갱신
        # TODO 고려할 부분) 가게의 평균 평점 개신 시점 -> 리뷰 작성시? 가게 조회시?
        cursor.execute("update restaurants "
                       "set avg_rating = "
                            "round("
                            "(select avg(review_rating) "
                            "from reviews "
                            "where restaurant_id = %s and review_rating is not null), 2)"
                       "where restaurant_id = %s", (selected_review[4], selected_review[4]))
        con.commit()
        print("리뷰가 성공적으로 작성되었습니다.")
    else:
        print("유효하지 않거나 권한이 없는 리뷰입니다.")


def view_myrestaurant():
    global con
    cursor = con.cursor()
    print("----내 가게 목록----")
    # 현재 사용자의 가게 목록 조회
    cursor.execute("select * from restaurants where owner_id = %s", (g_current_user.user_id,))
    my_restaurants = cursor.fetchall()

    if not my_restaurants:
        print("내 가게가 없습니다.")
        return False
    else:
        for restaurant in my_restaurants:
            status = "Open" if restaurant[5] else "Closed"
            print(f"가게 ID: {restaurant[0]}, 가게 이름: {restaurant[2]}, 주소: {restaurant[3]}, 평점: {restaurant[4]}, 상태: {status}")
    return True

def register_restaurant():
    global con
    cursor = con.cursor()
    print("가게 등록 기능이 선택되었습니다.")
    # 가게 정보 입력
    restaurant_name = input("가게 이름: ")
    restaurant_address = input("가게 주소: ")

    # 가게 등록 쿼리 실행
    cursor.execute("insert into restaurants (owner_id, restaurant_name, restaurant_address, open_status) values (%s, %s, %s, %s) returning restaurant_id", (g_current_user.user_id, restaurant_name, restaurant_address, False))
    con.commit()
    new_restaurant_id = cursor.fetchone()[0]

    print(f"가게 등록이 완료되었습니다. (가게 ID: {new_restaurant_id})")


def delete_restaurant():
    global con
    cursor = con.cursor()
    print("가게 삭제 기능이 선택되었습니다.")
    if not view_myrestaurant():
        return print("가게 삭제 기능을 종료합니다.")
    # 가게 ID 입력
    restaurant_id = int(input("삭제할 가게의 ID: "))

    # 가게 삭제 쿼리 실행
    cursor.execute("delete from restaurants where restaurant_id = %s and owner_id = %s", (restaurant_id, g_current_user.user_id))
    con.commit()

    if cursor.rowcount > 0:
        print("가게 삭제가 완료되었습니다.")
        return True
    else:
        print("해당 가게를 찾을 수 없거나 삭제 권한이 없습니다.")


def register_or_delete_restaurant():
    while True:
        print("가게 등록 및 삭제 메뉴입니다.\n"
              "1. 가게 등록\n"
              "2. 가게 삭제\n"
              "3. 종료\n")

        user_input = input("메뉴 선택: ")
        if user_input == "1":
            register_restaurant()
            break
        elif user_input == "2":
            if delete_restaurant(): break
        elif user_input == "3":
            print("가게 등록 및 삭제를 종료합니다.")
            break
        else:
            print("Invalid Option!\n 1, 2, 3 중 선택해주세요.")


def change_status_myrestaurant():
    global con
    cursor = con.cursor()
    while True:
        print("내 가게 상태 변경 메뉴입니다.\n"
              "1. 가게 상태 변경\n"
              "2. 종료\n")
        user_input = input("메뉴 선택: ")
        if user_input == "1":
            if not view_myrestaurant():
                return print("내 가게 상태 변경 기능을 종료합니다.")
            # 가게 ID 입력
            restaurant_id = input("변경할 가게의 ID: ")
            # 가게 상태 변경 쿼리 실행
            cursor.execute("update restaurants set open_status = not open_status where restaurant_id = %s and owner_id = %s", (restaurant_id, g_current_user.user_id))
            con.commit()

            if cursor.rowcount > 0:
                return print("가게 상태 변경이 완료되었습니다.")
            else:
                print("해당 가게를 찾을 수 없거나 변경 권한이 없습니다.")
        elif user_input == "2":
            return print("내 가게 상태 변경 기능을 종료합니다.")
        else:
            print("Invalid Option!\n 1, 2 중 선택해주세요.")


def manage_waiting():
    global con
    cursor = con.cursor()
    print("내 가게 대기열 관리 메뉴입니다.")
    if not view_myrestaurant(): return      # 자신의 가게가 없는 경우 return
    choosen_restaurant_id = input("선택할 가게의 ID: ")

    cursor.execute("select owner_id from restaurants where restaurant_id = %s", (choosen_restaurant_id,))
    owner_id = cursor.fetchone()

    # 선택된 가게가 없거나, 현재 사장의 가게가 아닌 경우 return
    if not owner_id or owner_id[0] != g_current_user.user_id:
        return print("해당 가게의 권한이 없습니다.")

    while 1:
        print("현재 대기열 목록: \n")
        cursor.execute("select * from waitings where restaurant_id = %s order by priority", (choosen_restaurant_id, ))
        waiting_list = cursor.fetchall()
        # 대기열이 비어있을 경우 종료
        if not waiting_list:
            return print("대기열이 비어있습니다.")

        for waiting in waiting_list:
            print(f"손님 ID: {waiting[1]}, 우선순위: {waiting[2]}")
        print("1: 손님 입장\n"
              "2: 종료\n")
        user_input = input("메뉴 선택: ")
        if user_input == "1":
            # 입장한 손님을 reviews에 추가하는 쿼리
            cursor.execute("insert into reviews (user_id, restaurant_id) values (%s, %s)", (waiting_list[0][1], choosen_restaurant_id))
            # 입장한 손님 삭제 쿼리
            cursor.execute("delete from waitings where restaurant_id = %s and priority = 1", (choosen_restaurant_id,))
            # 나머지 대기열 내 고객의 priority를 1씩 감소.
            cursor.execute("update waitings set priority = priority - 1 where restaurant_id = %s", (choosen_restaurant_id,))
            con.commit()
            print("손님 입장 처리를 완료하였습니다.")
        elif user_input == "2":
            return print("내 가게 대기열 관리 기능을 종료합니다.")
        else:
            print("Invalid Option!\n 1, 2 중 선택해주세요.")


def report_review(review_id):
    global con
    cursor = con.cursor()

    # 신고 횟수를 조회
    cursor.execute("select count(*) from reports where review_id = %s", (review_id,))
    current_reports = cursor.fetchone()[0]

    if current_reports:
        return print("이미 신고된 리뷰입니다.")
    else:
        comment = input("상황을 설명해주세요 (15자 이상): ")
        if len(comment) < 15:
            return print("설명은 15자 이상이어야 합니다.")
        # 리뷰 신고 쿼리
        cursor.execute("insert into reports (review_id, description) values (%s, %s)", (review_id, comment))
        con.commit()

def view_review():
    global con
    cursor = con.cursor()
    print("내 가게 리뷰 관리 메뉴입니다.")
    if not view_myrestaurant(): return  # 자신의 가게가 없는 경우 return
    choosen_restaurant_id = input("선택할 가게의 ID: ")

    cursor.execute("select owner_id from restaurants where restaurant_id = %s", (choosen_restaurant_id,))
    owner_id = cursor.fetchone()

    # 선택된 가게가 없거나, 현재 사장의 가게가 아닌 경우 return
    if not owner_id or owner_id[0] != g_current_user.user_id:
        return print("해당 가게의 권한이 없습니다.")

    print("리뷰 목록: \n")
    cursor.execute("select * from reviews where restaurant_id = %s and review_rating is not null and review_comment is not null order by review_id desc", (choosen_restaurant_id,))
    reviews = cursor.fetchall()
    # 작성된 리뷰가 없을 경우 종료
    if not reviews:
        return print("리뷰가 없습니다.")

    for review in reviews:
        print(f"리뷰 ID: {review[0]}, 평점: {review[3]}, 내용: {review[4]}")

    # 리뷰 신고 기능
    review_id_to_report = input("신고할 리뷰의 ID를 입력하세요 (종료: 0): ")

    if review_id_to_report == "0":
        return print("리뷰 신고를 종료합니다.")

    cursor.execute("select r.owner_id, re.restaurant_id "
                   "from restaurants r "
                   "join reviews re "
                   "on r.restaurant_id = re.restaurant_id "
                   "where re.review_id = %s", (review_id_to_report,))
    choosen_review_to_report = cursor.fetchone()

    # 선택된 신고 리뷰 유효성 검사
    if choosen_review_to_report is None:
        return print("존재하지 않는 리뷰입니다.")
    elif choosen_review_to_report[0] != g_current_user.user_id:
        return print("신고할 권한이 없는 리뷰입니다.")
    elif choosen_review_to_report[1] != int(choosen_restaurant_id):
        return print("현재 가게의 리뷰가 아닙니다.")

    report_review(review_id_to_report)

def user_menu():
    """
    고객이 사용할 수 있는 메뉴 출력
    1. 회원 정보 변경 (계정, 암호 변경)
    2. 가게 조회 (기준에 따른 순위별 조회)
    3. 내 대기열 조회 (현재 참여중인 대기열 정보)
    4. 리뷰 등록
    """
    while 1:
        print("----------------------------\n"
              "고객이 사용할 수 있는 메뉴입니다.\n"
              f"hello user - {g_current_user.user_name}\n"
              "1. 회원 정보 변경\n"
              "2. 가게 조회 (대기열 등록)\n"
              "3. 내 대기열 조회\n"
              "4. 리뷰 등록\n"
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
    1. 내 가게 조회
    2. 내 가게 상태 변경 (오픈 및 마감)
    3. 대기열 관리 (손님 입장)
    4. 리뷰 조회 (악성 리뷰 신고)
    5. 가게 등록 및 삭제
    """
    while True:
        print("----------------------------\n"
              "사장이 사용할 수 있는 메뉴입니다.\n"
              f"hello owner - {g_current_user.user_name}\n"
              "1. 내 가게 조회\n"
              "2. 내 가게 상태 변경\n"
              "3. 대기열 관리\n"
              "4. 리뷰 조회\n"
              "5. 가게 등록 및 삭제\n"
              "6. 종료\n")

        user_input = input("메뉴 선택: ")
        if user_input == "1":
            view_myrestaurant()
        elif user_input == "2":
            change_status_myrestaurant()
        elif user_input == "3":
            manage_waiting()
        elif user_input == "4":
            view_review()
        elif user_input == "5":
            register_or_delete_restaurant()
        elif user_input == "6":
            print("Bye")
            break
        else:
            print("Invalid Option!\n 1 ~ 6 중 선택해주세요.")


def examine_review():
    global con
    cursor = con.cursor()
    print("검토할 리뷰 목록: \n")
    cursor.execute("select r.report_id, r.review_id, r.description, re.user_id, re.review_rating, re.review_comment "
                   "from reports r "
                   "join reviews re on r.review_id = re.review_id "
                   "order by r.report_id desc")
    reviews = cursor.fetchall()

    if not reviews:
        return print("검토할 리뷰가 없습니다.")

    for review in reviews:
        print(f"신고 ID: {review[0]}, 리뷰 ID: {review[1]}, 신고 내용: {review[2]}\n"
              f"리뷰 작성자: {review[3]}, 리뷰 평점: {review[4]}, 리뷰 내용: {review[5]}\n"
              f"----------------------------------------------------------------------")

    # 리뷰 신고 기능
    review_id_to_report = input("검토할 리뷰의 신고 ID를 입력하세요 (종료: 0): ")

    if review_id_to_report == "0":
        return print("리뷰 검토가 종료됩니다.")

    cursor.execute("select r.report_id, r.review_id, r.description, re.user_id, re.review_rating, re.review_comment "
                   "from reports r "
                   "join reviews re on r.review_id = re.review_id "
                   "where r.report_id = %s", (review_id_to_report,))
    reported_review = cursor.fetchone()

    if not reported_review:
        return print("존재하지 않는 리뷰 신고입니다.")

    print(f"신고 ID: {reported_review[0]}, 리뷰 ID: {reported_review[1]}, 신고 내용: {reported_review[2]}\n"
          f"리뷰 작성자: {reported_review[3]}, 리뷰 평점: {reported_review[4]}, 리뷰 내용: {reported_review[5]}")

    decision = input("신고를 승인하시겠습니까? (승인: 1, 거부: 0): ")

    if decision == "1":
        # 승인된 신고에 대한 처리 로직
        cursor.execute("delete from reviews where review_id = %s", (reported_review[1],))
        cursor.execute("delete from reports where review_id = %s", (reported_review[1],))
        con.commit()
        print("신고가 승인되었습니다. 해당 리뷰가 삭제되었습니다.")
    elif decision == "0":
        cursor.execute("delete from reports where review_id = %s", (reported_review[1],))
        con.commit()
        print("신고를 거부하였습니다.")
    else:
        print("잘못된 선택입니다. 1 또는 0을 입력해주세요.")

def supervise_user():
    pass


def supervise_owner():
    pass


def admin_menu():
    """
    관리자가 사용할 수 있는 메뉴 출력
    """
    #TODO - 관리자의 메뉴 구현하기 -> 고객 및 사장 임시정지
    while True:
        print("----------------------------\n"
              "관리자가 사용할 수 있는 메뉴입니다.\n"
              f"hello admin - {g_current_user.user_name}\n"
              "1. 리뷰 검토\n"
              "2. 고객 관리\n"
              "3. 사장 관리\n"
              "4. 종료\n")

        user_input = input("메뉴 선택: ")
        if user_input == "1":
            examine_review()
        elif user_input == "2":
            supervise_user()
        elif user_input == "3":
            supervise_owner()
        elif user_input == "4":
            print("Bye")
            break
        else:
            print("Invalid Option!\n 1, 2, 3, 4 중 선택해주세요.")

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