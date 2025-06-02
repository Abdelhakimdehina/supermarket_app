"""Services for the application"""

from services.auth_service import AuthService
from services.product_service import ProductService
from services.customer_service import CustomerService
from services.sale_service import SaleService
from services.statistics_service import StatisticsService

__all__ = [
    'AuthService',
    'ProductService',
    'CustomerService',
    'SaleService',
    'StatisticsService'
] 