# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
import datetime
from scrapy_splash import SplashRequest
import math
from pkgutil import get_data


class Spider(scrapy.Spider):

    name = "weibo"
    http_user = 'd2a3856dc0964db68bd44542f6ed4cdd'
    start_urls = ['https://s.weibo.com/']
    key_url = 'weibo/{0}'
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    item_fields = ['word', 'date_scraped', 'url',
                   'user_id', 'user_name', 'post_content', 'post_datetime', 'post_id',
                   'comments',
                   'image_urls', 'image_post_id',
                   'user_device']
    comments_fields = ['comment_user_id', 'comment_user_name', 'comment_content',
                      'comment_datetime', 'comment_id', 'comment_img_url']

    def parse(self, response):
        for word in self.settings.get('KEYWORDS'):
            url = response.urljoin(self.key_url.format(word))
            self.log('Parse_keyword: {}'.format(url))
            yield SplashRequest(url=url, callback=self.parse_keyword, meta={"word": word},
                                endpoint='render.html',
                                # args={'wait': 2, 'lua_source': lua_go_url}
                                )
            # url = "https://s.taobao.com/search?q=hello"
            # reqa = SplashRequest(url=url, args={'wait': 0.5, 'html': 1})
            # reqb = scrapy.Request(url=url, meta={
            #     'splash': { 'args': {'html': 1, 'wait': 0.5}}
            # })
            # url="https://en.wikipedia.org/wiki/Diary"

    def parse_keyword(self, response):
        for mid in self.extract(response, '//*[@id="pl_feedlist_index"]//@mid'):
            comment_letter = Selector(response).xpath(
                '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[contains(@class, "card-act")]/ul/li[3]//text()'.format(
                    mid)).extract()[0]
            if not self.is_int(comment_letter[-1]):
                yield self.parse_uncommented_weibo(response, mid)
                # continue
            else:
                uid = self.get_weibo_uid(
                    self.extract_first(response,
                                 '//*[@id="pl_feedlist_index"]//div[@mid="{}"]//div[@class="avator"]/a/@href'.format(mid))
                )
                comment_url = 'https://www.weibo.com/{}/{}'.format(uid, self.mid_encode(mid))
                print(comment_url)
                weibo_r = self.parse_uncommented_weibo(response, mid)
                yield weibo_r
                # receiving error 400 on these requests. with passport.com check. anti bot measure...
                # yield SplashRequest(url=comment_url, callback=self.parse_commented_weibo,
                #                     meta={"word": response.meta['word'], "weibo_item": weibo_r},
                #                     endpoint='execute',
                #                     args={'wait': 1, 'lua_source': lua_expand_comments})

        self.log('Go next page')
        next_page_url = response.css('a.next::attr(href)').extract_first()
        if next_page_url is not None:
            next_page_url = response.urljoin(next_page_url)
            print(next_page_url)
            yield SplashRequest(url=next_page_url, callback=self.parse_keyword, meta={"word": response.meta['word']},
                                endpoint='render.html',
                                # args={'wait': 2, 'lua_source': lua_go_url}
                                )

    def parse_uncommented_weibo(self, response, mid):
        r = {k: None for k in self.item_fields}
        r['word'] = response.meta['word']
        r['url'] = response.url
        r['date_scraped'] = datetime.datetime.today().strftime('%Y%m%d')
        r['post_id'] = mid
        r['user_id'] = self.get_user_id(
            self.extract_first(response, '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//a[contains(@href, "weibo.com") and @class="name"]/@href'.format(mid))
        )
        weibo_text_hidden = '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[contains(@class, "txt") and contains(@style, "display: none")]/text()'.format(mid)
        weibo_text_all_vis = '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[contains(@class, "txt")]/text()'.format(mid)
        r['post_content'] = self.extract(response, weibo_text_hidden)
        if r['post_content'] == []:
            r['post_content'] = self.extract(response, weibo_text_all_vis)

        l_from = self.extract(response, '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[contains(@class, "from")]/a//text()'.format(mid))
        if type(l_from) == str:
            r['post_datetime'] = l_from
        elif type(l_from) == list and len(l_from) == 2:
            r['post_datetime'], r['user_device'] = l_from
        elif type(l_from) == list and len(l_from) > 0:
            r['post_datetime'] = l_from[0]

        r['user_name'] = self.extract(response, '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[contains(@class, "info")]//*[contains(@class, "name")]//text()'.format(mid))
        img_urls = self.extract(response, '//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[contains(@class, "media")]//img/@src'.format(mid))
        r['image_urls'] = [self.prepend_url_schema(url) for url in img_urls]
        return r

    def elem_comm_id(self, id):
        return '//div[@comment_id="{}"]'.format(id)

    def parse_commented_weibo(self, response):
        r = response.meta["weibo_item"]
        comment_ids = self.extract_first((response, '//div[@comment_id][@node-type="root_comment"]/@comment_id'))
        comments = []
        print(comment_ids)
        for id in comment_ids:
            c = {k: None for k in self.comments_fields}
            c['comment_user_id'] = self.extract(response, self.elem_comm_id(id) + '//a[not(@render)]/@usercard')
            c['comment_user_name'] = self.extract(response, self.elem_comm_id(id) + '//a[@usercard]/text()')
            c['comment_content'] = self.extract(response, self.elem_comm_id(id) + '//div[@class="WB_text"]/text()')
            c['comment_datetime'] = self.extract(response, self.elem_comm_id(id) + '//div[@class="list_con"]//div[@class="WB_from S_txt2"]/text()')
            c['comment_id'] = id
            # c['comment_user'], c['comment_text'] = Selector(response).xpath('//*[@id="pl_feedlist_index"]//*[@mid="{}"]//*[@node-type="feed_list_commentList"]//*[@class="txt"//text()]'.format(weibo_id)).extract()
            comments.append(c)
        r['comments'] = comments
        print('COMMENTS')
        print(comments)
        yield r

    def get_weibo_uid(self, uid):
        # example https://weibo.com/2823009565?refer_flag=1001030103_
        splits = uid.split(r'/')
        for s in range(0, len(splits)):
            if 'weibo' in splits[s]:
                s_uid = splits[s+1]
        uid_ex = ''
        for s in range(0, len(s_uid)):
            if self.is_int(s_uid[s]):
                uid_ex += s_uid[s]
            else:
                return uid_ex
        return uid_ex

    @staticmethod
    def mid_encode(mid):
        """ Convert number string tobase62 hash string.
        * @ param {String} mid weibo mid, e.g.: "201110410216293360" @ return {String} hash
        string, e.g.: "wr4mOFqpbO
        mid_encode(4194705149823124) === "FDJIeFdru"
        """
        id = str(mid)
        hash = ''
        end = len(id)
        while end > 0:
            start = end - 7
            if start < 0:
                start = 0
            num = id[start:end]
            h = Spider.mid_base62Encode(int(num))
            padding = 4 - len(h)
            if padding > 0 and start > 0:
                # not first group and not 4 length string, must add '0' padding.
                while padding > 0:
                    h = '0' + h
                    padding -= 1
            hash = h + hash
            end -= 7
        return hash

    @staticmethod
    def mid_base62Encode(num):
        abc = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        key = ''
        r = 0
        while num != 0 and len(key) < 100:
            r = num % 62
            key = abc[r] + key
            num = int(math.floor((num / 62)))
        return key

    @staticmethod
    def prepend_url_schema(url):
        if url[:2] == r"//":
            return "https:" + url
        else:
            return url

    @staticmethod
    def extract(response, xpath):
        return Selector(response).xpath(xpath).extract()

    @staticmethod
    def extract_first(response, xpath):
        return Selector(response).xpath(xpath).extract_first()

    @staticmethod
    def get_user_id(url):
        # example url
        # "https://weibo.com/5588802329?refer_flag=1001030103_"
        snippet = url.split('weibo.com')[1][1:]
        char_idx = snippet.find('?')
        if char_idx > 0:
            return snippet[:char_idx]
        else:
            return snippet

    @staticmethod
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

lua_expand_comments = """
    function main(splash)
        assert(splash:go(splash.args.url))
        splash:wait(splash.args.wait)
        
        -- 5x times. get height of body, wait a bit, scroll again
        for 0, 5, 1 do
            local feed = splash:select('div[class="repeat_list"]>div[node-type="feed_list"]')
            local feed_b = feed:bounds()
            splash:scroll_position = {y=feed_b.bottom}
            splash:wait(0.2)
        end
        -- if expand for more comments, displayed click on it, and scroll to bottom. repeat as long as button visible
        local more = splash:select('span[class="more_txt"]')
        local i = 0
        while (more~=nil and i < 10) do
            more:mouse_click()
            splash:wait(0.3)
            local more = splash:select('span[class="more_txt"]')
            i = i + 1
        end
        return splash:html()
    end
"""

lua_go_url = """
            function main(splash)
            
                assert(splash:go(splash.args.url))
                splash:wait(splash.args.wait)

                return splash:html()
            end
            """