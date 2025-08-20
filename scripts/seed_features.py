"""
Seed all required features for Paycrypt packages.
Run: python scripts/seed_features.py
"""
from app import create_app
from app.extensions import db
from app.models.feature import Feature
from datetime import datetime

def get_feature_definitions():
    # Key: feature_key, Value: dict with name/description
    return [
        {'feature_key': 'api_basic', 'name': 'API Basic', 'description': 'Basic API access for payments'},
        {'feature_key': 'api_advanced', 'name': 'API Advanced', 'description': 'Advanced API access with extra endpoints'},
        {'feature_key': 'api_webhooks', 'name': 'API Webhooks', 'description': 'Webhook support for payment events'},
        {'feature_key': 'dashboard_analytics', 'name': 'Dashboard Analytics', 'description': 'Analytics dashboard for transactions'},
        {'feature_key': 'dashboard_realtime', 'name': 'Dashboard Realtime', 'description': 'Realtime dashboard updates'},
        {'feature_key': 'wallet_basic', 'name': 'Wallet Basic', 'description': 'Basic wallet management'},
        {'feature_key': 'wallet_management', 'name': 'Wallet Management', 'description': 'Advanced wallet management'},
        {'feature_key': 'support_priority', 'name': 'Priority Support', 'description': 'Priority support for enterprise clients'},
        {'feature_key': 'support_dedicated', 'name': 'Dedicated Support', 'description': 'Dedicated support manager'},
    ]

def seed_features():
    features = get_feature_definitions()
    actions = []
    for feat in features:
        existing = Feature.query.filter_by(feature_key=feat['feature_key']).first()
        if existing:
            existing.name = feat['name']
            existing.description = feat['description']
            existing.updated_at = datetime.utcnow() if hasattr(existing, 'updated_at') else None
            actions.append(f"Updated: {feat['feature_key']}")
        else:
            f = Feature(
                feature_key=feat['feature_key'],
                name=feat['name'],
                description=feat['description'],
                created_at=datetime.utcnow()
            )
            db.session.add(f)
            actions.append(f"Created: {feat['feature_key']}")
    try:
        db.session.commit()
        print("Feature seeding complete.")
        for a in actions:
            print(a)
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")

def main():
    app = create_app()
    with app.app_context():
        seed_features()

if __name__ == "__main__":
    main()
