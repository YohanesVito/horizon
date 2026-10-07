"""Tests must never inherit a live database from the developer's .env.local."""
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ['HORIZON_API_KEY'] = ''
os.environ['HORIZON_REQUIRE_API_KEY'] = '0'
