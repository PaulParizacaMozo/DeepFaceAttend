# User Login as Student
curl -X POST http://127.0.0.1:5000/auth/login \
-H "Content-Type: application/json" \
-d '{
    "email": "luciana.h@email.com",
    "password": "123456"
}'

# User Login as Teacher
curl -X POST http://127.0.0.1:5000/auth/login \
-H "Content-Type: application/json" \
-d '{
    "email": "alvaro.m@email.com",
    "password": "profesor123"
}'


# Register a new User (Student)
curl -X POST http://127.0.0.1:5000/auth/register \
-H "Content-Type: application/json" \
-d '{
    "email": "ana_quispe@gmail.com",
    "password": "123456",
    "role": "student",
    "first_name": "Ana",
    "last_name": "Quispe",
    "cui": "20225678"
}'