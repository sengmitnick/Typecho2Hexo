# -*- coding: utf-8 -*-
__author__ = 'Zhou Rongyu'

import codecs
import os
import torndb
import arrow
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# 把数据库相关信息改成自己的，默认localhost（和数据库同机的话不需要修改）
db = torndb.Connection(host="localhost", database="数据库", user="root", password="密码")
# 创建分类和标签
categories = db.query("select type, slug, name from typecho_metas")
for cate in categories:
    path = 'data/%s' % cate.slug
    if not os.path.exists(path):
        os.makedirs(path)
    f = codecs.open('%s/index.md' % path, 'w', "utf-8")
    f.write("title: %s\n" % cate.slug)
    f.write("date: %s\n" % arrow.now().format('YYYY-MM-DD HH:mm:ss'))
    # 区分分类和标签
    if cate.type == 'category':
        f.write('type: "categories"\n')
    elif cate.type == 'tags':
        f.write('type: "tags"\n')
    # 禁止评论
    f.write("comments: false\n")
    f.write("---\n")
    f.close()

# 创建文章
entries = db.query("select cid, title, slug, text, created from typecho_contents where type='post'")
for e in entries:
    title = e.title.encode("utf-8")
    cid = e.cid
    content = e.text
    if content is None:
        content = ""
    content = str(content.encode("utf-8")).replace('<!--markdown-->', '')
    tags = []
    category = ""
    # 找出文章的tag及category
    metas = db.query(
        "select type, name, slug from `typecho_relationships` ts, typecho_metas tm where tm.mid = ts.mid and ts.cid = %s",
        e.cid)
    for m in metas:
        if m.type == 'tag':
            tags.append(m.name)
        if m.type == 'category':
            category = m.slug
    path = 'data/_posts/'
    if not os.path.exists(path):
        os.makedirs(path)
    f = codecs.open('%s%s.md' % (path, cid), 'w', "utf-8")
    f.write("title: %s\n" % title)
    f.write("date: %s\n" % arrow.get(e.created).format('YYYY-MM-DD HH:mm:ss'))
    f.write("categories: %s\n" % category)
    f.write("tags: [%s]\n" % ','.join(tags))
    f.write("---\n")
    f.write(content)
    f.close()