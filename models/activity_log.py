# models/activity_log.py
from datetime import datetime, timezone

class ActivityLog:
    @staticmethod
    def log_activity(user_id, action, item_type, item_name):
        from app import mongo
        mongo.db.activity_logs.insert_one({
            "user_id": user_id,
            "action": action,
            "item_type": item_type,
            "item_name": item_name,
            "timestamp": datetime.now(timezone.utc)
        })
