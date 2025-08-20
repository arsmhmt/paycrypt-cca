from decimal import Decimal, ROUND_DOWN
from flask import current_app
from sqlalchemy import func
from functools import lru_cache
from datetime import datetime, timedelta

# Import models
from app.models import (
    Client,
    Payment,
    PaymentStatus,
    WithdrawalRequest,
    WithdrawalStatus,
    CommissionSnapshot
)
from app.extensions import db


class FinanceCalculator:
    """Utility class for calculating financial metrics"""
    
    def __init__(self):
        """Initialize FinanceCalculator with required models and status enums"""
        # These are already available in the module scope, no need to store as instance attributes
        pass

    @staticmethod
    @lru_cache(maxsize=128)
    def calculate_client_balance(client_id):
        """
        Calculate a client's available balance after commissions.
        
        Args:
            client_id (int): The client's ID
            
        Returns:
            Decimal: The client's available balance
        """
        client = Client.query.get(client_id)
        if not client:
            return Decimal('0.0')

        # Get total deposits (completed payments)
        deposits_result = db.session.query(func.sum(Payment.amount))\
            .filter_by(client_id=client_id, status=PaymentStatus.APPROVED)\
            .scalar() 
        deposits = Decimal(str(deposits_result)) if deposits_result is not None else Decimal('0.0')

        # Get total withdrawals (approved requests)
        withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
            .filter_by(client_id=client_id, status=WithdrawalStatus.APPROVED)\
            .scalar()
        withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result is not None else Decimal('0.0')

        # Ensure commission rates are Decimal
        deposit_rate = Decimal(str(client.deposit_commission_rate)) if client.deposit_commission_rate is not None else Decimal('0.035')
        withdrawal_rate = Decimal(str(client.withdrawal_commission_rate)) if client.withdrawal_commission_rate is not None else Decimal('0.015')
        deposit_comm = deposits * deposit_rate
        withdrawal_comm = withdrawals * withdrawal_rate

        balance = deposits - deposit_comm - withdrawals - withdrawal_comm
        return balance.quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

    @staticmethod
    def calculate_commission(client_id):
        """
        Returns deposit_commission, withdrawal_commission, total_commission
        
        Args:
            client_id (int): The client's ID
            
        Returns:
            tuple: (deposit_commission, withdrawal_commission, total_commission)
        """
        client = Client.query.get(client_id)
        if not client:
            return (Decimal('0.0'), Decimal('0.0'), Decimal('0.0'))

        deposits_result = db.session.query(func.sum(Payment.amount))\
            .filter_by(client_id=client_id, status=PaymentStatus.APPROVED)\
            .scalar()
        deposits = Decimal(str(deposits_result)) if deposits_result is not None else Decimal('0.0')

        withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
            .filter_by(client_id=client_id, status=WithdrawalStatus.APPROVED)\
            .scalar()
        withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result is not None else Decimal('0.0')

        # Ensure commission rates are Decimal
        deposit_rate = Decimal(str(client.deposit_commission_rate)) if client.deposit_commission_rate is not None else Decimal('0.035')
        withdrawal_rate = Decimal(str(client.withdrawal_commission_rate)) if client.withdrawal_commission_rate is not None else Decimal('0.015')
        deposit_comm = deposits * deposit_rate
        withdrawal_comm = withdrawals * withdrawal_rate
        total_comm = deposit_comm + withdrawal_comm

        return (
            deposit_comm.quantize(Decimal('0.00000001'), ROUND_DOWN),
            withdrawal_comm.quantize(Decimal('0.00000001'), ROUND_DOWN),
            total_comm.quantize(Decimal('0.00000001'), ROUND_DOWN)
        )

    
    @staticmethod
    def validate_withdrawal_amount(client_id, amount):
        """
        Validate if a withdrawal amount is allowed based on client's balance
        
        Args:
            client_id (int): The client's ID
            amount (Decimal): The requested withdrawal amount
            
        Returns:
            bool: True if withdrawal is allowed, False otherwise
        """
        available_balance = FinanceCalculator.calculate_client_balance(client_id)
        return amount <= available_balance

    @staticmethod
    def get_gross_deposits(client_id):
        """
        Returns the total gross deposits for a client (before commission deduction)
        """
        from decimal import Decimal
        client = Client.query.get(client_id)
        if not client:
            return Decimal('0.0')
        deposits_result = db.session.query(func.sum(Payment.amount))\
            .filter_by(client_id=client_id, status=PaymentStatus.APPROVED)\
            .scalar()
        deposits = Decimal(str(deposits_result)) if deposits_result is not None else Decimal('0.0')
        return deposits

    @staticmethod
    def get_gross_withdrawals(client_id):
        """
        Returns the total gross withdrawals for a client (before commission deduction)
        """
        from decimal import Decimal
        client = Client.query.get(client_id)
        if not client:
            return Decimal('0.0')
        withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
            .filter_by(client_id=client_id, status=WithdrawalStatus.APPROVED)\
            .scalar()
        withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result is not None else Decimal('0.0')
        return withdrawals

    @staticmethod
    def get_commission_stats():
        """
        Get commission statistics for the last 30 days
        
        Returns:
            dict: Statistics including total_30d and avg_rate
        """
        try:
            from flask import current_app
            
            # Calculate total commission for last 30 days
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Get all active clients
            clients = Client.query.filter_by(is_active=True).all()
            
            total_commission_30d = Decimal('0.0')
            total_rate_sum = Decimal('0.0')
            client_count = 0
            
            for client in clients:
                # Get deposits and withdrawals for this client in last 30 days
                deposits_result = db.session.query(func.sum(Payment.amount))\
                    .filter(Payment.client_id == client.id,
                           Payment.status == PaymentStatus.APPROVED,
                           Payment.created_at >= thirty_days_ago)\
                    .scalar()
                
                withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
                    .filter(WithdrawalRequest.client_id == client.id,
                           WithdrawalRequest.status == WithdrawalStatus.APPROVED,
                           WithdrawalRequest.created_at >= thirty_days_ago)\
                    .scalar()
                
                deposits = Decimal(str(deposits_result)) if deposits_result else Decimal('0.0')
                withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result else Decimal('0.0')
                
                # Calculate commission for this client
                deposit_rate = Decimal(str(client.deposit_commission_rate)) if client.deposit_commission_rate else Decimal('0.035')
                withdrawal_rate = Decimal(str(client.withdrawal_commission_rate)) if client.withdrawal_commission_rate else Decimal('0.015')
                
                client_commission = (deposits * deposit_rate) + (withdrawals * withdrawal_rate)
                total_commission_30d += client_commission
                
                # Add to average rate calculation
                if deposits > 0 or withdrawals > 0:
                    avg_client_rate = ((deposits * deposit_rate) + (withdrawals * withdrawal_rate)) / (deposits + withdrawals) * 100 if (deposits + withdrawals) > 0 else Decimal('0.0')
                    total_rate_sum += avg_client_rate
                    client_count += 1
            
            avg_rate = total_rate_sum / client_count if client_count > 0 else Decimal('0.0')
            
            return {
                'total_30d': float(total_commission_30d),
                'avg_rate': float(avg_rate)
            }
            
        except Exception as e:
            # Handle the case where we're outside of application context
            try:
                from flask import current_app
                current_app.logger.error(f"Error calculating commission stats: {str(e)}")
            except RuntimeError:
                # We're outside app context, just print to console
                print(f"Error calculating commission stats: {str(e)}")
            
            return {
                'total_30d': 0,
                'avg_rate': 0
            }

    @staticmethod
    def get_total_volume_30d():
        """
        Get total payment volume for the last 30 days
        
        Returns:
            float: Total volume
        """
        try:
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            # Get total deposits
            deposits_result = db.session.query(func.sum(Payment.amount))\
                .filter(Payment.status == PaymentStatus.APPROVED,
                       Payment.created_at >= thirty_days_ago)\
                .scalar()
            
            # Get total withdrawals  
            withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
                .filter(WithdrawalRequest.status == WithdrawalStatus.APPROVED,
                       WithdrawalRequest.created_at >= thirty_days_ago)\
                .scalar()
            
            deposits = Decimal(str(deposits_result)) if deposits_result else Decimal('0.0')
            withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result else Decimal('0.0')
            
            return float(deposits + withdrawals)
            
        except Exception as e:
            # Handle the case where we're outside of application context
            try:
                from flask import current_app
                current_app.logger.error(f"Error calculating total volume: {str(e)}")
            except RuntimeError:
                # We're outside app context, just print to console
                print(f"Error calculating total volume: {str(e)}")
            
            return 0.0

# Initialize the calculator as a module-level instance
calculator = FinanceCalculator()
