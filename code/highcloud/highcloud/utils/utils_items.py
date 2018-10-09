# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class HighcloudItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class SocialUser(Item):
    '''
        用户信息
    '''

    id = Field() ## 用户ID
    nick = Field() ## 昵称
    name = Field() ## 用户名
    image = Field() ## 头像地址
    province = Field() ## 所在省
    city = Field() ## 所在城市
    description = Field() ## 用户描述
    url = Field() ## 用户地址
    personal_site = Field() ## 个人网站
    gender = Field() ## 性别
    followers = Field() ## 粉丝数
    following = Field() ## 关注数
    status = Field() ## 微博数
    favourites = Field() ## 收藏数
    create_at = Field() ## 注册时间


class SocialContent(Item):
    '''
        内容信息
    '''
    id = Field() ## 内容ID
    created_at = Field() ## 发布时间
    text = Field() ## 内容信息
    url = Field() ## 链接地址
    source = Field() ## 内容来源
    image = Field() ## 内容配图URL
    geo = Field() ## 地理位置信息
    user = Field() ## 发布用户ID
    retweeted = Field() ## 转发详情(转发ID列表)
    comments = Field() ## 评论详情(评论ID列表)
    reposts_count = Field() ## 转发数
    comments_count = Field() ## 评论数
    like_count = Field() ## 点赞数
    url_links = Field() ## 文字链接信息(key为带有超链接的文字, value为URL或用户ID, 当key为以TEXT_IMAGE_开头时,表示文字中显示的图片,value为图片URL)


class SocialTrans(Item):
    '''
        转发信息
    '''
    id = Field() ## 内容ID
    created_at = Field() ## 发布时间
    text = Field() ## 内容信息
    source = Field() ## 内容来源
    image = Field() ## 内容配图URL
    geo = Field() ## 地理位置信息
    user = Field() ## 发布用户ID
    retweeted = Field() ## 转发详情(内容ID列表)
    comments = Field() ## 评论详情(评论ID列表)
    reposts_count = Field() ## 转发数
    comments_count = Field() ## 评论数
    like_count = Field() ## 点赞数
    url_links = Field() ## 文字链接信息(字典类型: key为带有超链接的文字, value为URL或用户ID)


class SocialComment(Item):
    '''
        评论信息
    '''
    id = Field() ## 评论ID
    created_at = Field() ## 发布时间
    text = Field() ## 评论信息
    source = Field() ## 评论来源
    image = Field() ## 评论配图URL
    geo = Field() ## 地理位置信息
    user = Field() ## 评论用户ID
    reply_comment = Field() ## 当本评论属于对另一评论的回复时返回此字段(评论ID列表)
    reposts_count = Field() ## 转发数
    comments_count = Field() ## 评论数
    like_count = Field() ## 点赞数
    url_links = Field() ## 文字链接信息(字典类型: key为带有超链接的文字, value为URL或用户ID)

