# -*- coding: utf-8 -*-
import re
import time
import asyncio
import urllib.parse

from src.common.pluginbase import AsyncPluginBase
from src.common.output import Output

from src.extra import utils, decorators


class HTTPHeadersGetter(Output, AsyncPluginBase):
    def __init__(self, *args, **kwargs):
        kwargs.update({'final_file': 'http_headers'})
        super(HTTPHeadersGetter, self).__init__(*args, **kwargs)
        self._timeout = kwargs.get('timeout', .1)
        self._read_timeout = kwargs.get('read_timeout', .1)
        self._only_jsonrpc = kwargs.get('only_jsonrpc', False)

        self.tmp_file = utils.create_tmp_file(prefix='pydrommer_')

    @staticmethod
    async def _prepare_final_data(headers, host, port):
        node = f'{host}:{port}-'
        if headers:
            for header in headers:
                node += f'<{header}>'

            return node

        return

    @staticmethod
    async def _check_on_jsonrpc(headers):
        pattern = re.compile(r'jsonrpc', re.IGNORECASE)

        for header in headers:
            if re.search(pattern, header):
                return header

    async def _read_headers(self, reader):
        lines = []

        while True:
            line = await asyncio.wait_for(reader.readline(), self._read_timeout)

            if not line:
                break

            line = line.decode('utf-8').rstrip()

            if line:
                lines.append(line)

        return lines if lines else None

    @staticmethod
    async def _write_query(url_path, url_hostname, writer):
        query = (
            f"HEAD {url_path or '/'} HTTP/1.0\r\n"
            f"Host: {url_hostname}\r\n"
            f"\r\n"
        )

        writer.write(query.encode('utf-8'))
        await writer.drain()

    @staticmethod
    async def _get_valid_port(port, url_scheme):
        if port:
            return port

        if url_scheme == 'https':
            port = 443
        else:
            port = 80

        return port

    async def _header_reading_handler(self, *args):
        url, writer, reader = args
        await self._write_query(url.path, url.hostname, writer)

        try:
            headers = await self._read_headers(reader)
        except (asyncio.futures.TimeoutError, ConnectionResetError):
            headers = None
        finally:
            writer.close()

        return headers

    async def _open_connection(self, url_scheme, url_hostname, port):
        valid_port = await self._get_valid_port(port, url_scheme)

        if url_scheme == 'https':
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(url_hostname, valid_port, ssl=True), timeout=self._read_timeout
            )
        else:
            reader, writer = await asyncio.wait_for(
                asyncio.open_connection(url_hostname, valid_port), timeout=self._read_timeout
            )

        return reader, writer

    @staticmethod
    async def _get_valid_url(url, port):
        prefixes = {
            80: 'http://',
            443: 'https://'
        }

        if not url.startswith('http'):
            return f'{prefixes.get(port, "http://")}{url}'

        return url

    async def _get_http_headers(self, host, port=None):
        valid_url = await self._get_valid_url(host, port)
        url = urllib.parse.urlsplit(valid_url)

        try:
            reader, writer = await self._open_connection(url.scheme, url.hostname, port)
        except (asyncio.TimeoutError, ConnectionRefusedError):
            return
        else:
            headers = await self._header_reading_handler(url, writer, reader)

        if self._only_jsonrpc and headers:
            jsonrpc_header = await self._check_on_jsonrpc(headers)

            if jsonrpc_header:
                return f'{valid_url}:{port}-{jsonrpc_header}'

        return await self._prepare_final_data(headers, valid_url, port)

    async def _http_headers_handler(self, host, ports):
        time.sleep(self._timeout)
        data_block = await asyncio.gather(
            *(self._get_http_headers(host, int(port)) for port in ports)
        )

        await decorators.async_write_to_file(
            self.tmp_file, filter(lambda x: x is not None, data_block)
        )

    async def run(self):
        await self.run_plugin(self._http_headers_handler, require_ports=True)
        self.output(self.tmp_file)
