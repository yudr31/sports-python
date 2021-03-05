import urllib
import http.cookiejar
import json, mysql

class HtmlDownloader(object):

	def __init__(self):
		self.outputer = mysql.MysqlCursor()

	"""docstring for HtmlDownloader"""
	def download(self, url):
		if url is None:
			return None
		response = urllib.request.urlopen(url)
		if response.getcode() != 200:
			return None
		return response.read()
	def download_login(self, data):
		post_data = urllib.parse.urlencode(data).encode('utf-8')
		# 设置请求头
		headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'}
		# 登录时表单提交到的地址（用开发者工具可以看到）
		login_url = 'https://m.quyundong.com/login/dologin'
		# 构造登录请求
		req = urllib.request.Request(login_url, headers=headers, data=post_data)
		# 构造cookie
		cookie = http.cookiejar.CookieJar()
		# 由cookie构造opener
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
		# 发送登录请求，此后这个opener就携带了cookie，以证明自己登录过
		resp = opener.open(req)
		return opener,headers

	def get_orders(self, opener, headers, url):
		# 登录后才能访问的网页
		# url = 'https://m.quyundong.com/myorder/index?type=0'
		# 构造访问请求
		req = urllib.request.Request(url, headers=headers)
		resp = opener.open(req)
		return resp.read()

	def book_order(self, opener, headers, gid):
		book_court1,book_court2 = self.outputer.select_by_gid(gid)
		if (book_court1['court'] != book_court2['court']):
			return Exception('球场信息不一致')
		if ('VIP' in book_court1['court'] or 'VIP' in book_court2['court'] ):
			return Exception('VIP场不进行预订')
		# 提交订单
		book_data = {'court_name':'兴东羽毛球馆',
					 'category_name':'羽毛球',
					 'bid':'17056',
					 'cid':'1',
					 'order_type':'0',
					 'relay':'0',
					 'allcourse_name':'1号场,2号场,3号场,4号场,5号场,6号场,7号场,8号场,9号场,10号场,11号场,12号场,13号场,VIP1,VIP2,VIP3'}
		book_data['price[]'] = book_court1['price']
		book_data['hour[]'] = book_court1['hour']
		book_data['course_name[]'] =  book_court1['court']
		book_data['real_time[]'] =  book_court1['time_interval']
		book_data['price[]'] = book_court2['price']
		book_data['hour[]'] = book_court2['hour']
		book_data['course_name[]'] = book_court2['court']
		book_data['real_time[]'] = book_court2['time_interval']
		book_data['book_date'] = self.get_book_date(book_court1['book_param'])
		book_data['goods_ids'] = book_court1['gid'] + ',' + book_court2['gid']
		book_url = 'http://m.quyundong.com/order/Confirm?'
		book_data = urllib.parse.urlencode(book_data).encode('utf-8')
		# 构造访问请求
		req = urllib.request.Request(book_url, headers=headers, data=book_data)
		resp = opener.open(req)
		# print(resp.read().decode('utf-8'))
		return resp.read()

	def get_book_date(self, book_param):
		params = book_param.split('&')
		return params[1].split('=')[1]

	def confirm_order(self, opener, headers, confirm_data):
		# 确认订单
		# confirm_data = {
		# 			 'goods_ids': '224445998,224445999',
		# 			 'act_id': '0',
		# 			 'code':'0',
		# 			 'bid': '17056',
		# 			 'cid': '1',
		# 			 'coupon_id':'0',
		# 			 'ticket_type':'1',
		# 			 'utm_source': '',
		# 			 'pay_type': 'online',
		# 			 'card_no': '',
		# 			 'relay': '0',
		# 			 'package_type': 0,
		# 			 'hash': '37184392de83b14b842cd86a9acb5695'}
		confirm_url = 'http://m.quyundong.com/order/doconfirm?'
		confirm_data = urllib.parse.urlencode(confirm_data).encode('utf-8')
		# 构造访问请求
		req = urllib.request.Request(confirm_url, headers=headers, data=confirm_data)
		resp = opener.open(req)
		result = json.loads(resp.read().decode('utf-8'))
		print(result)
		if ('1' == result['code']):
			return result['data']
		return None

	def get_order_detail(self, opener, headers, order_id):
		order_detail_url = 'http://m.quyundong.com/myorder/detail?id=' + order_id
		req = urllib.request.Request(order_detail_url, headers=headers)
		resp = opener.open(req)
		return resp.read()

	def get_order_list(self, opener, headers):
		order_list_url = 'https://m.quyundong.com/myorder/orderList?action=order_get_order_list&page=1&type=0'
		req = urllib.request.Request(order_list_url, headers=headers)
		resp = opener.open(req)
		order_list = json.loads(resp.read().decode('utf-8'))['data']
		for order in order_list:
			order_status = order['order_status']
			if ('0' == order_status):
				return 1
		return 0

	def logout(self, opener, headers):
		logout_url = 'https://m.quyundong.com/user/logOut'
		req = urllib.request.Request(logout_url, headers=headers)
		resp = opener.open(req)

	def get_access_token(self,):
		url = 'https://oapi.dingtalk.com/gettoken?corpid=%s&corpsecret=%s' % (corp_id, corp_secret)
		request = urllib.Request(url)
		response = urllib.urlopen(request)
		response_str = response.read()
		response_dict = json.loads(response_str)
		error_code_key = "errcode"
		access_token_key = "access_token"
		if response_dict.has_key(error_code_key) and response_dict[error_code_key] == 0 and response_dict.has_key(
				access_token_key):
			return response_dict[access_token_key]
		else:
			return ''
