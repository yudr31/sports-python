from bs4 import BeautifulSoup
from urllib import parse as urlparse

class HtmlParser(object):

    def _get_news_url(self, page_url, soup, week_days):
        new_urls = set()
        div_node = soup.find('div', class_='book borderBottom1px')
        if div_node is None:
            return new_urls
        li_nodes = div_node.find_all('li', class_='borderBottom1px')
        for li_node in li_nodes:
            a_node = li_node.find('a', class_='booking')
            new_url = a_node['href']
            weekday_node = li_node.find('div', class_='weekday')
            weekday_text = weekday_node.get_text().strip().replace("（","").replace("）","")
            if (week_days is None):
                new_full_url = urlparse.urljoin(page_url, new_url)
                new_urls.add(new_full_url)
            else :
                if (weekday_text in week_days ):
                    new_full_url = urlparse.urljoin(page_url, new_url)
                    new_urls.add(new_full_url)
        return new_urls

    def _get_date_data(self, result_data, page_url, soup):
        div_node = soup.find('div', class_='book-list')
        if (div_node is None):
            return []
        date_wrap = soup.find('div', class_='date-wrap')
        urls = page_url.split('?')
        book_date, week_day = self._get_date_day(urls[1],date_wrap)
        ul_nodes = div_node.find_all('ul')
        for ul_node in ul_nodes:
            li_nodes = ul_node.find_all('li')
            for li_node in li_nodes:
                data = {}
                data['book_param'] = urls[1]
                data['gid'] = li_node.get('goodsid')
                data['book_date'] = book_date
                data['week_day'] = week_day
                data['price'] = li_node.get('price')
                course_content = li_node.get('course_content')
                contents = course_content.split(',')
                data['court'] = contents[0]
                data['start_time'] = contents[1]
                data['time_interval'] = contents[0]
                data['booking'] = li_node.get('class')[0]
                data['group_ids'] = li_node.get('group_ids')
                data['content'] = course_content
                result_data.append(data)
        return result_data

    def _get_date_day(self, book_param,date_wrap):
        a_nodes = date_wrap.find_all('a')
        for a_node in a_nodes:
            if (book_param in a_node.get('href')):
                p_nodes = a_node.find_all('p')
                week_day = p_nodes[0].get_text().strip()
                book_date = p_nodes[len(p_nodes) - 1].get_text().strip()
                return book_date,week_day
        return '',''

    def _get_confirm_data(self, soup):
        confirm_data = {'code': '0',
                        'utm_source': '',
                        'pay_type': 'online',
                        'relay': '0',
                        'package_type': 0}
        input_nodes = soup.find_all('input')
        if (len(input_nodes) == 0):
            return None

        for input_node in input_nodes:
            if ('goods_ids' == input_node.get('name')):
                confirm_data['goods_ids'] = input_node.get('value')
            if ('act_id' == input_node.get('name')):
                confirm_data['act_id'] = input_node.get('value')
            if ('bid' == input_node.get('name')):
                confirm_data['bid'] = input_node.get('value')
            if ('cid' == input_node.get('name')):
                confirm_data['cid'] = input_node.get('value')
            if ('coupon_id' == input_node.get('name')):
                confirm_data['coupon_id'] = input_node.get('value')
            if ('ticket_type' == input_node.get('name')):
                confirm_data['ticket_type'] = input_node.get('value')
            if (input_node.get('name') is None and 'user_has_card' == input_node['id']):
                confirm_data['card_no'] = input_node.get('value')
            if ('relay' == input_node.get('name')):
                confirm_data['relay'] = input_node.get('value')
            if ('package_type' == input_node.get('name')):
                confirm_data['package_type'] = input_node.get('value')
            if (input_node.get('name') is None and 'J_payHash' == input_node['id']):
                confirm_data['hash'] = input_node.get('value')
        return confirm_data

    def _get_order_data(self, soup, order_id):
        order_data = {}
        order_data['gid'] = order_id
        order_bd = soup.find('div', class_='order-bd')
        order_items = order_bd.find_all('div', class_='order-item')
        if (len(order_items) < 2):
            raise Exception('order-item 订单解析失败')

        p_nodes = order_items[0].find_all('p')
        order_data['arena'] = p_nodes[0].get_text()
        order_data['address'] = p_nodes[1].get_text()
        ul_nodes = order_items[1].find_all('ul', class_='info-list')
        if (len(ul_nodes) < 3):
            raise Exception('info-list 订单解析失败')

        ul0_p_nodes = ul_nodes[0].find_all('p')
        order_data['item'] = ul0_p_nodes[1].get_text()
        order_data['order_date'] = ul0_p_nodes[3].get_text()
        order_data['space_time'] = ul0_p_nodes[5].get_text().strip().replace('\xa0',' ').replace('元','元 ')
        order_data['smount'] = ul0_p_nodes[9].get_text()

        ul1_p_nodes = ul_nodes[2].find_all('p')
        order_data['verif_code'] = ul1_p_nodes[1].get_text()
        order_data['order_no'] = ul1_p_nodes[3].get_text()
        order_data['pay_status'] = ul1_p_nodes[5].get_text()
        order_data['book_date'] = ul1_p_nodes[7].get_text()
        return order_data

    def parse_court(self, result_data, page_url, html_cont, week_day):
        if page_url is None or html_cont is None:
            return
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        new_urls = self._get_news_url(page_url, soup, week_day)
        self._get_date_data(result_data, page_url, soup)
        return new_urls

    def parse_book_order_and_get_confirm_data(self, html_cont):
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        return self._get_confirm_data(soup)

    def parse_order_detail(self, html_cont, order_id):
        soup = BeautifulSoup(html_cont, 'html.parser', from_encoding='utf-8')
        return self._get_order_data(soup, order_id)