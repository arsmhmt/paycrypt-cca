
import os
from dotenv import load_dotenv
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.role import Role
import click

load_dotenv()
app = create_app()

@app.cli.command('create-superadmin')
def create_superadmin():
    """Create the superadmin role and user from environment variables."""
    with app.app_context():
        try:
            # Create superadmin role if not exists
            role = Role.query.filter_by(name='superadmin').first()
            if not role:
                role = Role(name='superadmin', description='Super Administrator', permissions={'all': True})
                db.session.add(role)
                db.session.commit()
                click.echo('Superadmin role created.')
            else:
                click.echo('Superadmin role already exists.')

            # Create superadmin user if not exists
            username = os.getenv('ADMIN_USERNAME')
            email = os.getenv('ADMIN_EMAIL')
            password = os.getenv('ADMIN_PASSWORD')
            click.echo(f'Using credentials: username={username}, email={email}, password={password}')
            user = User.query.filter_by(username=username).first()
            if not user:
                user = User(username=username, email=email)
                user.set_password(password)
                user.role = role
                db.session.add(user)
                db.session.commit()
                click.echo('Superadmin user created.')
            else:
                click.echo('Superadmin user already exists.')
            click.echo(f'User: {user}')
            click.echo(f'Password hash: {user.password_hash}')
            click.echo(f'Role: {user.role.name if user and user.role else None}')
        except Exception as e:
            click.echo(f'Error during superadmin creation: {e}')
