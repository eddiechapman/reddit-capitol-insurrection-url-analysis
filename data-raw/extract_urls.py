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
import markdown

INFILE = pathlib.Path.cwd() / 'data-raw' / 'quotation_manager_output.csv'
OUTFILE = pathlib.Path.cwd() / 'data-raw' / 'extracted_urls.csv'


class NoUrlsFoundException(Exception):
    def __init__(self):
        self.message = 'No URLs were found in quotation content'
        super().__init__(self.message)


class MultipleUrlsFoundException(Exception):
    def __init__(self, n):
        self.message = f'{n} URLs were found in quotation content'
        super().__init__(self.message)


def strip_markup(content):
    html = markdown.markdown(content)
    soup = bs4.BeautifulSoup(html, 'html.parser')
    
    return ' '.join(soup.stripped_strings)


def _extract_url(content):
    pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'

    return re.findall(pattern, content)


def extract_url(content):
    urls = set(m for m in _extract_url(content))
    
    if not urls:
        raise NoUrlsFoundException
    elif len(urls) > 1:
        raise MultipleUrlsFoundException(len(urls))
    
    return list(urls)[0]
    

class UrlEvidence:
    
    def __init__(self, document_id, quote_id, **kwargs):
        self.quote_id = quote_id
        self.document_id = document_id
        self.note = kwargs.get('note')
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
                self.profile = self.get_param(1)
                self.content = self.get_param(3)
            
            if self.platform == 'facebook.com':
                self.profile = self.get_param(1)
                self.content = self.get_param(3)
            
            if self.platform == 'reddit.com':
                self.community = self.get_param(2)
                self.profile = self.get_param(6) or self.get_param(4)
                self.content = self.get_param(5)
                
            if self.platform == 'youtube.com':
                params = parse_qs(self.query)
                if params:
                    self.content = params.get('v', [])[0]
            
            if self.platform == 'youtu.be':
                self.platform = 'youtube.com'
                self.content = self.get_param(1)
      
    def get_param(self, idx):
        try:
            param = self.params.split('\\')[idx]
        except IndexError:
            return None
        else:
            return param
        
    def to_dict(self):
        return {
            'quote_id': self.quote_id,
            'document_id': self.document_id,
            'note': self.note,
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
            'quote_id',
            'document_id',
            'note',
            'url',
            'netloc',
            'path',
            'params',
            'query',
            'fragment',
            'platform',
            'profile',
            'content',
            'community'
        ]
        

def main():
    parsed_url_rows = []

    with INFILE.open('r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            if 'evidence' in row['Codes']:
                content = strip_markup(row['Quotation Content'])

                try:
                    url = extract_url(content)
                except (NoUrlsFoundException, MultipleUrlsFoundException) as e:
                    evidence_url = UrlEvidence(
                        document_id=row['Document'], 
                        quote_id=row['ID'], 
                        note=e.message
                    )
                else:
                    evidence_url = UrlEvidence(
                        document_id=row['Document'], 
                        quote_id=row['ID'], 
                        url=url  
                    )
                
                parsed_url_rows.append(evidence_url.to_dict())

    with OUTFILE.open('w') as f:
        writer = csv.DictWriter(f, fieldnames=UrlEvidence.fieldnames())
        writer.writeheader()
        writer.writerows(parsed_url_rows)


if __name__ == '__main__':
    main()
