import sqlite3
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from .schema import get_connection

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for loan approval system"""

    def __init__(self, database_path: str):
        self.database_path = database_path

    # Application Operations
    def create_application(self, application_data: Dict[str, Any]) -> Optional[str]:
        """Create a new loan application record"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            app_id = f"APP-{uuid4().hex[:12].upper()}"

            cursor.execute(
                """
                INSERT INTO applications (
                    id, applicant_id, age, income, employment_type,
                    credit_score, loan_amount, tenure_months,
                    existing_liabilities, location, application_timestamp, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    app_id,
                    application_data.get("applicant_id"),
                    application_data.get("age"),
                    application_data.get("income"),
                    application_data.get("employment_type"),
                    application_data.get("credit_score"),
                    application_data.get("loan_amount"),
                    application_data.get("tenure_months"),
                    application_data.get("existing_liabilities"),
                    application_data.get("location"),
                    application_data.get("application_timestamp", datetime.now().isoformat()),
                    "PENDING",
                ),
            )

            conn.commit()
            logger.info(f"Application created: {app_id}")
            return app_id

        except sqlite3.Error as e:
            logger.error(f"Error creating application: {e}")
            return None
        finally:
            conn.close()

    def get_application(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an application by ID"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM applications WHERE id = ?", (app_id,))
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            logger.error(f"Error retrieving application: {e}")
            return None
        finally:
            conn.close()

    def update_application_status(self, app_id: str, status: str) -> bool:
        """Update application status"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE applications SET status = ? WHERE id = ?", (status, app_id)
            )
            conn.commit()
            logger.info(f"Application {app_id} status updated to {status}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Error updating application status: {e}")
            return False
        finally:
            conn.close()

    def list_applications(
        self, status: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List applications with optional filtering"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            if status:
                cursor.execute(
                    "SELECT * FROM applications WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                    (status, limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM applications ORDER BY created_at DESC LIMIT ?",
                    (limit,),
                )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error listing applications: {e}")
            return []
        finally:
            conn.close()

    # Decision Operations
    def create_decision(self, decision_data: Dict[str, Any]) -> Optional[str]:
        """Create a new decision record"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            decision_id = f"DEC-{uuid4().hex[:12].upper()}"

            cursor.execute(
                """
                INSERT INTO decisions (
                    id, application_id, classification, risk_score,
                    confidence_level, reasoning, key_decision_factors
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    decision_id,
                    decision_data.get("application_id"),
                    decision_data.get("classification"),
                    decision_data.get("risk_score"),
                    decision_data.get("confidence_level"),
                    decision_data.get("reasoning"),
                    decision_data.get("key_decision_factors"),
                ),
            )

            conn.commit()
            logger.info(f"Decision created: {decision_id}")
            return decision_id

        except sqlite3.Error as e:
            logger.error(f"Error creating decision: {e}")
            return None
        finally:
            conn.close()

    def get_decision(self, app_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve decision for an application"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM decisions WHERE application_id = ?", (app_id,)
            )
            row = cursor.fetchone()

            if row:
                return dict(row)
            return None

        except sqlite3.Error as e:
            logger.error(f"Error retrieving decision: {e}")
            return None
        finally:
            conn.close()

    # Audit Log Operations
    def create_audit_log(self, log_data: Dict[str, Any]) -> Optional[str]:
        """Create an audit log entry"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            log_id = f"LOG-{uuid4().hex[:12].upper()}"

            cursor.execute(
                """
                INSERT INTO audit_logs (
                    id, case_id, application_id, agent_name, action, details
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    log_id,
                    log_data.get("case_id"),
                    log_data.get("application_id"),
                    log_data.get("agent_name"),
                    log_data.get("action"),
                    log_data.get("details"),
                ),
            )

            conn.commit()
            logger.info(f"Audit log created: {log_id}")
            return log_id

        except sqlite3.Error as e:
            logger.error(f"Error creating audit log: {e}")
            return None
        finally:
            conn.close()

    def get_audit_logs(
        self, app_id: str, limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs for an application"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT * FROM audit_logs WHERE application_id = ? ORDER BY timestamp DESC LIMIT ?",
                (app_id, limit),
            )

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

        except sqlite3.Error as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []
        finally:
            conn.close()

    # Statistics Operations
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            conn = get_connection(self.database_path)
            cursor = conn.cursor()

            stats = {}

            # Application stats
            cursor.execute("SELECT COUNT(*) FROM applications")
            stats["total_applications"] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT status, COUNT(*) FROM applications GROUP BY status"
            )
            stats["applications_by_status"] = dict(cursor.fetchall())

            # Decision stats
            cursor.execute("SELECT COUNT(*) FROM decisions")
            stats["total_decisions"] = cursor.fetchone()[0]

            cursor.execute(
                "SELECT classification, COUNT(*) FROM decisions GROUP BY classification"
            )
            stats["decisions_by_classification"] = dict(cursor.fetchall())

            # Audit log stats
            cursor.execute("SELECT COUNT(*) FROM audit_logs")
            stats["total_audit_logs"] = cursor.fetchone()[0]

            return stats

        except sqlite3.Error as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
        finally:
            conn.close()
