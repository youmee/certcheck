import asyncio
import http.client
import time
from abc import ABC, abstractmethod

import aiohttp
from colored import fg, attr

__version__ = '0.1'


class Colors:
    """ Colors list https://pypi.org/project/colored/ """
    intro = 40
    status_moved = 38
    status_ok = 42
    success = 46
    warning = 11
    error = 9
    exception = 197


def _longest_string(array_of_strings):
    return max(array_of_strings, key=len)


def _print_time_spend(time_spend):
    done_text = f'Done in {time_spend:.3f} s.'
    if time_spend < 1:
        done_text = f'Done in {time_spend * 1000:.0f} ms.'
    print(f'{fg(Colors.success)}{done_text}{attr("reset")}')


def _print_hello_msg(args):
    ending = 's' if len(args.domain) > 1 else ''
    domain_list = ', '.join(args.domain)
    domains_line = f'Running for domain{ending}: {domain_list}'

    print(f'{fg(Colors.intro)}{__name__.capitalize()} {__version__}')
    print(domains_line)
    print('=' * (len(domains_line)), f'{attr("reset")}')


def _get_http_status_message(status_code: int) -> str:
    return http.client.responses[status_code]


def _generate_urls(domain):
    return 'http://{url}|' \
           'https://{url}|' \
           'http://www.{url}|' \
           'https://www.{url}'.format(url=domain).split('|')


class ResponseHandler(ABC):
    @staticmethod
    @abstractmethod
    def handle(checker, url, response):
        pass


class DefaultResponseHandler(ResponseHandler):
    @staticmethod
    def handle(checker, url, response):
        if isinstance(response, Exception):
            print(f'{fg(Colors.exception)}000 EXCEPTION {attr("bold")}{url}{attr(22)}, '
                  f'Exception: {response}{attr("reset")}')
            return

        max_length = len(_longest_string(checker.urls)) + 20
        status_message = _get_http_status_message(response.status).upper()

        if response.status in [200]:
            print(f'{fg(Colors.status_ok)}{response.status} {attr("reset")}{status_message} {url}')
        elif response.status in [301, 302]:
            redirect_url = response.headers['Location']
            status_url_mess = f'{status_message} {url}'
            print(f'{fg(Colors.status_moved)}{response.status} {attr("reset")}'
                  f'{status_url_mess: <{max_length}} -> {redirect_url}')
        elif response.status in [403]:
            print(f'{fg(Colors.warning)}{response.status} {status_message}{attr("reset")} {url}')
        elif response.status in [404]:
            print(f'{fg(Colors.error)}{response.status} {status_message}{attr("reset")} {url}')
        else:
            print(f'{url}, status: {response.status}')


class UrlFirstResponseHandler(ResponseHandler):
    @staticmethod
    def handle(checker, url, response):
        if isinstance(response, Exception):
            print(f'{fg(Colors.exception)}{attr("bold")}{url}{attr(22)} --- EXCEPTION --- '
                  f'{response}{attr("reset")}')
            return

        max_length = len(_longest_string(checker.urls)) + 10
        status_message = _get_http_status_message(response.status).upper()

        if response.status in [200]:
            print(f'{fg(Colors.status_ok)}{url: <{max_length}} --- {response.status} {attr("reset")}{status_message}')
        elif response.status in [301, 302]:
            redirect_url = response.headers['Location']
            print(f'{fg(Colors.status_moved)}{url: <{max_length}} --- '
                  f'{response.status}{attr("reset")} {status_message} {attr("dim")}({redirect_url}){attr("reset")}')
        elif response.status in [403]:
            print(f'{fg(Colors.warning)}{response.status} {status_message}{attr("reset")} {url}')
        elif response.status in [404]:
            print(f'{fg(Colors.error)}{response.status} {status_message}{attr("reset")} {url}')
        else:
            print(f'{url}, status: {response.status}')


class Checker:
    def __init__(self, domains: [str],
                 response_handler: ResponseHandler = DefaultResponseHandler(),
                 follow_redirects=False,
                 timeout=5):
        self.domains = domains
        self.urls = []
        self._response_handler = response_handler
        self._follow_redirects = follow_redirects
        self._timeout = aiohttp.ClientTimeout(total=timeout)

        assert isinstance(domains, list)

        for domain in self.domains:
            self.urls += _generate_urls(domain)

    async def check(self):
        time_start = time.time()
        await self.__main(self.urls)
        _print_time_spend(time.time() - time_start)

    async def __get(self, session: aiohttp.ClientSession, url: str):
        try:
            response = await session.get(url, allow_redirects=self._follow_redirects)
            return url, response
        except (aiohttp.client_exceptions.ClientConnectorCertificateError,
                aiohttp.client_exceptions.ClientConnectorError) as e:
            return url, e
        except asyncio.TimeoutError as e:
            return url, Exception('Request timeout')

    async def __main(self, urls):
        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            tasks = [self.__get(session=session, url=u) for u in urls]
            for next_to_complete in asyncio.as_completed(tasks):
                url, response = await next_to_complete
                self._response_handler.handle(self, url, response)


def main(args):
    _print_hello_msg(args)

    response_handler = UrlFirstResponseHandler()

    if args.group_by_domain:
        for d in args.domain:
            checker = Checker(domains=[d],
                              response_handler=response_handler,
                              follow_redirects=args.follow_redirect,
                              timeout=args.timeout)
            asyncio.run(checker.check())
    else:
        checker = Checker(domains=args.domain,
                          response_handler=response_handler,
                          follow_redirects=args.follow_redirect,
                          timeout=args.timeout)
        asyncio.run(checker.check())
