import web, spider_main
from twilio.twiml.voice_response import VoiceResponse

urls = (
    '/(twilio.*)', 'hello'
)
app = web.application(urls, globals())


class hello:
    def __init__(self):
        self.spiderMain = spider_main.SpiderMain()

    def GET(self, name):
        response = VoiceResponse()
        response.say("Twilio's always there when you call!")
        # response.play('https://api.twilio.com/cowbell.mp3')
        print(response)
        # param = web.input().get("name")
        # print(param)
        # if not name:
        #     name = 'World'
        # self.spiderMain.craw()
        return str(response)


if __name__ == "__main__":
    app.run()