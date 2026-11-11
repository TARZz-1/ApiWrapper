import requests
import requests.packages
from typing import List, Dict
from MainApi.exceptions import ApiWrapperException
from json import JSONDecodeError
from MainApi.models import Result
import logging

class RestAdapter:
    def __init__(self, hostname:str, api_key:str='', ver:str= 'v1', ssl_verify: bool=True, logger: logging.Logger = None):
        """Constructor for RestAdapter

         Args:
            hostname (str): The target hostname or base URL for the API.
            api_key (str, optional): The API key used for authentication. Defaults to ''.
            ver (str, optional): The API version to use in the URL. Defaults to 'v1'.
            ssl_verify (bool, optional): Whether to verify SSL certificates for requests. Defaults to True.
            logger (logging.Logger, optional): Custom logger instance for logging events. Defaults to None.
        """
        
        
        self.url = "https://{}/{}/".format(hostname, ver)
        self._api_key = api_key
        self._ssl_verify = ssl_verify
        if not ssl_verify:
            requests.packages.urllib3.disable_warnings()
        self._logger = logger or logging.getLogger(__name__)            
    def _do(self, http_method: str, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        full_url = self.url + endpoint
        headers = {'x-api-key': self._api_key}
        log_line_pre = f"method={http_method}, url={full_url}, params={ep_params}"
        log_line_post = ', '.join((log_line_pre, "success={}, status_code={}, message={}"))
        # Log HTTP params and perform an HTTP request, catching and re-raising any exceptions
        try:
            self._logger.debug(msg=log_line_pre)
            response = requests.request(method=http_method, url=full_url, verify=self._ssl_verify, headers=headers, params=ep_params, json=data)
        except requests.exceptions.RequestException as e:
            self._logger.error(msg=(str(e)))
            raise ApiWrapperException("Failed Request") from e
         # Deserialize JSON output to Python object, or return failed Result on exception
        try:
            data_out = response.json()
        except (ValueError, JSONDecodeError) as e:
            self._logger.error(msg=log_line_post.format(False,None,e))
            raise ApiWrapperException("bad JSON in response") from e
         # If status_code in 200-299 range, return success Result with data, otherwise raise exception
        check_success = 299 >= response.status_code >= 200
        log_line = log_line_post.format(check_success, response.status_code,response.reason)
        if check_success:
            self._logger.debug(msg=log_line)
            return Result(response.status_code, message=response.reason, data=data_out)
        self._logger.error(msg=log_line)
        raise ApiWrapperException(f"{response.status_code}: {response.reason}")
            
            
    def get(self, endpoint: str, ep_params: Dict = None) -> Result:
        """Send a GET request to the specified API endpoint.

        Args:
            endpoint (str): The target endpoint path for the API request.
            ep_params (Dict, optional): Optional query parameters to include in the request. Defaults to None.

        Returns:
            Result: The parsed response data returned from the API.
        """
        return self._do(http_method='GET', endpoint=endpoint, ep_params=ep_params)
        
    def post(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        """Send a POST request to the specified API endpoint.

        Args:
            endpoint (str): The target endpoint path for the API request.
            ep_params (Dict, optional): Optional query parameters to include in the request. Defaults to None.
            data (Dict, optional): The payload data to send in the body of the request. Defaults to None.

        Returns:
            Result: The parsed response data returned from the API.
        """
        return self._do(http_method='POST', endpoint=endpoint, ep_params=ep_params, data=data)
    
    def delete(self, endpoint: str, ep_params: Dict = None, data: Dict = None) -> Result:
        """Send a DELETE request to the specified API endpoint.

        Args:
            endpoint (str): The target endpoint path for the API request.
            ep_params (Dict, optional): Optional query parameters to include in the request. Defaults to None.
            data (Dict, optional): The payload data to send in the body of the request, if any. Defaults to None.

        Returns:
            Result: The parsed response data returned from the API.
        """
        return self._do(http_method='DELETE', endpoint=endpoint, ep_params=ep_params, data=data)
    