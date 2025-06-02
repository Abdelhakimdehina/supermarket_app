from typing import Dict, Any, List, Optional

from database.models.customer import Customer

class CustomerService:
    """Service for managing customers"""
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Optional[Customer]:
        """Create a new customer"""
        try:
            # Check if customer with same phone exists
            if customer_data.get('phone'):
                existing = Customer.get_by_phone(customer_data['phone'])
                if existing:
                    return None
            
            # Create and save customer
            customer = Customer.from_dict(customer_data)
            if customer.save():
                return customer
            return None
        except Exception as e:
            print(f"Error creating customer: {e}")
            return None
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Optional[Customer]:
        """Update an existing customer"""
        try:
            # Get existing customer
            customer = Customer.get_by_id(customer_id)
            if not customer:
                return None
            
            # Check if phone is being changed and new phone exists
            if customer_data.get('phone') and customer_data['phone'] != customer.phone:
                existing = Customer.get_by_phone(customer_data['phone'])
                if existing:
                    return None
            
            # Update customer fields
            customer.name = customer_data.get('name', customer.name)
            customer.phone = customer_data.get('phone', customer.phone)
            customer.email = customer_data.get('email', customer.email)
            customer.address = customer_data.get('address', customer.address)
            
            if customer.save():
                return customer
            return None
        except Exception as e:
            print(f"Error updating customer: {e}")
            return None
    
    def delete_customer(self, customer_id: int) -> bool:
        """Delete a customer"""
        try:
            customer = Customer.get_by_id(customer_id)
            if customer:
                return customer.delete()
            return False
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False
    
    def get_customer(self, customer_id: int) -> Optional[Customer]:
        """Get a customer by ID"""
        try:
            return Customer.get_by_id(customer_id)
        except Exception as e:
            print(f"Error getting customer: {e}")
            return None
    
    def get_customers(self) -> List[Customer]:
        """Get all customers"""
        try:
            return Customer.get_all()
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []
    
    def search_customers(self, search_term: str) -> List[Customer]:
        """Search for customers"""
        try:
            return Customer.search(search_term)
        except Exception as e:
            print(f"Error searching customers: {e}")
            return []
    
    def update_loyalty_points(self, customer_id: int, points: int) -> bool:
        """Update customer loyalty points"""
        try:
            customer = Customer.get_by_id(customer_id)
            if customer:
                return customer.update_loyalty_points(points)
            return False
        except Exception as e:
            print(f"Error updating loyalty points: {e}")
            return False 