from django.shortcuts import render
from django.http import JsonResponse
import mysql.connector
from mysql.connector import Error

def get_db_status():
    status = {}
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='your_database_name',
            user='your_username',
            password='your_password'
        )
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Uptime';")
            status['uptime'] = cursor.fetchone()['Value']
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Threads_connected';")
            status['connections'] = cursor.fetchone()['Value']
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Aborted_connects';")
            status['aborted_connects'] = cursor.fetchone()['Value']
            
            cursor.execute("SHOW GLOBAL STATUS LIKE 'Questions';")
            status['questions'] = cursor.fetchone()['Value']

            cursor.execute("SHOW GLOBAL STATUS LIKE 'Slow_queries';")
            status['slow_queries'] = cursor.fetchone()['Value']

        else:
            status['error'] = 'Failed to connect to database'
    except Error as e:
        status['error'] = str(e)
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return status

def dashboard(request):
    status = get_db_status()
    return render(request, 'dashboard/dashboard.html', {'status': status})

def dashboard_data(request):
    status = get_db_status()
    return JsonResponse(status)