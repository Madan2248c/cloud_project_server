import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
cred = credentials.Certificate('./config/firebase.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://cloudcomputing-4555d-default-rtdb.firebaseio.com' 
})

# 2. Define your test data
test_data = {
    'users': {
        'user1': {
            'name': 'Alice',
            'age': 30,  
            'city': 'New York'
        },
        'user2': {
            'name': 'Bob',
            'age': 25,
            'city': 'London'
        }
    },
    'products': {
        'product1': {
            'name': 'Laptop',
            'price': 1200
        },
        'product2': {
            'name': 'Smartphone',
            'price': 800
        }
    }
}

# 3. Push the test data to your database
ref = db.reference('/tttt')  # Get a reference to the root of your database
ref.set(test_data)

print("Test data pushed successfully!")
