import url_manager, html_parser, html_downloader, mysql, twilio_message, schedule, time, datetime


class  SpiderMain(object):
	"""docstring for  SpiderMain"""
	def __init__(self):
		self.urls = url_manager.UrlManager()
		self.downloader = html_downloader.HtmlDownloader()
		self.parser = html_parser.HtmlParser()
		self.dbData = mysql.MysqlCursor()
		self.sender = twilio_message.twilio()

		
	def craw(self, week_days, opener, headers):
		root_urls = []
		result_data = []
		root_urls.append("http://m.quyundong.com/court/detail?id=17056")
		self.urls.add_new_urls(root_urls)
		# order_user = self.dbData.select_order_user(user_id)
		# data = {'username': order_user['user_name'], 'password': order_user['password']}
		# opener, headers = self.downloader.download_login(data)

		while self.urls.has_new_url():
			try:
				new_url = self.urls.get_new_url()
				html_cont = self.downloader.get_orders(opener, headers, new_url)
				new_urls = self.parser.parse_court(result_data, new_url, html_cont, week_days)
				self.urls.add_new_urls(new_urls)
			except Exception as e:
				print('craw failed')
				print(e)
		# if (result_data is not None and result_data != []):
		# 	self.dbData.insert_court_data(result_data)
		return result_data

	def book_order(self, court_id, user_id):
		# 登录时需要POST的数据
		order_user = self.dbData.select_order_user(user_id)
		data = {'username': order_user['user_name'],'password': order_user['password']}
		opener, headers = self.downloader.download_login(data)
		order_count = self.downloader.get_order_list(opener, headers)

		if (order_count == 0):
			book_order = self.downloader.book_order(opener, headers, court_id)
			confirm_data = self.parser.parse_book_order_and_get_confirm_data(book_order)
			if (confirm_data is not None):
				order_id = self.downloader.confirm_order(opener, headers,confirm_data)
				if (order_id is not None):
					unpay_order = self.downloader.get_order_detail(opener, headers, order_id)
					order_data = self.parser.parse_order_detail(unpay_order, order_id)
					self.dbData.insert_order_data(order_data)
		self.downloader.logout(opener, headers)

	def craw_and_book(self, booking_rule):
		week_days = booking_rule['booking_date'].split(",")
		self.craw(week_days)
		for week_day in week_days:
			court = self.dbData.select_available_court(week_day,booking_rule)
			if (court is not None):
				print(week_day + '有可预订球场，正在通知和下单！')
				if (booking_rule['notify_count'] > booking_rule['max_notify']):
					print('通知已达最大次数，不进行通知和下单！\n')
					return 0
				if (booking_rule['notify_time']):
					second = (datetime.datetime.now() - booking_rule['notify_time']).seconds
					if (second < booking_rule['time_interval'] * 60):
						print('不在通知时间范围，不进行通知和下单！\n')
						return 0
				self.sender.notify_user(booking_rule)
				if (booking_rule['order_now'] == 1):
					self.book_order(court['gid'],booking_rule['order_user'])
				return 1
			else:
				print(week_day + '无可预订球场!\n')
		return 0

	def update_order(self, order_id, user_id):
		# 登录时需要POST的数据
		order_user = self.dbData.select_order_user(user_id)
		data = {'username': order_user['user_name'], 'password': order_user['password']}
		opener, headers = self.downloader.download_login(data)
		unpay_order = self.downloader.get_order_detail(opener, headers, order_id)
		order_data = self.parser.parse_order_detail(unpay_order, order_id)
		self.dbData.update_unpay_order(order_data)
		self.downloader.logout(opener, headers)

	def send_message(self):
		# self.sender.send_message()
		self.sender.voice_call()
		# self.sender.test()

	def select_rule_info(self):
		booking_rules = self.dbData.select_booking_rules()
		print(booking_rules)
		if (booking_rules is None or booking_rules == ()):
			print("无开启的预订规则\n")
			return
		for booking_rule in  booking_rules:
			order = self.select_unuse_order(booking_rule)
			if (order is not None):
				grab_count = self.update_order_info(order)
			else:
				print('继续预订球场')
				grab_count = booking_rule['grab_count']
				notify_count = self.craw_and_book(booking_rule)
			if notify_count == 1:
				notify_time = datetime.datetime.now()
			else:
				notify_time = booking_rule['notify_time']
			notify_count += booking_rule['notify_count']
			self.dbData.update_grab_info(booking_rule['gid'], grab_count, notify_count, notify_time)

	def update_order_info(self, order):
		if ('未支付' == order['pay_status']):
			print('更新未支付订单\n')
			self.update_order(order['gid'])
		elif ('已取消' == order['pay_status']):
			print('订单已取消，继续预订球场')
			self.craw_and_book()
		elif ('待使用' == order['pay_status']):
			print('已预订到球场，停止预订球场\n')
		elif ('待开始' == order['pay_status']):
			print('已预订到球场，停止预订球场\n')
		return 0

	def job(self):
		print("正在查询订单，预订球场！")
		obj_spider.select_rule_info()

	def select_unuse_order(self,booking_rule):
		order_user = booking_rule['order_user'];
		order = self.dbData.select_unuse_order(order_user)
		return order


if __name__ == "__main__":

	obj_spider = SpiderMain()
	# obj_spider.craw('')
	# obj_spider.book_order(gid)
	# obj_spider.send_message()
	# obj_spider.select_unuse_order()
	# gid = "8b6c3b7250ca48469b20b0eed5c0e962"
	# obj_spider.select_rule_info()

	schedule.every(10).seconds.do(obj_spider.job)

	while True:
		schedule.run_pending()
		time.sleep(1)
