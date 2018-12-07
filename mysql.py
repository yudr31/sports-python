import pymysql.cursors, time, datetime

# 连接数据库
connect = pymysql.Connect(
    host = '10.10.11.208',
    port = 3306,
    user = 'root',
    passwd = 'testsmysql',
    db = 'sports',
    charset = 'utf8',
    cursorclass=pymysql.cursors.DictCursor
)

class MysqlCursor(object):

    def insert_court_data(self,datas):
        # 获取游标
        connect.autocommit(True)
        cursor = connect.cursor()
        cursor.execute("delete from court_info")
        for data in datas:
            sql = "insert into court_info (gid, book_date, week_day, price, start_time, court, time_interval, booking, book_param, group_ids, content) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            param = (data['gid'], data['book_date'], data['week_day'], data['price'], data['start_time'], data['court'], data['time_interval'], data['booking'], data['book_param'], data['group_ids'], data['content'])
            cursor.execute(sql,param)
        print('更新球场信息成功，更新数据条数：',len(datas))

    def insert_order_data(self, order_data):
        connect.autocommit(True)
        cursor = connect.cursor()
        sql = "insert into order_info (gid, arena, item, order_no, book_date, order_date, space_time, smount, verif_code, pay_status, address) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        param = (order_data['gid'], order_data['arena'], order_data['item'], order_data['order_no'], order_data['book_date'], order_data['order_date'],
                 order_data['space_time'], order_data['smount'], order_data['verif_code'], order_data['pay_status'], order_data['address'])
        cursor.execute(sql, param)

    def update_unpay_order(self, order_data):
        connect.autocommit(True)
        cursor = connect.cursor()
        sql = "update order_info set pay_status = %s where gid = %s"
        param = (order_data['pay_status'],order_data['gid'])
        cursor.execute(sql, param)

    def select_order_user(self, user_id):
        cursor = connect.cursor()
        cursor.execute("select * from outer_user where gid = %s",user_id)
        result = cursor.fetchone()
        print(result)
        return result

    def select_by_gid(self, gid):
        cursor = connect.cursor()
        cursor.execute("select * from court_info where gid = " + gid)
        book_court1 = cursor.fetchone()
        cursor.execute('select * from court_info where gid = ' + str(int(gid) + 1))
        book_court2 = cursor.fetchone()
        return book_court1,book_court2

    def select_booking_rules(self):
        cursor = connect.cursor()
        cursor.execute("select * from booking_info where booking_state = 1")
        booking_rules = cursor.fetchall()
        return booking_rules

    def update_grab_info(self, gid, grab_count, notify_count, notify_time):
        connect.autocommit(True)
        cursor = connect.cursor()
        sql = "update booking_info set grab_count = %s, notify_count = %s, notify_time = %s where gid = %s"
        param = (grab_count + 1, notify_count, notify_time, gid)
        cursor.execute(sql, param)

    def select_unuse_order(self,order_user):
        today = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        sql = "select * from order_info where order_date > %s and order_user = %s"
        param = (str(today),order_user)
        cursor = connect.cursor()
        cursor.execute(sql,param)
        return cursor.fetchone()

    def select_available_court(self, week_day, booking_rule):
        cursor = connect.cursor()
        hour = int(booking_rule['booking_time'].split(":")[0])
        booking_court = None
        for i in range(0,booking_rule['duration']):
            hour = hour + i
            sql = "select * from court_info where week_day = %s and booking = %s and start_time = %s and court like %s"
            param = (week_day,'available',hour, '%'+ booking_rule['court_type'])
            cursor.execute(sql, param)
            court = cursor.fetchone()
            if court is None:
                return None;
            if (i == 0):
                booking_court = court
            print(booking_court)
        return booking_court