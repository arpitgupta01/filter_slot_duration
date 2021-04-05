# coding: utf-8
from sqlalchemy import Column, Computed, DateTime, Enum, ForeignKey, JSON, String, Text, Time, text
from sqlalchemy.dialects.mysql import INTEGER, TINYINT
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata
