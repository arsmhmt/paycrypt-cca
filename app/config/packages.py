# app/config/packages.py

class FeatureAccessMixin:
    def has_feature(self, feature_name):
        # Check for flat_rate client type and enterprise package
        package = getattr(self, 'package', None)
        # Accept both direct attribute and relationship
        slug = getattr(package, 'slug', None) if package else None
        client_type = None
        if hasattr(self, 'get_client_type'):
            client_type = self.get_client_type()
        elif hasattr(self, 'client_type'):
            client_type = self.client_type
        
        # Grant all features for enterprise flat-rate clients
        # Handle both enum and string values, and check for 'enterprise' slug
        is_flat_rate = (
            client_type == 'flat_rate' or 
            (hasattr(client_type, 'value') and client_type.value == 'FLAT_RATE') or
            str(client_type) == 'ClientType.FLAT_RATE'
        )
        is_enterprise = slug in ['enterprise', 'enterprise_flat_rate']
        
        if is_flat_rate and is_enterprise:
            return True
            
        # Fallback: check if feature is in package features
        if package and hasattr(package, 'features'):
            return any(getattr(f, 'feature_key', None) == feature_name for f in package.features)
        return False  # Default: no access

def client_has_feature(client, feature_name):
    return client.has_feature(feature_name) if hasattr(client, "has_feature") else False

def sync_client_status_with_package(client):
    # Optional logic to sync plan/package status — placeholder
    pass
