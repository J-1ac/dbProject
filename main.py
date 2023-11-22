import psycopg2
import getpass

def printmenu():
    while 1:
        print("---------------------\n"
              "Welcome to 뭐먹지?\n"
              "Choose Menu\n"
              "1. login\n"
              "2. sign in\n")
        result = input("메뉴 선택: ")
        if result == "1" or result == "2":
            return result
        else:
            print("please input 1 or 2")

def signin(cursor):
    input_username = input("아이디: ")
    input_password = input('비밀번호: ')

    # 사용자 아이디와 비밀번호로 조회
    cursor.execute("select * from users where user_name = %s and user_pw = %s", (input_username, input_password))
    result = cursor.fetchall()

    if result:
        print("로그인 성공!")
        # 여기에 로그인 성공 후의 동작을 추가하세요
    else:
        print("로그인 실패. 아이디 또는 비밀번호를 확인하세요.")

if __name__ == "__main__":
    con = psycopg2.connect(
        database='mmg',
        user='sjlee',
        password='sjlee!2023',
        host='::1',
        port='5432'
    )

    cursor = con.cursor()

    m = printmenu();

    if m == "1":
        print("sign in chosen")
        signin(cursor)
    elif m == "2":
        print("sign up chosen")
        # signup()


    # cursor.execute("insert into customers (customer_id, customer_name, phone, birth_date, balance) "
    #                "values ('1234', 'Cho', '12345678', '2023-01-01', 78.56)")
    # con.commit()

    # cursor.execute("select * from users")
    # result = cursor.fetchall()
    # for r in result:
    #     print(r)
    #
    # cursor.execute("select * from restaurant")
    # result = cursor.fetchall()
    # for r in result:
    #     print(r)