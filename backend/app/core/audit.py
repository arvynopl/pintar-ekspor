# backend/app/core/audit.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import json
from datetime import datetime
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.declarative import declarative_base

logger = logging.getLogger(__name__)

# Create a separate base for audit models
AuditBase = declarative_base()

class AuditLog(AuditBase):
    """
    Audit log model for tracking database changes
    """
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    user_id = Column(Integer, nullable=True)
    action = Column(String, nullable=False)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)

class AuditLogger:
    """
    Handles audit logging for database operations
    """
    def __init__(self, session: Session):
        self.session = session

    def log_change(
        self,
        action: str,
        table_name: str,
        record_id: Optional[int] = None,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None
    ):
        """Log a database change"""
        try:
            audit_entry = AuditLog(
                action=action,
                table_name=table_name,
                record_id=record_id,
                old_values=old_values,
                new_values=new_values,
                user_id=user_id,
                ip_address=ip_address
            )
            self.session.add(audit_entry)
            self.session.commit()
        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            self.session.rollback()

def setup_audit_listeners():
    """Set up SQLAlchemy event listeners for automatic audit logging"""
    @event.listens_for(Session, 'after_flush')
    def after_flush(session, flush_context):
        """Log changes after flush"""
        try:
            for instance in session.new:
                if not isinstance(instance, AuditLog):
                    _log_insert(session, instance)

            for instance in session.dirty:
                if not isinstance(instance, AuditLog):
                    _log_update(session, instance)

            for instance in session.deleted:
                if not isinstance(instance, AuditLog):
                    _log_delete(session, instance)
        except Exception as e:
            logger.error(f"Error in audit logging: {str(e)}")

def _log_insert(session: Session, instance: Any):
    """Log INSERT operations"""
    try:
        new_values = {
            c.key: getattr(instance, c.key)
            for c in instance.__table__.columns
            if not c.primary_key
        }
        
        AuditLogger(session).log_change(
            action="INSERT",
            table_name=instance.__tablename__,
            record_id=getattr(instance, 'id', None),
            new_values=new_values
        )
    except Exception as e:
        logger.error(f"Error logging INSERT: {str(e)}")

def _log_update(session: Session, instance: Any):
    """Log UPDATE operations"""
    try:
        if not instance._sa_instance_state.modified:
            return

        old_values = {}
        new_values = {}

        for attr in instance._sa_instance_state.attrs:
            if attr.key not in ('created_at', 'updated_at') and attr.history.has_changes():
                old_values[attr.key] = attr.history.deleted[0] if attr.history.deleted else None
                new_values[attr.key] = attr.history.added[0] if attr.history.added else None

        AuditLogger(session).log_change(
            action="UPDATE",
            table_name=instance.__tablename__,
            record_id=getattr(instance, 'id', None),
            old_values=old_values,
            new_values=new_values
        )
    except Exception as e:
        logger.error(f"Error logging UPDATE: {str(e)}")

def _log_delete(session: Session, instance: Any):
    """Log DELETE operations"""
    try:
        old_values = {
            c.key: getattr(instance, c.key)
            for c in instance.__table__.columns
            if not c.primary_key
        }
        
        AuditLogger(session).log_change(
            action="DELETE",
            table_name=instance.__tablename__,
            record_id=getattr(instance, 'id', None),
            old_values=old_values
        )
    except Exception as e:
        logger.error(f"Error logging DELETE: {str(e)}")