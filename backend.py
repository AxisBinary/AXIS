import json
import sys
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from datetime import date

def validate_login(access_code, password):
    try:
        # Check MongoDB connection
        client = MongoClient('mongodb://localhost:27017/', serverSelectionTimeoutMS=5000)
        client.admin.command('ping')  # Test connection
        db = client['axislimited']
        collection = db['axislimited']

        # Check for empty fields
        if not access_code:
            return {'success': False, 'message': 'Access code is required'}
        if not password:
            return {'success': False, 'message': 'Password is required'}

        # Find user with matching access_code (with dashes) and password
        user = collection.find_one({'access_code': access_code, 'password': password})

        if user:
            # Check if activation_date is null and update to current date
            if user.get('activation_date') is None:
                collection.update_one(
                    {'access_code': access_code, 'password': password},
                    {'$set': {'activation_date': date.today().isoformat()}}  # e.g., "2025-05-30"
                )
            return {'success': True, 'message': 'Login successful'}
        else:
            return {'success': False, 'message': 'Invalid access code or password'}
    except ConnectionFailure:
        return {'success': False, 'message': 'MongoDB is not connected'}
    except Exception as e:
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
            print(json.dumps({'success': False, 'message': 'Invalid input format'}))
            sys.stdout.flush()