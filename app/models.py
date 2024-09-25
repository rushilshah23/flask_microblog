from datetime import datetime, timezone
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, app, login

class User(UserMixin, db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash:so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts:so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me:so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen:so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))


    def __repr__(self):
        return '<User {} - with last seen -{} '.format(self.username, self.last_seen)
    
    def set_password(self,password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest =  md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

class Post(db.Model):
    id:so.Mapped[int] = so.mapped_column(primary_key=True)
    body:so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp:so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id:so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    author:so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}'.format(self.body)


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


def truncate_table(model):
    """Truncate or delete all records from a table based on the database dialect."""
    table_name = model.__tablename__
    dialect = db.engine.dialect.name

    if dialect == 'sqlite':
        # For SQLite, use DELETE and try resetting the sequence if it exists
        db.session.execute(sa.text(f'DELETE FROM {table_name}'))
        # Try resetting the auto-increment, but only if sqlite_sequence exists
        try:
            db.session.execute(sa.text(f'DELETE FROM sqlite_sequence WHERE name="{table_name}"'))
        except Exception as e:
            # Handle cases where sqlite_sequence doesn't exist, i.e., no AUTOINCREMENT
            print(f"Skipping auto-increment reset for {table_name}: {e}")
    else:
        # For other databases, use TRUNCATE
        db.session.execute(sa.text(f'TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE'))
    
    db.session.commit()



@app.shell_context_processor
def make_shell_context():
    return {'sa':sa,'so':so,'db':db, 'User':User, 'Post':Post, 'truncate_table':truncate_table}


