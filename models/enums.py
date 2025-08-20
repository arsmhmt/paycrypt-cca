from enum import Enum


class WithdrawalMethodType(Enum):
    """Types of withdrawal methods supported by the platform."""
    BANK = 'bank'  # Traditional bank transfer
    CRYPTO = 'crypto'  # Cryptocurrency transfer
    PAYPAL = 'paypal'  # PayPal transfer
    WISE = 'wise'  # Wise (formerly TransferWise)
    PAYONEER = 'payoneer'  # Payoneer transfer
    SKRILL = 'skrill'  # Skrill e-wallet
    NETTELLER = 'neteller'  # Neteller e-wallet
    OTHER = 'other'  # Other withdrawal methods


class WithdrawalStatus(Enum):
    """Status values for withdrawal requests."""
    PENDING = 'pending'  # Initial state, waiting for processing
    APPROVED = 'approved'  # Approved by admin, waiting for processing
    REJECTED = 'rejected'  # Rejected by admin
    PROCESSING = 'processing'  # Currently being processed
    COMPLETED = 'completed'  # Successfully completed
    FAILED = 'failed'  # Processing failed
    CANCELLED = 'cancelled'  # Cancelled by user or system


class WithdrawalType(Enum):
    """Types of withdrawals in the system."""
    USER_REQUEST = 'user_request'  # B2C - Users withdrawing from client platforms
    CLIENT_BALANCE = 'client_balance'  # B2B - Clients withdrawing their net balances


class InvoiceStatus(Enum):
    """Status values for invoices."""
    DRAFT = 'draft'  # Invoice is being created/edited
    PENDING = 'pending'  # Awaiting payment
    PAID = 'paid'  # Payment received
    OVERDUE = 'overdue'  # Payment is late
    CANCELLED = 'cancelled'  # Invoice was cancelled
    REFUNDED = 'refunded'  # Payment was refunded
    PARTIALLY_PAID = 'partially_paid'  # Partial payment received
    UNPAID = 'unpaid'  # Payment is due but not yet received

class PaymentStatus(Enum):
    PENDING = 'pending'
    APPROVED = 'approved'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class ClientEntityType(Enum):
    """Entity type for client business structure (deprecated - use ClientType from client_package)"""
    INDIVIDUAL = 'individual'
    COMPANY = 'company'

class CommissionSnapshottingType(Enum):
    MANUAL = 'manual'
    AUTOMATIC = 'automatic'
    SCHEDULED = 'scheduled'


class AuditActionType(Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    LOGIN = 'login'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    FAILED_LOGIN = 'failed_login'
    ACCESS_DENIED = 'access_denied'
    FILE_UPLOAD = 'file_upload'
    FILE_DOWNLOAD = 'file_download'
    FILE_DELETE = 'file_delete'
    config_CHANGE = 'config_change'
    SYSTEM_ALERT = 'system_alert'
    SECURITY_ALERT = 'security_alert'
    COMMISSION_CHANGE = 'commission_change'
    RATE_CHANGE = 'rate_change'
    STATUS_CHANGE = 'status_change'
    DOCUMENT_APPROVAL = 'document_approval'
    DOCUMENT_REJECTION = 'document_rejection'
    DOCUMENT_REQUEST = 'document_request'
    DOCUMENT_SUBMISSION = 'document_submission'
    DOCUMENT_EXPIRATION = 'document_expiration'
    DOCUMENT_RENEWAL = 'document_renewal'
    DOCUMENT_REVIEW = 'document_review'
    DOCUMENT_UPDATE = 'document_update'
    DOCUMENT_ARCHIVE = 'document_archive'
    DOCUMENT_RESTORE = 'document_restore'
    DOCUMENT_DELETE = 'document_delete'
    DOCUMENT_DUPLICATE = 'document_duplicate'
    DOCUMENT_MERGE = 'document_merge'

class SettingType(Enum):
    SYSTEM = 'system'
    PLATFORM = 'platform'
    CLIENT = 'client'
    ADMIN = 'admin'

class SettingKey(Enum):
    # System settings
    SYSTEM_MAINTENANCE_MODE = 'system.maintenance_mode'
    SYSTEM_NOTIFICATION_EMAIL = 'system.notification_email'
    SYSTEM_LOG_RETENTION_DAYS = 'system.log_retention_days'
    
    # Platform settings
    PLATFORM_NAME = 'platform.name'
    PLATFORM_DESCRIPTION = 'platform.description'
    PLATFORM_CONTACT_EMAIL = 'platform.contact_email'
    PLATFORM_SUPPORT_EMAIL = 'platform.support_email'
    
    # Client settings
    CLIENT_DEFAULT_COMMISSION = 'client.default_commission'
    CLIENT_MIN_BALANCE = 'client.min_balance'
    CLIENT_MAX_BALANCE = 'client.max_balance'
    
    # Admin settings
    ADMIN_DEFAULT_PASSWORD_EXPIRY = 'admin.default_password_expiry'
    ADMIN_MIN_PASSWORD_LENGTH = 'admin.min_password_length'
    ADMIN_MAX_LOGIN_ATTEMPTS = 'admin.max_login_attempts'
    DOCUMENT_SPLIT = 'document_split'
    DOCUMENT_SIGN = 'document_sign'
    DOCUMENT_VERIFY = 'document_verify'
    DOCUMENT_ENCRYPT = 'document_encrypt'
    DOCUMENT_DECRYPT = 'document_decrypt'
    DOCUMENT_WATERMARK = 'document_watermark'
    DOCUMENT_THUMBNAIL = 'document_thumbnail'
    DOCUMENT_PREVIEW = 'document_preview'
    DOCUMENT_EXPORT = 'document_export'
    DOCUMENT_IMPORT = 'document_import'
    DOCUMENT_SYNC = 'document_sync'
    DOCUMENT_BACKUP = 'document_backup'
    DOCUMENT_MIGRATE = 'document_migrate'
    DOCUMENT_VALIDATE = 'document_validate'
    DOCUMENT_OPTIMIZE = 'document_optimize'
    DOCUMENT_COMPRESS = 'document_compress'
    DOCUMENT_DECOMPRESS = 'document_decompress'
    DOCUMENT_ENHANCE = 'document_enhance'
    DOCUMENT_REPAIR = 'document_repair'
    DOCUMENT_GENERATE = 'document_generate'
    DOCUMENT_ANALYZE = 'document_analyze'
    DOCUMENT_CLASSIFY = 'document_classify'
    DOCUMENT_TAG = 'document_tag'
    DOCUMENT_INDEX = 'document_index'
    DOCUMENT_SEARCH = 'document_search'
    DOCUMENT_FILTER = 'document_filter'
    DOCUMENT_SORT = 'document_sort'
    DOCUMENT_GROUP = 'document_group'
    DOCUMENT_COMPARE = 'document_compare'
    DOCUMENT_DIFF = 'document_diff'
    DOCUMENT_VERSION = 'document_version'
    DOCUMENT_HISTORY = 'document_history'
    DOCUMENT_REVISION = 'document_revision'
    DOCUMENT_COMMENT = 'document_comment'
    DOCUMENT_ANNOTATE = 'document_annotate'
    DOCUMENT_HIGHLIGHT = 'document_highlight'
    DOCUMENT_REDACT = 'document_redact'
    DOCUMENT_MASK = 'document_mask'
    DOCUMENT_CROP = 'document_crop'
    DOCUMENT_RESIZE = 'document_resize'
    DOCUMENT_ROTATE = 'document_rotate'
    DOCUMENT_MIRROR = 'document_mirror'
    DOCUMENT_FLIP = 'document_flip'
    DOCUMENT_TRANSFORM = 'document_transform'
    DOCUMENT_DISTORT = 'document_distort'
    DOCUMENT_SKEW = 'document_skew'
    DOCUMENT_PERSPECTIVE = 'document_perspective'
