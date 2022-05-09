import sqlalchemy

from auth.db import metadata


ROLE_EMPLOYEE = 'employee'
ROLE_ADMIN = 'admin'
ROLE_ACCOUNTANT = 'accountant'


users = sqlalchemy.Table(
    'users',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('public_id', sqlalchemy.String, unique=True),
    sqlalchemy.Column('username', sqlalchemy.String),
    sqlalchemy.Column('role', sqlalchemy.String),
    sqlalchemy.Column('pwd_hash', sqlalchemy.String),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
)


tasks_table = sqlalchemy.Table(
    'tasks',
    metadata,
    sqlalchemy.Column('id', sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column('public_id', sqlalchemy.String, unique=True),
    sqlalchemy.Column('assigned_to', sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('name', sqlalchemy.String),
    sqlalchemy.Column('description', sqlalchemy.String),
    sqlalchemy.Column('created_at', sqlalchemy.DateTime),
    sqlalchemy.Column('updated_at', sqlalchemy.DateTime),
)
