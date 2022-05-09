import databases
import sqlalchemy


from auth.settings import DB_DSN


database = databases.Database(DB_DSN)
metadata = sqlalchemy.MetaData()
engine = sqlalchemy.create_engine(DB_DSN, connect_args={'check_same_thread': False})
