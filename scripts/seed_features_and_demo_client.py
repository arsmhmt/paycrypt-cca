"""
Seed all features for packages and create a demo client for Paycrypt.
Run: python scripts/seed_features_and_demo_client.py
"""
from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, PackageFeature
from app.models.feature import Feature
from app.models.client import Client
from app.models.client_package import ClientType
from datetime import datetime

def seed_features_for_packages():
    # Map features to package names (as in REVISED_FLAT_RATE_PACKAGES)
    package_features_map = {
        'Starter Flat Rate': ['api_basic', 'wallet_basic'],
        'Business Flat Rate': ['api_basic', 'api_webhooks', 'dashboard_analytics', 'wallet_management'],
        'Enterprise Flat Rate': [
            'api_basic', 'api_advanced', 'api_webhooks', 'dashboard_analytics', 'dashboard_realtime',
            'wallet_management', 'support_priority', 'support_dedicated'
        ],
        'Commission Basic': ['api_basic', 'wallet_basic']  # Example for commission package
    }
    actions = []
    for pkg_name, feature_keys in package_features_map.items():
        pkg = ClientPackage.query.filter_by(name=pkg_name).first()
        if not pkg:
            actions.append(f"Package not found: {pkg_name}")
            continue
        for key in feature_keys:
            feat = Feature.query.filter_by(feature_key=key).first()
            if not feat:
                actions.append(f"Feature not found: {key}")
                continue
            # Check if already linked
            pf = PackageFeature.query.filter_by(package_id=pkg.id, feature_id=feat.id).first()
            if pf:
                pf.is_included = True
                actions.append(f"Updated feature '{key}' for package '{pkg_name}'")
            else:
                pf = PackageFeature(package_id=pkg.id, feature_id=feat.id, is_included=True)
                db.session.add(pf)
                actions.append(f"Linked feature '{key}' to package '{pkg_name}'")
    return actions

def create_demo_client():
    # Create a demo client assigned to 'Enterprise Flat Rate'
    pkg = ClientPackage.query.filter_by(name='Enterprise Flat Rate').first()
    if not pkg:
        return "Enterprise Flat Rate package not found."
    # Check if demo client exists
    demo = Client.query.filter_by(email='demo@paycrypt.com').first()
    if demo:
        demo.package_id = pkg.id
        demo.client_type = ClientType.FLAT_RATE
        demo.updated_at = datetime.utcnow()
        action = "Updated demo client."
    else:
        demo = Client(
            name='Demo Enterprise Client',
            email='demo@paycrypt.com',
            package_id=pkg.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            is_active=True
        )
        db.session.add(demo)
        action = "Created demo client."
    return action

def main():
    app = create_app()
    with app.app_context():
        print("Seeding features for packages...")
        feature_actions = seed_features_for_packages()
        for a in feature_actions:
            print(a)
        print("Creating demo client...")
        demo_action = create_demo_client()
        try:
            db.session.commit()
            print(demo_action)
            print("Seeding complete.")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
