# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from urllib.parse import urljoin
import datetime


class Spider(scrapy.Spider):
    name = "58"
    regions = ['bj']
    regionst = ['yangchun', 'bazhou', 'yxx', 'linyixianq', 'xiaogan', 'xintai', 'nt', 'changningx', 'dq', 'shaoyangxian',
               'pt', 'xzpeixian', 'ws', 'lj', 'haifengxian', 'wanning', 'kaipingshi', 'zhongxiangshi', 'dingzhou',
               'qianxixian', 'cixian', 'jincheng', 'xc', 'qidongxian', 'yy', 'taizhou', 'ya', 'shuyang',
               'jingshanxian', 'yj', 'qingxu', 'chifeng', 'zouping', 'xianyang', 'nc', 'zq', 'changdu', 'zhijiang',
               'xn', 'yiyang', 'ms', 'ez', 'wudi', 'linqu', 'xa', 'honghe', 'su', 'qixia', 'gl', 'lishu', 'xuanwushi',
               'xiangyuanxian', 'dongming', 'zezhou', 'zhangpu', 'ty', 'cangzhou', 'jingzhou', 'anlu', 'jingmen', 'gz',
               'nananshi', 'fz', 'jl', 'sm', 'guannan', 'puyang', 'tongxiang', 'songyuan', 'lb', 'hegang', 'hlr',
               'alsm', 'lvliang', 'yidou', 'shehongxian', 'xianghe', 'hc', 'anyuexian', 'ls', 'changde', 'qiongzhong',
               'yulin', 'jintan', 'bycem', 'dongzhi', 'pl', 'benxi', 'hf', 'huidong', 'lfguan', 'taikang', 'lw', 'qihe',
               'shanghangxian', 'wz', 'fcg', 'linhai', 'yili', 'mengjinqu', 'tianchang', 'anqiu', 'zoucheng', 'sy',
               'linqing', 'yichuan', 'baishan', 'ly', 'zy', 'heihe', 'cangxian', 'xm', 'linzhou', 'alt', 'xiaoyi',
               'qinyang', 'hk', 'yancheng', 'yanshiqu', 'lianyuanshi', 'changzhi', 'cd', 'bt', 'tunchang',
               'huaibinxian', 'haian', 'lishui', 'qingzhen', 'qingyuan', 'bozhou', 'wx', 'ny', 'hn', 'yichun',
               'luannanxian', 'guanyun', 'sg', 'liuzhou', 'ta', 'jiyuan', 'hexian', 'tl', 'xinzhou', 'la', 'jinxian',
               'dg', 'fushun', 'lf', 'jdz', 'dandong', 'yunmeng', 'cz', 'jingjiang', 'baish', 'guanghanshi', 'fugu',
               'yingchixian', 'suzhou', 'hami', 'wf', 'xionganxinqu', 'hld', 'zc', 'xianning', 'shenmu', 'huangnan',
               'ganzi', 'mengzhou', 'zjk', 'yichengshi', 'lijin', 'diqing', 'liulin', 'ks', 'jinchang', 'sys',
               'changge', 'wuan', 'wzs', 'dy', 'yangzhong', 'fuliangxian', 'bh', 'rugao', 'wenxian', 'tongling',
               'qixianqu', 'fenyi', 'qd', 'rizhao', 'sn', 'mdj', 'panzhihua', 'mm', 'jiangyan', 'jining', 'cm', 'hd',
               'dali', 'haiyan', 'np', 'jm', 'hshi', 'hzyc', 'qdn', 'fengcheng', 'gaotang', 'sz', 'dxal', 'cilixian',
               'zaozhuang', 'yinchuan', 'wlcb', 'dunhuang', 'jianhu', 'anningshi', 'chizhou', 'ningyang', 'wjq',
               'chuzhou', 'tongcheng', 'huarong', 'px', 'shenxian', 'meihekou', 'nd', 'xuancheng', 'tz', 'shouguang',
               'lc', 'laiyang', 'kzls', 'baise', 'zd', 'huaibei', 'qingyang', 'shanxian', 'zs', 'xiangyin', 'wenling',
               'huantaixian', 'siyang', 'hq', 'betl', 'lincang', 'qingzhou', 'hezhou', 'qth', 'ningguo', 'jiaozuo',
               'xy', 'hb', 'shanda', 'xam', 'linfen', 'jx', 'zunyi', 'jms', 'zhuji', 'yuhuan', 'linyixian', 'gaoping',
               'tm', 'luohe', 'smx', 'gaomi', 'chengde', 'baoyingx', 'dt', 'km', 'yb', 'guangrao', 'xuanhan',
               'tengzhou', 'bs', 'huizhou', 'baoting', 'pingyi', 'suining', 'huanghua', 'klmy', 'st', 'luzhou', 'zx',
               'kaifeng', 'yongxing', 'sq', 'jh', 'zhangshu', 'sjz', 'deqing', 'yanling', 'yuncheng', 'changji', 'ln',
               'wuxueshi', 'yich', 'wuhai', 'suixia', 'caoxian', 'yz', 'heze', 'danyang', 'sanya', 'ankang', 'wuhu',
               'hh', 'hainan', 'yongzhou', 'dingbian', 'shexian', 'gucheng', 'beipiao', 'wugang', 'linxia', 'yujiang',
               'dl', 'shaodongxian', 'beiliushi', 'sd', 'lixian', 'gongzhuling', 'jinzhou', 'zhaozhou', 'xx', 'huadian',
               'ay', 'penglai', 'taishan', 'juancheng', 'hu', 'cn', 'hy', 'yq', 'lingshui', 'tianshui', 'xiaochang',
               'yongkang', 'xiantao', 'zhuozhou', 'anxixian', 'zixing', 'gaizexian', 'shaoyang', 'shuozhou', 'qz', 'ja',
               'qqhr', 'anshun', 'da', 'zz', 'anji', 'wuwei', 'changyishi', 'zw', 'lasa', 'chiping', 'boxing',
               'zhanjiang', 'lyyiyang', 'yt', 'lengshuijiangshi', 'shiyan', 'laizhou', 'quzhou', 'yongchunxian',
               'zhangzhou', 'zunhua', 'yingtan', 'dongtai', 'zk', 'kl', 'zh', 'nb', 'renshouxian', 'tancheng', 'kel',
               'laohekou', 'guoluo', 'zhangqiu', 'mianyang', 'pingyangxian', 'sw', 'pds', 'shangshui', 'qiyang', 'xinye',
               'df', 'leling', 'weishixian', 'jianyangshi', 'cx', 'renhuaishi', 'shaheshi', 'zhuzhou', 'changyuan',
               'mas', 'jinjiangshi', 'gushixian', 'sansha', 'liangshan', 'heyuan', 'liangshanx', 'szs', 'ab', 'liaoyuan',
               'renqiu', 'shenqiu', 'panshi', 'qux', 'xinyu', 'kaiyuan', 'ht', 'bn', 'ch', 'fudingshi', 'fuanshi',
               'guipingqu', 'zhangye', 'dh', 'changxing', 'hejian', 'hanchuan', 'nanxian', 'sheyang', 'huangshan',
               'geermushi', 'changle', 'shzhaodong', 'zaoyang', 'sl', 'bygl', 'qixianq', 'dangyang', 'liyang', 'pizhou',
               'jn', 'xf', 'yongcheng', 'huzhou', 'lingbaoshi', 'jiangshanshi', 'erds', 'gaoan', 'xinyishi', 'ys',
               'yuchengshi', 'linyi', 'bijie', 'junxian', 'am', 'guangshuishi', 'milexian', 'czguiyang', 'tr', 'yf',
               'xuyi', 'fanxian', 'zhangbei', 'fs', 'shz', 'hz', 'zhaoyuan', 'xiangtan', 'ld', 'longhai',
               'shuangfengxian', 'cs', 'suihua', 'nanchong', 'haimen', 'deyang', 'yueqingcity', 'anqing', 'songzi',
               'yanbian', 'haidong', 'bazhong', 'es', 'liling', 'suizhou', 'changlingxian', 'dazu', 'xl', 'cenxi', 'fy',
               'cixi', 'ga', 'dawu', 'xinghuashi', 'yinanxian', 'quanguo', 'as', 'donghai', 'linzhi', 'scnj',
               'yutianxian', 'xt', 'nj', 'zb', 'lz', 'yl', 'shengzhou', 'qhd', 'sp', 'ruzhou', 'luoyang', 'hx', 'tc',
               'dengzhou', 'fx', 'huaxian', 'hlbe', 'ha', 'pj', 'weihai', 'yuzhou', 'guyuan', 'liaoyang', 'qn',
               'wenchang', 'nujiang', 'gy', 'cc', 'hg', 'yiyuanxian', 'aks', 'wfd', 'yuyao', 'danzhou', 'dongping',
               'qh', 'hrb', 'tmsk', 'lankaoxian', 'fuzhou', 'wuyix', 'taixing', 'bobaixian', 'rushan', 'jyg', 'sx',
               'rituxian', 'nq', 'zmd', 'guangyuan', 'hs', 'chenzhou', 'zg', 'dx', 'th', 'sr', 'dafeng', 'yx', 'weishan',
               'nanzhang', 'bz', 'juye', 'zt', 'lepingshi', 'qianan', 'haibei', 'tlf', 'jj', 'jz', 'chaozhou', 'boluo',
               'suqian', 'wn', 'yanan', 'dz', 'qinzhou', 'by', 'yongan', 'ale', 'lufengshi', 'yuanjiangs', 'hancheng',
               'dazhou', 'zzyouxian', 'wh', 'jinhu', 'rkz', 'haining', 'mg', 'gn', 'cangnanxian', 'qianjiang',
               'hengdong', 'sihong', 'longkou', 'wuzhou', 'xiangchengshi', 'dengta', 'rongcheng', 'nanchengx', 'yanggu',
               'ganzhou', 'wuweixian', 'yk', 'tongliao', 'fengchengshi', 'tac', 'funingxian', 'bengbu', 'sanhe', 'zjj',
               'zhoushan', 'jiayuxian', 'mz', 'yc', 'jingbian', 'ruiancity', 'chibishi', 'cy', 'haikou', 'jq', 'dongyang',
               'szkunshan', 'bd', 'lfyanjiao', 'baoji', 'juxian', 'xiangshanxian', 'gt', 'tongxuxian', 'luyi', 'pe',
               'xinchang', 'lyg', 'nn', 'shishi', 'chongzuo', 'jiashanx', 'bc', 'ningjin', 'guanxian', 'tw', 'jurong',
               'fuyuxian', 'changningshi', 'zj', 'hanzhong', 'xj', 'xz', 'qidong', 'yiwu', 'gg', 'rudong', 'al', 'jixi',
               'wuyishan', 'suixian', 'wenshang', 'pinghushi', 'feicheng', 'ts', 'xiangshui', 'qxn', 'shayangxian',
               'lyxinan', 'wuzhong', 'qj', 'xiangxi', 'jy', 'lps', 'snj', 'pld']

    start_urls = ['https://58.com/']
    url_template = 'https://{0}.58.com/sou/?key={1}'
    custom_settings = {
        'FEED_EXPORT_ENCODING': 'utf-8'
    }
    item_fields = ['word', 'date_scraped', 'url',
                   'user_id', 'user_name', 'post_content', 'post_datetime', 'post_id',  # 'price',
                   'comments',
                   'image_urls', 'image_post_id',
                   'post_title', 'region'
                   ]
    comments_fields = ['comment_user_id', 'comment_user_name', 'comment_content',
                       'comment_datetime', 'comment_id', 'comment_img_url']

    def parse(self, response):
        for region in self.regions:
            for word in self.settings.get('KEYWORDS'):
                url = self.url_template.format(region, word)
                self.log('Parse_keyword: {}'.format(url))
                yield scrapy.Request(url=url, callback=self.parse_keyword,
                                     meta={"word": word, "region": region, "region_url": url})

    def parse_keyword(self, response):
        # article_urls = response.xpath('//*[@id="searchTable"]/tr/td/a/@href').extract()
        article_urls = self.extract(response, '//*[@id="searchTable"]//a[@class="t"]//@href')
        # avoid empty ursl  like this <a class="t" href="" target="_blank" title="农民注意了！城里买了房，户口留在农村，有解决办法了！">农民注意了！城里买了房，<b>户口</b>留在农村，有解决办法了！</a>
        article_urls = [self.prepend_url_schema(u) for u in article_urls if u is not None]
        if len(article_urls) == 0:  # BJ offers lots of sites with empty results list. must stop pagination
            stop_pagination = True
        else:
            stop_pagination = False

        for article_url in article_urls:
            yield scrapy.Request(url=article_url, callback=self.parse_article,
                                 meta={'word': response.meta['word'], 'region': response.meta['region']})

        next_page_url = self.extract(response, '//a[@class="next"]/@href')
        if next_page_url is not None and len(next_page_url) > 0 and not stop_pagination:
            url = urljoin(response.meta['region_url'], next_page_url[0])
            yield scrapy.Request(url=self.prepend_url_schema(url),
                                 callback=self.parse_keyword,
                                 meta={'word': response.meta['word'], 'region': response.meta['region']})

    def parse_article(self, response):
        r = {k: None for k in self.item_fields}
        r['word'] = response.meta['word']
        r['date_scraped'] = datetime.datetime.today().strftime('%Y%m%d')
        r['region'] = response.meta['region']
        r['post_title'] = self.extract(response, '//*[@class="detail-title__name"]//text()')
        r['user_name'] = self.extract(response, '//div[@class="shopinfo"]/div[@class="shopinfo__title"]/h2//text()')  # company name
        # r['user_id'] = self.extract(response, '//a[@class="poster-name"]//text()')
        r['post_content'] = self.extract(response, '//*[@class="description_con"]//text()')
        # r['price'] = self.extract(response, )
        r['post_datetime'] = self.extract(response, '//*[@class="detail-title__info__text"][1]//text()')
        r['post_id'] = response.url
        r['user_wechat_img'] = self.extract_first(response, '//div[@class="infocard__container__pop--wx__left"]//img/@src')
        r['image_urls'] = self.extract(response, '//div[contains(@class, "ContentBox")]//img/@src')
        if r['user_wechat_img'] is not None and len(r['user_wechat_img']) > 5:  # maybe  None, '' or other little stuff. need proper url
            r['image_urls'].append(self.prepend_url_schema(r['user_wechat_img']))
        else:
            r['user_wechat_img'] = None
        r['image_urls'] = [self.prepend_url_schema(url) for url in r['image_urls']]
        r['image_post_id'] = response.url

        r['comments'] = []
        comment_elements = Selector(response).xpath('//div[@id="appraise"]/div[@class="_contentList"]/dl')
        for comment_el in comment_elements:
            c = {k: None for k in self.comments_fields}
            #'comment_user_id', 'comment_user_name', - those are hidden
            c['comment_content'] = comment_el.xpath('//dd/div/text()').extract()
            # r['comment_content'] = self.extract(response, '//div[@id="appraise"]//dd/div/text()')
            c['comment_datetime'] = comment_el.xpath('//span[contains(@class, "comentDate")]/text()').extract()
            # c['comment_datetime'] = self.extract(response, '//div[@id="appraise"]//span[contains(@class, "comentDate")]/text()')
            r['comments'].append(c)
        yield r

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