
# models/expense.py
from bson import ObjectId
from datetime import datetime, timezone

class Expense:
    @staticmethod
    def add_expense(user_id, amount, category, name):
        from app import mongo
        mongo.db.expenses.insert_one({
            "user_id": user_id,
            "amount": amount,
            "category": category,
            "name": name,  # Save the expense name
            "created_at": datetime.now(timezone.utc)   # Save the creation timestamp
        })


    @staticmethod
    def get_all_expenses(user_id):
        from app import mongo
        expenses = mongo.db.expenses.find({"user_id": str(user_id)})
        
        # Convert ObjectId fields to strings for JSON serialization
        expenses_list = []
        for expense in expenses:
            expense["_id"] = str(expense["_id"])
            expenses_list.append(expense)
        
        return expenses_list


    @staticmethod
    def update_expense(expense_id, new_name, new_amount, new_category):
        from app import mongo
        mongo.db.expenses.update_one(
            {"_id": ObjectId(expense_id)},
            {"$set": {"name": new_name, "amount": new_amount, "category": new_category}}
        )

    @staticmethod
    def delete_expense(expense_id):
        from app import mongo
        mongo.db.expenses.delete_one({"_id": ObjectId(expense_id)})



    @staticmethod
    def get_expense_by_id(expense_id):
        from app import mongo
        # Retrieve the income document by its ID
        return mongo.db.expenses.find_one({"_id": ObjectId(expense_id)})

    

