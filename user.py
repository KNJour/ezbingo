from mysqlconnection import connectToMySQL
class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.username = data['username']
        self.password = data['password']
        self.email = data['email']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
    @classmethod
    def all_users(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL('ezbingo').query_db(query)

        users = []
        for user in results:
            users.append( cls(user) )
        return users