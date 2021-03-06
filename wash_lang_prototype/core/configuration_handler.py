from __future__ import annotations

from abc import abstractmethod
from typing import Any, Type

from wash_lang_prototype.core.common import Handler
from wash_lang_prototype.core.exceptions import WashError
from wash_lang_prototype.core.executor import WashExecutor, ChromeExecutor, FirefoxExecutor, EdgeExecutor, OperaExecutor
from wash_lang_prototype.lang.wash import Configuration


class ConfigurationHandlingResult:
    """
    Encapsulates the result of configuration handling, containing the executor type to be used,
    browser options to be passed to the web driver (specified in WASH configuration),
    and other parameters specified through WASH configuration that must directly be set on the
    web driver instance (instead of using browser options).
    """
    def __init__(self, executor_type: Type[WashExecutor], browser_options: Any, implicit_wait_value: int):
        self.__executor_type = executor_type                # type: Type[WashExecutor]
        self.__browser_options = browser_options            # type: Any
        self.__implicit_wait_value = implicit_wait_value    # type: int

    @property
    def executor_type(self) -> Type[WashExecutor]:
        return self.__executor_type

    @property
    def browser_options(self) -> Any:
        return self.__browser_options

    @property
    def implicit_wait_value(self) -> int:
        return self.__implicit_wait_value


class ConfigurationHandler(Handler):
    """
    A base configuration handler implementing the default chaining behavior.
    """

    _next_configuration_handler: ConfigurationHandler = None

    def set_next(self, configuration_handler: ConfigurationHandler) -> ConfigurationHandler:
        self._next_configuration_handler = configuration_handler

        return configuration_handler

    @abstractmethod
    def handle(self, configuration: Configuration) -> ConfigurationHandlingResult:
        """
        Handles the given configuration instance by executing
        the right hand-side chain of registered configuration handlers.

        All concrete configuration handlers either handle the given Configuration instance
        or pass it to the next configuration handler in the chain.

        Args:
            configuration: The Configuration to be handled by the chain.
        """
        if self._next_configuration_handler:
            return self._next_configuration_handler.handle(configuration)

        raise WashError('Unsupported browser type')

    @classmethod
    def _extract_browser_type(cls, configuration: Configuration) -> str:
        return configuration.get_browser_type()

    @abstractmethod
    def _create_options(self, configuration: Configuration):
        pass


class ChromeConfigurationHandler(ConfigurationHandler):
    """
    Concrete implementation of ConfigurationHandler that handles configuration for Chrome browser.
    """

    def handle(self, configuration: Configuration) -> ConfigurationHandlingResult:
        browser_type = self._extract_browser_type(configuration)
        if browser_type.casefold() != "chrome":
            return super().handle(configuration)
        return ConfigurationHandlingResult(
            executor_type=ChromeExecutor,
            browser_options=self._create_options(configuration),
            implicit_wait_value=configuration.get_wait_timeout())

    def _create_options(self, configuration: Configuration):
        from selenium.webdriver import ChromeOptions

        options = ChromeOptions()
        options.headless = False
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        user_agent = configuration.get_user_agent()
        access_as_mobile_device = configuration.get_access_as_mobile_device()
        use_incognito_mode = configuration.get_use_incognito_mode()
        window_size = configuration.get_window_size()

        options.add_argument(f'--user-agent={user_agent}') if user_agent else None
        options.add_argument('--use-mobile-user-agent') if access_as_mobile_device else None
        options.add_argument('--incognito') if use_incognito_mode else None
        options.add_argument(f'--window-size={window_size[0]},{window_size[1]}') if window_size else None

        return options


class FirefoxConfigurationHandler(ConfigurationHandler):
    """
    Concrete implementation of ConfigurationHandler that handles configuration for Firefox browser.
    """

    def handle(self, configuration: Configuration) -> ConfigurationHandlingResult:
        browser_type = self._extract_browser_type(configuration)
        if browser_type.casefold() != "firefox":
            return super().handle(configuration)
        return ConfigurationHandlingResult(
            executor_type=FirefoxExecutor,
            browser_options=self._create_options(configuration),
            implicit_wait_value=configuration.get_wait_timeout())

    def _create_options(self, configuration: Configuration):
        from selenium.webdriver import FirefoxOptions

        # TODO (fivkovic): Connect options and config.

        options = FirefoxOptions()
        options.headless = False
        options.add_argument("--window-size=1920,1080")

        return options


class EdgeConfigurationHandler(ConfigurationHandler):
    """
    Concrete implementation of ConfigurationHandler that handles configuration for Edge browser.
    """

    def handle(self, configuration: Configuration) -> ConfigurationHandlingResult:
        browser_type = self._extract_browser_type(configuration)
        if browser_type.casefold() != "edge":
            return super().handle(configuration)
        return ConfigurationHandlingResult(
            executor_type=EdgeExecutor,
            browser_options=self._create_options(configuration),
            implicit_wait_value=configuration.get_wait_timeout())

    def _create_options(self, configuration: Configuration):

        # TODO (fivkovic): Use additional library to set options
        # https://stackoverflow.com/questions/65171183/how-to-run-microsoft-edge-headless-with-selenium-python

        # TODO (fivkovic): Connect options and config.

        return None


class OperaConfigurationHandler(ConfigurationHandler):
    """
    Concrete implementation of ConfigurationHandler that handles configuration for Opera browser.
    """

    def handle(self, configuration: Configuration) -> ConfigurationHandlingResult:
        browser_type = self._extract_browser_type(configuration)
        if browser_type.casefold() != "opera":
            return super().handle(configuration)
        return ConfigurationHandlingResult(
            executor_type=OperaExecutor,
            browser_options=self._create_options(configuration),
            implicit_wait_value=configuration.get_wait_timeout())

    def _create_options(self, configuration: Configuration):
        from selenium.webdriver.opera.options import Options

        # TODO (fivkovic): Connect options and config.

        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1080")

        return options
