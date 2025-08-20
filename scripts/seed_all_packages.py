"""
Seed all default flat-rate and commission-based packages for Paycrypt.
Run: python scripts/seed_all_packages.py
"""
from app import create_app
from app.extensions import db
from app.models.client_package import (
    create_default_flat_rate_packages,
    COMMISSION_BASED_PACKAGES,
    ClientPackage,
    ClientType,
    PackageStatus
)
from datetime import datetime

def seed_commission_package():
    cfg = COMMISSION_BASED_PACKAGES['commission_basic']
    existing = ClientPackage.query.filter_by(name=cfg['name'], client_type=ClientType.COMMISSION).first()
    if existing:
        existing.commission_rate = cfg['commission_rate'] / 100.0
        existing.setup_fee = cfg['setup_fee']
        existing.description = cfg['description']
        existing.status = PackageStatus.ACTIVE
        existing.updated_at = datetime.utcnow()
        action = f"Updated: {existing.name}"
    else:
        commission_pkg = ClientPackage(
            name=cfg['name'],
            description=cfg['description'],
            client_type=ClientType.COMMISSION,
            commission_rate=cfg['commission_rate'] / 100.0,
            setup_fee=cfg['setup_fee'],
            status=PackageStatus.ACTIVE,
            is_popular=False
        )
        db.session.add(commission_pkg)
        action = f"Created: {cfg['name']}"
    return action

def main():
    app = create_app()
    with app.app_context():
        print("Seeding flat-rate packages...")
        flat_result = create_default_flat_rate_packages()
        print(flat_result)
        print("Seeding commission package...")
        commission_action = seed_commission_package()
        try:
            db.session.commit()
            print(f"Commission: {commission_action}")
            print("Seeding complete.")
        except Exception as e:
            db.session.rollback()
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
