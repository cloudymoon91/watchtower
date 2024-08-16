from flask import Flask, jsonify, render_template
import threading
from datetime import datetime, timedelta

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

# TODO: @app.route('/api/lives/domain/<domain>')
# TODO: @app.route('/api/lives/program/<p_name>')

@app.route('/api/lives/all')
def all_lives():
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    lives_obj = LiveSubdomains.objects(last_update__gte=twelve_hours_ago).all()
    
    res_array = [f"{live_obj.subdomain}" for live_obj in lives_obj]
    return res_array

@app.route('/api/lives/fresh')
def all_lives_fresh():
    twenty_four_hours_ago = datetime.now() - timedelta(hours=24)

    fresh_lives = LiveSubdomains.objects(created_date__gte=twenty_four_hours_ago)
    
    res_array = [f"{fresh_live.subdomain}" for fresh_live in fresh_lives]
    return res_array

@app.route('/api/lives/provider/<provider>')
def all_lives_provider(provider):
    
    twelve_hours_ago = datetime.now() - timedelta(hours=12)
    subdomains = Subdomains.objects(providers=[provider])
    lives = [
        LiveSubdomains.objects(
            subdomain=sub.subdomain, last_update__gte=twelve_hours_ago
        ).first()
        for sub in subdomains
        if LiveSubdomains.objects(
            subdomain=sub.subdomain, last_update__gte=twelve_hours_ago
        )
    ]
    res_array = [f"{live.subdomain}" for live in lives]
    return res_array

if __name__ == '__main__':
    threading.Thread(target=main_loop, args=()).start()
    
    app.run(debug=True)
        

