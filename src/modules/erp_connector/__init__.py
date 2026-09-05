"""Módulo de integração com ERPs."""
from .connector import (
    ERPConnector,
    FileERPConnector,
    TotvsConnector,
    SAPConnector,
    SeniorConnector,
    get_erp_connector,
    EmployeeData,
    IncomeEventData
)

__all__ = [
    'ERPConnector',
    'FileERPConnector',
    'TotvsConnector',
    'SAPConnector',
    'SeniorConnector',
    'get_erp_connector',
    'EmployeeData',
    'IncomeEventData'
]
