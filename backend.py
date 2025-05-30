import json
import sys
import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import date

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def validate_login(access_code, password):
    try:
        # Check MongoDB connection
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test connection
        logger.info("Connected to MongoDB")
        db = client['axislimited']
        collection = db['axislimited']

        # Check for empty fields
        if not access_code:
            logger.warning("Access code is empty")
            return {'success': False, 'message': 'Access code is required'}
        if not password:
            logger.warning("Password is empty")
            return {'success': False, 'message': 'Password is required'}

        # Find user with matching access_code and password
        user = collection.find_one({'access_code': access_code, 'password': password})
        if not user:
            logger.warning(f"Invalid credentials for access_code: {access_code}")
            return {'success': False, 'message': 'Invalid access code or password'}

        # Check if activation_date is null and update to current date
        if user.get('activation_date') is None:
            try:
                result = collection.update_one(
                    {'access_code': access_code, 'password': password, 'activation_date': None},
                    {'$set': {'activation_date': date.today().isoformat()}}  # e.g., "2025-05-30"
                )
                if result.modified_count == 1:
                    logger.info(f"Updated activation_date to {date.today().isoformat()} for access_code: {access_code}")
                else:
                    logger.warning(f"Failed to update activation_date for access_code: {access_code}")
            except PyMongoError as e:
                logger.error(f"Error updating activation_date for access_code: {access_code}: {str(e)}")
                return {'success': False, 'message': 'Failed to update activation date'}

        return {'success': True, 'message': 'Login successful'}

    except ConnectionFailure:
        logger.error("MongoDB connection failed")
        return {'success': False, 'message': 'MongoDB is not connected'}
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return {'success': False, 'message': f'Server error: {str(e)}'}

if __name__ == '__main__':
    # Read input from Electron
    for line in sys.stdin:
        try:
            data = json.loads(line)
            access_code = data.get('access_code', '').strip()
            password = data.get('password', '').strip()
            result = validate_login(access_code, password)
            print(json.dumps(result))
            sys.stdout.flush()
        except json.JSONDecodeError:
            logger.error("Invalid JSON input")
            print(json.dumps({'success': False, 'message': 'Invalid input format'}))
            sys.stdout.flush()