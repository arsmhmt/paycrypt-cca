from sqlalchemy import func
from decimal import Decimal
from app.models import db, Payment, WithdrawalRequest, PaymentStatus, Client, Client

class FinanceCalculator:
    @staticmethod
    def calculate_client_commission(client, date_from=None, date_to=None):
        """
        Calculate commission for a client based on deposits and withdrawals.
        
        Args:
            client: Client model instance
            date_from: Optional start date for filtering
            date_to: Optional end date for filtering
            
        Returns:
            dict: Commission details including totals and fees
        """
        # Base query for deposits
        deposit_query = db.session.query(func.sum(Payment.amount))\
            .filter(Payment.client_id == client.id, 
                    Payment.status == PaymentStatus.COMPLETED)
        
        # Base query for withdrawals
        withdrawal_query = db.session.query(func.sum(WithdrawalRequest.amount))\
            .filter(WithdrawalRequest.client_id == client.id, 
                    WithdrawalRequest.status == PaymentStatus.COMPLETED)  # Using same status enum
        
        # Apply date filters if provided
        if date_from:
            deposit_query = deposit_query.filter(Payment.created_at >= date_from)
            withdrawal_query = withdrawal_query.filter(WithdrawalRequest.created_at >= date_from)
        if date_to:
            deposit_query = deposit_query.filter(Payment.created_at <= date_to)
            withdrawal_query = withdrawal_query.filter(WithdrawalRequest.created_at <= date_to)
        
        # Get totals
        deposits_result = deposit_query.scalar()
        withdrawals_result = withdrawal_query.scalar()
        
        # Ensure proper Decimal conversion
        deposits = Decimal(str(deposits_result)) if deposits_result is not None else Decimal('0')
        withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result is not None else Decimal('0')
        
        # Get commission rates (stored as decimal in the client model)
        dep_rate = client.deposit_commission if hasattr(client, 'deposit_commission') else Decimal('0.035')  # 3.5% default
        wd_rate = client.withdrawal_commission if hasattr(client, 'withdrawal_commission') else Decimal('0.015')  # 1.5% default
        
        # Calculate commissions
        dep_comm = deposits * dep_rate
        wd_comm = withdrawals * wd_rate
        
        total = dep_comm + wd_comm
        
        return {
            'deposit_total': deposits,
            'withdrawal_total': withdrawals,
            'deposit_rate': dep_rate,
            'withdrawal_rate': wd_rate,
            'deposit_fee': dep_comm,
            'withdrawal_fee': wd_comm,
            'total_commission': total
        }
    
    @staticmethod
    def calculate_client_balance(client_id):
        """
        Calculate client's available balance after commissions.
        
        Args:
            client_id (int): The client's ID
            
        Returns:
            Decimal: The client's available balance
        """
        try:
            client = db.session.query(Client).get(client_id)
            if not client:
                return Decimal('0.0')

            # Get total deposits (completed payments)
            deposits_result = db.session.query(func.sum(Payment.amount))\
                .filter_by(client_id=client_id, status=PaymentStatus.COMPLETED)\
                .scalar() 
            deposits = Decimal(str(deposits_result)) if deposits_result is not None else Decimal('0.0')

            # Get total withdrawals (approved requests)
            withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
                .filter_by(client_id=client_id, status=PaymentStatus.COMPLETED)\
                .scalar()
            withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result is not None else Decimal('0.0')

            # Calculate commissions
            deposit_rate = client.deposit_commission_rate if hasattr(client, 'deposit_commission_rate') and client.deposit_commission_rate else Decimal('0.035')
            withdrawal_rate = client.withdrawal_commission_rate if hasattr(client, 'withdrawal_commission_rate') and client.withdrawal_commission_rate else Decimal('0.015')
            
            deposit_comm = deposits * Decimal(str(deposit_rate))
            withdrawal_comm = withdrawals * Decimal(str(withdrawal_rate))

            # Balance = deposits - withdrawal_requests - commissions
            balance = deposits - withdrawals - deposit_comm - withdrawal_comm
            return max(balance, Decimal('0.0'))  # Ensure non-negative balance
            
        except Exception as e:
            print(f"Error calculating client balance: {e}")
            return Decimal('0.0')

    @staticmethod
    def calculate_commission(client_id):
        """
        Calculate commission totals for a client.
        
        Args:
            client_id (int): The client's ID
            
        Returns:
            tuple: (deposit_commission, withdrawal_commission, total_commission)
        """
        try:
            client = db.session.query(Client).get(client_id)
            if not client:
                return (Decimal('0.0'), Decimal('0.0'), Decimal('0.0'))

            # Get totals
            deposits_result = db.session.query(func.sum(Payment.amount))\
                .filter_by(client_id=client_id, status=PaymentStatus.COMPLETED)\
                .scalar()
            deposits = Decimal(str(deposits_result)) if deposits_result is not None else Decimal('0.0')

            withdrawals_result = db.session.query(func.sum(WithdrawalRequest.amount))\
                .filter_by(client_id=client_id, status=PaymentStatus.COMPLETED)\
                .scalar()
            withdrawals = Decimal(str(withdrawals_result)) if withdrawals_result is not None else Decimal('0.0')

            # Get commission rates
            deposit_rate = client.deposit_commission_rate if hasattr(client, 'deposit_commission_rate') and client.deposit_commission_rate else Decimal('0.035')
            withdrawal_rate = client.withdrawal_commission_rate if hasattr(client, 'withdrawal_commission_rate') and client.withdrawal_commission_rate else Decimal('0.015')
            
            # Calculate commissions
            deposit_comm = deposits * Decimal(str(deposit_rate))
            withdrawal_comm = withdrawals * Decimal(str(withdrawal_rate))
            total_comm = deposit_comm + withdrawal_comm

            return (deposit_comm, withdrawal_comm, total_comm)
            
        except Exception as e:
            print(f"Error calculating commission: {e}")
            return (Decimal('0.0'), Decimal('0.0'), Decimal('0.0'))

    @staticmethod
    def validate_withdrawal_amount(client_id, amount):
        """
        Validate if a withdrawal amount is valid for the client.
        
        Args:
            client_id (int): The client's ID
            amount (Decimal): The withdrawal amount
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if amount <= 0:
                return False
                
            available_balance = FinanceCalculator.calculate_client_balance(client_id)
            return amount <= available_balance
            
        except Exception as e:
            print(f"Error validating withdrawal amount: {e}")
            return False
