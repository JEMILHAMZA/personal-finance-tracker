# models/budget.py
from bson import ObjectId 
import logging




class Budget:
    @staticmethod
    def add_budget(user_id, amount, name):
        from app import mongo
        mongo.db.budgets.insert_one({
            "user_id": user_id,
            "amount": amount,
            "name": name  # Save the budget name
        })



    @staticmethod
    def get_all_categories(user_id):
        from app import mongo  # Import mongo instance here
        budgets = mongo.db.budgets.find({"user_id": str(user_id)})  # Convert user_id to string if needed
        return list({budget['name'] for budget in budgets if 'name' in budget})  # Ensure unique categories
    

    @staticmethod
    def get_all_budgets(user_id):
        from app import mongo
        budgets = mongo.db.budgets.find({"user_id": str(user_id)})
        all_budgets = []
        
        for budget in budgets:
            budget_data = {
                "id": str(budget["_id"]),  # Convert ObjectId to string
                "name": budget["name"],
                "amount": budget["amount"]
            }
            # Calculate spent amount for each budget
            expenses = mongo.db.expenses.find({"user_id": str(user_id), "category": budget["name"]})
            spent_amount = sum(expense["amount"] for expense in expenses)
            
            # Add spent and remaining to budget data
            budget_data["spent_amount"] = spent_amount
            budget_data["remaining_amount"] = budget["amount"] - spent_amount
            
            all_budgets.append(budget_data)
        
        return all_budgets



    @staticmethod
    def update_budget(budget_id, new_name, new_amount):
        from app import mongo
        mongo.db.budgets.update_one(
            {"_id": ObjectId(budget_id)},
            {"$set": {"name": new_name, "amount": new_amount}}
        )

    @staticmethod
    def delete_budget(budget_id):
        from app import mongo
        mongo.db.budgets.delete_one({"_id": ObjectId(budget_id)})


    

    @staticmethod
    def get_remaining_amount(user_id, category_name):
        from app import mongo
        budget = mongo.db.budgets.find_one({"user_id": str(user_id), "name": category_name})
        
        if budget:
            expenses = mongo.db.expenses.find({"user_id": str(user_id), "category": category_name})
            spent_amount = sum(expense["amount"] for expense in expenses)
            return budget["amount"] - spent_amount  # Remaining amount
        
        return 0  # No budget found for category
    

    @staticmethod
    def get_budget_by_id(budget_id):
        from app import mongo
        # Retrieve the income document by its ID
        return mongo.db.budgets.find_one({"_id": ObjectId(budget_id)})


    




