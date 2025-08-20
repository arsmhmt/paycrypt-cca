"""
Seed commission package and all features for every package.
Run with: python scripts/seed_packages_and_features.py
"""
from app import create_app
from app.extensions import db
from app.models.client_package import ClientPackage, ClientType, PackageStatus, PackageFeature
from app.models.feature import Feature
from app.models.client_package import COMMISSION_BASED_PACKAGES, REVISED_FLAT_RATE_PACKAGES
from datetime import datetime

def seed_commission_package():
    config = COMMISSION_BASED_PACKAGES["commission_basic"]
    existing = ClientPackage.query.filter_by(name=config["name"], client_type=ClientType.COMMISSION).first()
    if existing:
        existing.commission_rate = config["commission_rate"] / 100.0
        existing.setup_fee = config["setup_fee"]
        existing.description = config["description"]
        existing.updated_at = datetime.utcnow()
        msg = f"Updated: {existing.name}"
    else:
        package = ClientPackage(
            name=config["name"],
            description=config["description"],
            client_type=ClientType.COMMISSION,
            commission_rate=config["commission_rate"] / 100.0,
            setup_fee=config["setup_fee"],
            status=PackageStatus.ACTIVE,
            is_popular=False
        )
        db.session.add(package)
        msg = f"Created: {package.name}"
    db.session.commit()
    return msg

def seed_features_for_packages():
    features = Feature.query.all()
    packages = ClientPackage.query.all()
    count = 0
    for package in packages:
        # Get feature keys for this package
        if package.client_type == ClientType.COMMISSION:
            included_keys = []  # Commission package may have no features
        else:
            # Find config by name
            config = next((v for v in REVISED_FLAT_RATE_PACKAGES.values() if v["name"] == package.name), None)
            included_keys = config["features"] if config else []
        for feature in features:
            exists = PackageFeature.query.filter_by(package_id=package.id, feature_id=feature.id).first()
            if not exists:
                pf = PackageFeature(
                    package_id=package.id,
                    feature_id=feature.id,
                    is_included=feature.feature_key in included_keys
                )
                db.session.add(pf)
                count += 1
    db.session.commit()
    return count

def main():
    app = create_app()
    with app.app_context():
        print(seed_commission_package())
        added = seed_features_for_packages()
        print(f"Features seeded for all packages: {added}")

if __name__ == "__main__":
    main()
