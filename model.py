# The MIT License
# 
# Copyright (c) 2008 William T. Katz
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

import pickle

from google.appengine.ext import db
from google.appengine.ext import search
import logging
import config

# The below was pulled due to computational quota issues on large posts.
# Works with dev server but not after uploading to cloud.
# class Article(search.SearchableModel):

class Article(db.Model):
    permalink = db.StringProperty(required=True)
    legacy_id = db.StringProperty()     # Useful for aliasing of old urls
    title = db.StringProperty(required=True)
    article_type = db.StringProperty(required=True, 
                                     choices=set(["page", "blog"]))
    body = db.TextProperty(required=True)
    # If available, we use 'excerpt' to summarize instead of 
    # extracting the first 68 words of 'body'.
    excerpt = db.TextProperty()
    html = db.TextProperty()        # This is autogenerated from body
    published = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now_add=True)
    format = db.StringProperty(required=True, 
                               choices=set(["html", "textile", 
                                            "markdown", "text"]))
    tags = db.ListProperty(db.Category)
    # Picked dict for sidelinks, associated Amazon items, etc.
    assoc_dict = db.BlobProperty()
    num_comments = db.IntegerProperty(default=0)

    # Serialize data that we'd like to store with this article.
    # Examples include relevant (per article) links and associated 
    #  Amazon items.
    def set_associated_data(self, data):
        self.assoc_dict = pickle.dumps(data)

    def get_associated_data(self):
        return pickle.loads(self.assoc_dict)

    def full_permalink(self):
        return config.blog['root_url'] + '/' + self.permalink
    
    def rfc3339_published(self):
        return self.published.strftime('%Y-%m-%dT%H:%M:%SZ')

    def rfc3339_updated(self):
        return self.updated.strftime('%Y-%m-%dT%H:%M:%SZ')

    def is_big(self):
        if len(self.html) > 2000 or 
           '<img' in self.html or 
           '<code>' in self.html or 
           '<pre>' in self.html:
            return True
        else:
            return False

class Comment(db.Model):
    permalink = db.StringProperty(required=True)
    name = db.StringProperty()
    email = db.EmailProperty()
    homepage = db.StringProperty()
    title = db.StringProperty()
    body = db.TextProperty(required=True)
    published = db.DateTimeProperty(auto_now_add=True)
    article = db.ReferenceProperty(Article)
    # Describe thread tree.  Sort on this field to order comments.
    thread = db.StringProperty(required=True)
