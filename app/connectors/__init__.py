"""Connectors package for external marketplace and business systems."""
from app.connectors.base import BaseConnector
from app.connectors.ozon import OzonConnector, ozon_connector
from app.connectors.sbermarket import SberMarketConnector, sbermarket_connector
from app.connectors.wildberries import WildberriesConnector, wb_connector
from app.connectors.yandex_market import YandexMarketConnector, ym_connector

__all__ = [
    "BaseConnector",
    "WildberriesConnector",
    "wb_connector",
    "OzonConnector",
    "ozon_connector",
    "YandexMarketConnector",
    "ym_connector",
    "SberMarketConnector",
    "sbermarket_connector",
]

