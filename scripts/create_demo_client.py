from app import create_app, db
from app.models.client import Client
from app.models.client_package import ClientPackage
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Find or create enterprise package
    from app.models.client_package import ClientType
    demo_package = ClientPackage.query.filter(ClientPackage.client_type==ClientType.FLAT_RATE, ClientPackage.name.ilike('%enterprise%')).first()
    if not demo_package:
        demo_package = ClientPackage(name='Enterprise', client_type=ClientType.FLAT_RATE, monthly_price=999.99, status='active')
        db.session.add(demo_package)
        db.session.commit()
        print('Created Enterprise package.')
    else:
        print('Enterprise package already exists.')

    # Find or create demo client
    demo_client = Client.query.filter_by(username='demo').first()
    if not demo_client:
        demo_client = Client(
            username='demo',
            password_hash=generate_password_hash('Demo12345'),
            package=demo_package
        )
        db.session.add(demo_client)
        db.session.commit()
        print('Demo client created with enterprise package.')
    else:
        print('Demo client already exists.')
