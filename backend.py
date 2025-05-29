import json
import sys
from pymongo import MongoClient

def validate_login(access_code, password):
    try:
        # Check for empty fields
        if not access_code:
            return {'success': False, 'message': 'Access code is required'}
        if not password:
            return {'success': False, 'message': 'Password is required'}

        # Connect to MongoDB
        client = MongoClient('mongodb://localhost:27017/')
        db = client['axislimited']
        collection = db['axislimited']

        # Find user with matching access_code (with dashes) and password
        user = collection.find_one({'access_code': access_code, 'password': password})

        if user:
            return {'success': True, 'message': 'Login successful'}
        else:
            return {'success': False, 'message': 'Invalid access code or password'}
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