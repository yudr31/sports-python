import itchat



class sender(object):

    def send_message(self):
        itchat.auto_login(hotReload=True)
        friends = itchat.search_friends(name='痞子绅士')
        # 获取`UserName`,用于发送消息
        userName = friends[0]['UserName']
        print(userName)
        # itchat.send("已为您下单，请尽快登录进行支付！",toUserName = userName)
        print('succeed')
        # itchat.logout()