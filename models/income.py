# income.py
from bson import ObjectId

class Income:
    @staticmethod
    def add_income(user_id, amount, source):
        from app import mongo
        mongo.db.incomes.insert_one({
            "user_id": user_id,
            "amount": amount,
            "source": source
        })

    @staticmethod
    def get_all_incomes(user_id):
        from app import mongo
        incomes = mongo.db.incomes.find({"user_id": str(user_id)})
        return list(incomes)
    


    @staticmethod
    def update_income(income_id, new_name, new_amount):
        from app import mongo
        mongo.db.incomes.update_one(
            {"_id": ObjectId(income_id)},
            {"$set": {"source": new_name, "amount": new_amount}}
        )

    @staticmethod
    def delete_income(income_id):
        from app import mongo
        mongo.db.incomes.delete_one({"_id": ObjectId(income_id)})


    @staticmethod
    def get_income_by_id(income_id):
        from app import mongo
        # Retrieve the income document by its ID
        return mongo.db.incomes.find_one({"_id": ObjectId(income_id)})


