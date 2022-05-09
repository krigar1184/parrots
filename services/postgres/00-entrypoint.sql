CREATE EXTENSION "uuid-ossp";

CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  public_id UUID NOT NULL DEFAULT GEN_RANDOM_UUID() ,
  username TEXT NOT NULL,
  role VARCHAR(25) NOT NULL,
  pwd_hash VARCHAR(100) NOT NULL,
  created_at TIMESTAMP(6) DEFAULT NOW(),
  updated_at TIMESTAMP(6) DEFAULT NOW(),
  UNIQUE(public_id)
);

CREATE TABLE IF NOT EXISTS tasks (
  id SERIAL PRIMARY KEY,
  public_id UUID NOT NULL DEFAULT GEN_RANDOM_UUID() ,
  assigned_to INT REFERENCES users(id),
  name TEXT NOT NULL,
  description TEXT NOT NULL,
  created_at TIMESTAMP(6) DEFAULT NOW(),
  updated_at TIMESTAMP(6) DEFAULT NOW(),
  UNIQUE(public_id)
);
