# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy_splash import SplashRequest
import datetime
import json
from pkgutil import get_data


class Spider(scrapy.Spider):

    name = "baidu"
    http_user = 'd2a3856dc0964db68bd44542f6ed4cdd'
    start_urls = ['https://tieba.baidu.com']  #/f?ie=utf-8&kw={0}&fr=search'.format(key) for key in KEYWORDS]
    key_url = '/f?ie=utf-8&kw={0}&fr=search'
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    item_fields = ['word', 'date_scraped', 'url',
                   'user_id', 'user_name', 'post_content', 'post_datetime', 'post_id',
                   'comments',
                   'image_urls', 'image_post_id']
    comments_fields = ['comment_user_id', 'comment_user_name', 'comment_content',
                       'comment_datetime', 'comment_id', 'comment_img_url']


    def parse(self, response):
        for word in self.settings.get('KEYWORDS'):
            url = response.urljoin(self.key_url.format(word))
            self.log('Parse_keyword: {}'.format(url))
            yield SplashRequest(url=url, callback=self.parse_keyword,
                                meta={"word": word}, endpoint='execute',
                                args={'wait': 2, 'lua_source': lua_go_scroll_bottom})

    def scrapy_shell_test(self):
        from scrapy_splash import SplashRequest
        http_user = 'd2a3856dc0964db68bd44542f6ed4cdd'
        start_urls = ['https://tieba.baidu.com/']
        key_url = 'f?ie=utf-8&kw={0}&fr=search'
        key_words = ['sample1', 'sample2']
        url = start_urls[0] + key_url.format(key_words[5])
        req = SplashRequest(url=url, endpoint='execute',
                            # dont_process_response=True,
                            args={'wait': 5, 'lua_source': lua_go_scroll_bottom})
        # reqb = scrapy.Request(url=url, meta={'splash': {
        #     'endpoint': 'execute',
        #     'dont_process_response': True,
        #     'args': {'wait': 2, 'lua_source': lua_go_scroll_bottom}}
        # })
        # fetch(req)
        # Selector(response).xpath('//*[@id="thread_list"]').extract()

    def parse_keyword(self, response):
        article_urls_suffix = self.extract(response, '//*[@id="thread_list"]//*[contains(@class, "threadlist_title")]//@href')
        # print(article_urls_suffix)
        article_urls = ['https://tieba.baidu.com' + url for url in article_urls_suffix if 'baidu.php?url' not in url]
        self.log("{}: Number of article_urls: {}".format(response.meta['word'], len(article_urls)))

        for article_url in article_urls:
            # yield {'word': 'lalaland'}
            yield SplashRequest(url=article_url, callback=self.parse_baidu_post,
                                meta={"word": response.meta['word']}, endpoint='render.html')#execute',
                                #args={'wait': 2, 'lua_source': lua_go_scroll_bottom})
            # yield SplashRequest(url=article_url,
            #                      callback=self.parse_baidu_post,
            #                      meta={'word': response.meta['word']},
            #                     args={'wait': 1}
            #                      )
            # yield scrapy.Request(url=article_url,
            #                      callback=self.parse_baidu_post,
            #                      meta={'word': response.meta['word']}
            #                      )
            # print('Article Url: {}'.format(article_url))

        next_page_url = self.extract_first(response, '//a[@class="next pagination-item "]/@href')
        if next_page_url is not None:
            self.log("Next page url: {}".format(next_page_url))
            next_page_url = self.prepend_url_schema(next_page_url)
            yield SplashRequest(url=next_page_url, callback=self.parse_keyword,
                                meta={"word": response.meta['word']}, endpoint='execute',
                                args={'wait': 2, 'lua_source': lua_go_scroll_bottom})
            # yield SplashRequest(url=next_page_url, callback=self.parse,
            #                     meta={"word": response.meta['word']}, endpoint='execute',
            #                     args={'wait': 2, 'lua_source': lua_go_scroll_bottom}
            #                     )

    @staticmethod
    def post_el(id):
        return '//div[@class="p_postlist"]//div[contains(@class, "post")]//div[contains(@id, "post_content")][@id="{}"]/../../..'.format(id)

    def parse_baidu_post(self, response):
        print('Item crawling start')
        r = {k: None for k in self.item_fields}
        post_comments_data_fields = self.extract(response, '//div[@class="p_postlist"]/div[contains(@class, "post")]/@data-field')
        post_comments_ids = self.extract(response, '//div[@class="p_postlist"]/div[contains(@class, "post")]//div[contains(@id, "post_content")]/@id')
        post_id = post_comments_ids[0]
        post_data_fields = json.loads(post_comments_data_fields[0])

        r['word'] = response.meta['word']
        r['date_scraped'] = datetime.datetime.today().strftime('%Y%m%d')
        r['url'] = response.url

        r['post_id'] = post_id
        try:
            r['user_id'] = post_data_fields['author']['user_id']
        except KeyError:
            r['user_id'] = "anonym"
        r['user_name'] = post_data_fields['author']['user_name']
        try:
            r['post_content'] = post_data_fields['content']['content']
        except KeyError:
            r['post_content'] = self.extract(response, '//*[@id="{}"]/text()'.format(post_id))
        r['post_datetime'] = self.extract_first(response, self.post_el(post_id) + '//div[contains(@class, "post-tail-wrap")]/span[last()]/text()')
        r['post_img_url'] = self.extract(response, self.post_el(post_id) + '//div[contains(@id, "post_content")]//img/@src')

        r['image_urls'] = self.extract(response, '//div[contains(@id, "post_content")]//img/@src')
        r['image_post_id'] = self.extract(response, '//div[contains(@id, "post_content")]//img/../@id')

        # COMMENTS ON PAGE 1
        comment_ids = post_comments_ids[1:]
        r['comments'] = []
        for id in comment_ids:
            r['comments'].append(self.parse_comment(response, id))

        # COMMENTS ON FURTHER PAGES IF PRESENT
        # THIS IS SOMEWHAT CHAINING REQUESTS INTO EACH OTHER AND DEFERRED UNTIL REST WORKS
        cnt_pages_txt = self.extract(response, '//*[@class="l_posts_num"]/*[@class="l_reply_num"]/span[last()]/text()')
        cnt_urls = self.get_cnt_urls(response, cnt_pages_txt)
        if False and len(cnt_urls) > 0:
            # chaining item build into multiple requests
            for pn_url in cnt_urls:
                print('Another comment url: {}'.format(pn_url))
                yield SplashRequest(url=pn_url,
                                    callback=self.parse_post_comments_page,
                                    endpoint='render.html',
                                    meta={'r': r, 'cnt_urls': cnt_urls})
            # now this item includes comments parsed over multiple requests
            yield r
        else:
            yield r

    def get_cnt_urls(self, response, cnt_pages_txt):
        cnt_pages = []
        for item in cnt_pages_txt:
            if self.is_int(item):
                cnt_pages.append(int(item))
        cnt_pages = max(cnt_pages)
        # also work with just a single page
        cnt_urls = [response.urljoin('?pn={}'.format(i)) for i in range(1, cnt_pages + 1)]
        self.log("number of posts per page: {}".format(len(cnt_pages_txt)))
        return cnt_urls

    def parse_comment(self, response, id):
        c = {k: None for k in self.comments_fields}
        comment_data_fields = self.extract_first(response, self.post_el(id) + '/../@data-field')
        try:
            c['comment_user_id'] = json.loads(comment_data_fields)['author']['user_id']
        except KeyError:
            c['comment_user_id'] = 'anonympost_comments_data_fields'
        c['comment_user_name'] = json.loads(comment_data_fields)['author']['user_name']
        c['comment_content'] = json.loads(comment_data_fields)['content']['content']
        c['comment_id'] = id
        c['comment_datetime'] = self.extract_first(response, self.post_el(id) + '//div[contains(@class, "post-tail-wrap")]/span[last()]/text()')
        c['comment_img_url'] = self.extract(response, self.post_el(id) + '//div[contains(@id, "post_content")]//img/@src')
        return c

    def parse_post_comments_page(self, response):
        r = response.meta['r']
        post_comments_ids = self.extract(response, '//div[@class="p_postlist"]/div[contains(@class, "post")]//div[contains(@id, "post_content")]/@id')
        additional_comments = []
        for id in post_comments_ids:
            additional_comments.append(self.parse_comment(response, id))
        r['comments'] += additional_comments
        r['image_urls'] += self.extract(response, '//div[contains(@id, "post_content")]//img/@src')
        return r

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
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False

lua_go_scroll_bottom = """
            function main(splash)
                local num_scrolls = 10
                local scroll_delay = 1.0
            
                local scroll_to = splash:jsfunc("window.scrollTo")
                local get_body_height = splash:jsfunc(
                    "function() {return document.body.scrollHeight;}"
                )
                assert(splash:go(splash.args.url))
                splash:wait(splash.args.wait)
                
                local i = 0
                while not splash:select('[id="thread_list"]') and i < 5 do
                    splash:wait(1)
                    i = i + 1
                end
                splash:wait(0.1)
                
                for _ = 1, num_scrolls do
                    scroll_to(0, get_body_height())
                    splash:wait(scroll_delay)
                end        
                return splash:html()
            end
            """