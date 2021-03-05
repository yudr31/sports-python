import web, spider_main, html_downloader, mysql

urls = (
    '/craw_court', 'craw_court'
)
app = web.application(urls, globals())
web.opener = None
web.headers = None

class craw_court:
    def __init__(self):
        self.spiderMain = spider_main.SpiderMain()
        self.dbData = mysql.MysqlCursor()
        self.downloader = html_downloader.HtmlDownloader()

    def GET(self):
        week_days = web.input().get("week_days")
        user_id = web.input().get("user_id")
        if web.opener is None:
            print("do login")
            order_user = self.dbData.select_order_user(user_id)
            data = {'username': order_user['user_name'], 'password': order_user['password']}
            opener, headers = self.downloader.download_login(data)
            web.opener = opener
            web.headers = headers
        return self.spiderMain.craw(week_days, web.opener, web.headers)


if __name__ == "__main__":
    app.run()