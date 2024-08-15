from flask import Flask, jsonify, render_template
import threading, time, os

from config import config
from operation_all import main_loop
from database.db import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/temp')
def temp():
    return render_template('temp.html')

@app.route('/api/ping', methods=['GET'])
def ping():
    response = {
        "message": "pong",
        "status": "success"
    }
    return jsonify(response)


@app.route('/api/programs/all')
def all_programs():
    programs = Programs.objects().all()

    response = {}
    for program in programs:
        response[program.program_name] = {
            'scopes': program.scopes,
            'ooscopes': program.ooscopes,
            'config': program.config,
            'created_date': program.created_date,
            }

    # Return JSON response
    return response

@app.route('/api/subdomains/domain/<domain>')
def subdomains_of_domain(domain):
    obj_subdomains = Subdomains.objects(scope=domain)

    if obj_subdomains:
        # Convert query result to list of dictionaries
        res_array = [f"{obj_sub.subdomain}" for obj_sub in obj_subdomains]
        return res_array
    else:
        return jsonify({'error': 'subdomain not found'})


@app.route('/api/subdomains/program/<p_name>')
def subdomains_of_program(p_name):
    obj_subdomains = Subdomains.objects(program_name=p_name)

    if obj_subdomains:
        res_array = [f"{obj_sub.subdomain}" for obj_sub in obj_subdomains]
        return res_array
    else:
        return jsonify({'error': 'subdomain not found'})
    
@app.route('/api/subdomains/all')
def all_subdomains():
    obj_subdomains = Subdomains.objects().all()

    if obj_subdomains:
        res_array = [f"{obj_sub.subdomain}" for obj_sub in obj_subdomains]
        return res_array

if __name__ == '__main__':
    threading.Thread(target=main_loop, args=()).start()
    
    app.run(debug=True)
        

