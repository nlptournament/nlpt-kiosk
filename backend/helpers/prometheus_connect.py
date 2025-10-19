"""
A Class for collection of metrics from a Prometheus Host.

It's a dramatic stripped down version of: https://github.com/4n4nd/prometheus-api-client-python
as the library requires matplotlib, which is a problem for me, when building containers for arm

this version of the class is all I need for now
"""
from urllib.parse import urlparse
import logging
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests import Session


class PrometheusApiClientException(Exception):
    """API client exception, raises when response status code != 200."""
    pass


# set up logging

_LOGGER = logging.getLogger(__name__)

# In case of a connection failure try 2 more times
MAX_REQUEST_RETRIES = 3
# wait 1 second before retrying in case of an error
RETRY_BACKOFF_FACTOR = 1
# retry only on these status
RETRY_ON_STATUS = [408, 429, 500, 502, 503, 504]


class PrometheusConnect:
    """
    A Class for collection of metrics from a Prometheus Host.

    :param url: (str) url for the prometheus host
    :param headers: (dict) A dictionary of http headers to be used to communicate with
        the host. Example: {"Authorization": "bearer my_oauth_token_to_the_host"}
    :param disable_ssl: (bool) If set to True, will disable ssl certificate verification
        for the http requests made to the prometheus host
    :param retry: (Retry) Retry adapter to retry on HTTP errors
    :param auth: (optional) Auth tuple to enable Basic/Digest/Custom HTTP Auth. See python
        requests library auth parameter for further explanation.
    :param proxy: (Optional) Proxies dictionary to enable connection through proxy.
        Example: {"http_proxy": "<ip_address/hostname:port>", "https_proxy": "<ip_address/hostname:port>"}
    :param session (Optional) Custom requests.Session to enable complex HTTP configuration
    :param timeout: (Optional) A timeout (in seconds) applied to all requests
    """

    def __init__(
        self,
        url: str = 'http://127.0.0.1:9090',
        headers: dict = None,
        disable_ssl: bool = False,
        retry: Retry = None,
        auth: tuple = None,
        proxy: dict = None,
        session: Session = None,
        timeout: int = None,
    ):
        """Functions as a Constructor for the class PrometheusConnect."""
        if url is None:
            raise TypeError('missing url')

        self.headers = headers
        self.url = url
        self.prometheus_host = urlparse(self.url).netloc
        self._all_metrics = None
        self._timeout = timeout

        if retry is None:
            retry = Retry(
                total=MAX_REQUEST_RETRIES,
                backoff_factor=RETRY_BACKOFF_FACTOR,
                status_forcelist=RETRY_ON_STATUS,
            )

        self.auth = auth

        if session is not None:
            self._session = session
        else:
            self._session = requests.Session()
            self._session.verify = not disable_ssl

        if proxy is not None:
            self._session.proxies = proxy
        self._session.mount(self.url, HTTPAdapter(max_retries=retry))

    def check_prometheus_connection(self, params: dict = None) -> bool:
        """
        Check Promethus connection.

        :param params: (dict) Optional dictionary containing parameters to be
            sent along with the API request.
        :returns: (bool) True if the endpoint can be reached, False if cannot be reached.
        """
        response = self._session.get(
            '{0}/'.format(self.url),
            verify=self._session.verify,
            headers=self.headers,
            params=params,
            auth=self.auth,
            cert=self._session.cert,
            timeout=self._timeout,
        )
        return response.ok

    def custom_query(self, query: str, params: dict = None, timeout: int = None):
        """
        Send a custom query to a Prometheus Host.

        This method takes as input a string which will be sent as a query to
        the specified Prometheus Host. This query is a PromQL query.

        :param query: (str) This is a PromQL query, a few examples can be found
            at https://prometheus.io/docs/prometheus/latest/querying/examples/
        :param params: (dict) Optional dictionary containing GET parameters to be
            sent along with the API request, such as "time"
        :param timeout: (Optional) A timeout (in seconds) applied to the request
        :returns: (list) A list of metric data received in response of the query sent
        :raises:
            (RequestException) Raises an exception in case of a connection error
            (PrometheusApiClientException) Raises in case of non 200 response status code
        """
        params = params or {}
        data = None
        query = str(query)
        timeout = self._timeout if timeout is None else timeout
        # using the query API to get raw data
        response = self._session.get(
            '{0}/api/v1/query'.format(self.url),
            params={**{'query': query}, **params},
            verify=self._session.verify,
            headers=self.headers,
            auth=self.auth,
            cert=self._session.cert,
            timeout=timeout,
        )
        if response.status_code == 200:
            data = response.json()['data']['result']
        else:
            raise PrometheusApiClientException(
                'HTTP Status Code {} ({!r})'.format(response.status_code, response.content)
            )

        return data
