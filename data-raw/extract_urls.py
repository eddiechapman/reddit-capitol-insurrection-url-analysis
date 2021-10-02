#!/usr/bin/env python3
"""
Analyze URLs submitted as evidence to the Reddit 1/6 megathread.

infile should be the quotation manager export file from Atlas.ti.

"""
import csv
import pathlib
import re
from urllib.parse import urlparse, parse_qs

import bs4
from markdown import markdown

INFILE = pathlib.Path.cwd() / 'data-raw' / 'quotes.csv'
OUTFILE = pathlib.Path.cwd() / 'data-raw' / 'extracted_urls.csv'

    
class UrlEvidence:
    
    def __init__(self, document_id, quote_id, **kwargs):
        self.quote_id = quote_id
        self.document_id = document_id
        self.url = kwargs.get('url')
        self.netloc = kwargs.get('netloc')
        self.path = kwargs.get('path')
        self.params = kwargs.get('params')
        self.query = kwargs.get('query')
        self.fragment = kwargs.get('fragment')
        self.platform = kwargs.get('platform')
        self.profile = kwargs.get('profile')
        self.content = kwargs.get('content')
        self.community = kwargs.get('community')
        
        if kwargs.get('url'):
            u = urlparse(self.url)
            self.netloc = u.netloc
            self.path = u.path
            self.params = u.params
            self.query = u.query
            self.fragment = u.fragment
            
            self.platform = self.netloc.replace('www.', '')

            if self.platform == 'mobile.twitter.com':
                self.platform = 'twitter.com'
            
            if self.platform == 'twitter.com':
                self.profile = self.path_segment(1)
                self.content = self.path_segment(3)
            
            if self.platform == 'facebook.com':
                self.profile = self.path_segment(1)
                self.content = self.path_segment(3)
            
            if self.platform == 'reddit.com':
                self.community = self.path_segment(2)
                self.profile = self.path_segment(6) or self.path_segment(4)
                self.content = self.path_segment(5)
                
            if self.platform == 'm.youtube.com':
                self.platform = 'youtube.com'
                
            if self.platform == 'youtube.com':
                params = parse_qs(self.query)
                if params:
                    try:
                        self.content = params.get('v', [])[0]
                    except IndexError:
                        self.content = None
            
            if self.platform == 'youtu.be':
                self.platform = 'youtube.com'
                self.content = self.path_segment(1)
                
            if self.platform == 'instagram.com':
                if self.path_segment(1) == 'p':
                    self.content = self.path_segment(2)
                    
            if self.platform == 'pscp.tv':
                if self.path_segment(1) != 'w':
                    self.profile = self.path_segment(2)
                    self.content = self.path_segment(3)
      
    def path_segment(self, idx):
        """
        >>> self.path
        '/p/CJ3LQcHgFZ0/'
        >>> self.path_segment(0)
        ''
        >>> self.path_segment(1)
        'p'
        >>> self.path_segment(2)
        'CJ3LQcHgFZ0'
        
        """
        try:
            param = self.path.split('/')[idx]
        except IndexError:
            return None
        else:
            return param
        
    def to_dict(self):
        return {
            'quote_id': self.quote_id,
            'document_id': self.document_id,
            'url': self.url,
            'netloc': self.netloc,
            'path': self.path,
            'params': self.params,
            'query': self.query,
            'fragment': self.fragment,
            'platform': self.platform,
            'profile': self.profile,
            'content': self.content,
            'community': self.community
        }
    
    @classmethod
    def fieldnames(cls):
        return [
            'quote_id', 'document_id', 'url', 'netloc', 'path', 'params', 
            'query', 'fragment', 'platform', 'profile', 'content', 'community'
        ]
        

def main():
    parsed_url_rows = []

    with INFILE.open('r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if not 'evidence' in row['Codes']:
                continue
              
            quote = row['Quotation Content']
            doc_id = row['Document']
            quote_id = row['ID']
            
            soup = bs4.BeautifulSoup(markdown(quote), 'html.parser')
            content = ' '.join(soup.stripped_strings)

            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

            for url in re.findall(url_pattern, content):
                url_info = UrlEvidence(doc_id, quote_id, url=url)
                parsed_url_rows.append(url_info.to_dict())

    with OUTFILE.open('w') as f:
        print(f'Writing extracted urls to {OUTFILE}')
        writer = csv.DictWriter(f, fieldnames=UrlEvidence.fieldnames())
        writer.writeheader()
        writer.writerows(parsed_url_rows)
        print('Output write successful.')


if __name__ == '__main__':
    main()
