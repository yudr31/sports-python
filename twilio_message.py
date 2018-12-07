from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "ACec6572226448e0765060822882fd6bd7"
# Your Auth Token from twilio.com/console
auth_token = "6cc9a9bd6079edfc8cff8e1c390dfb9e"

client = Client(account_sid, auth_token)

class twilio(object):

    def send_message(self,phone):
        message = client.messages.create(
            to="+86" + phone,
            from_="12393603007",
            body="温馨提醒：请尽快登录确认订单并支付!")
        print(message.sid)
        print('success\n')

    def voice_call(self,phone):
        call = client.calls.create(
            url='http://demo.twilio.com/docs/voice.xml',
            to="+86" + phone,
            from_="12393603007"
        )
        print(call.sid)
        print('success\n')

    def notify_user(self,booking_rule):
        notify_type = booking_rule['notify_type']
        phone = booking_rule['phone']
        if (notify_type == 1):
            self.send_message(phone)
        else:
            self.voice_call(phone)