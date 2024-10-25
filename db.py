
import motor.motor_tornado

from config import settings
uri = settings.MONGODB_URL

# Create a new client and connect to the server
client = motor.motor_tornado.MotorClient(uri)

print(uri)

db = client.RuleNodes

collection = db["RuleNodes"]

final_node_collection = db["StringWithNode"]