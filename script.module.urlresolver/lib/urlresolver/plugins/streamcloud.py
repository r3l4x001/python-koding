"""
streamcloud urlresolver plugin
Copyright (C) 2012 Lynx187 

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

from t0mm0.common.net import Net
from urlresolver.plugnplay.interfaces import UrlResolver
from urlresolver.plugnplay.interfaces import PluginSettings
from urlresolver.plugnplay import Plugin
from urlresolver import common
import re

class StreamcloudResolver(Plugin, UrlResolver, PluginSettings):
    implements = [UrlResolver, PluginSettings]
    name = "streamcloud"
    domains = [ "streamcloud.eu" ]

    def __init__(self):
        p = self.get_setting('priority') or 100
        self.priority = int(p)
        self.net = Net()

    def get_media_url(self, host, media_id):
        web_url = self.get_url(host, media_id)
        resp = self.net.http_GET(web_url)
        html = resp.content
        post_url = resp.get_url()
        if re.search('>(File Not Found)<',html):
            raise UrlResolver.ResolverError('File Not Found or removed')
            
        form_values = {}
        for i in re.finditer('<input.*?name="(.*?)".*?value="(.*?)">', html):
            form_values[i.group(1)] = i.group(2).replace("download1","download2")
        html = self.net.http_POST(post_url, form_data=form_values).content

        r = re.search('file: "(.+?)",', html)
        if r:
            return r.group(1)
        else:
            raise UrlResolver.ResolverError('File Not Found or removed')

    def get_url(self, host, media_id):
            return 'http://streamcloud.eu/%s' % (media_id)

    def get_host_and_id(self, url):
        r = re.search('http://(?:www.)?(.+?)/([0-9A-Za-z]+)', url)
        if r:
            return r.groups()
        else:
            return False

    def valid_url(self, url, host):
        if self.get_setting('enabled') == 'false': return False
        return re.match('http://(www.)?streamcloud.eu/[0-9A-Za-z]+', url) or 'streamcloud' in host
