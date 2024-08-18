from mongoengine import Document, StringField, DateTimeField, ListField, DictField, IntField, connect
from datetime import datetime
from config.config import config
from utils import util


# Connect to MongoDB
connect(db='watch', host='mongodb://127.0.0.1:27017/watch')

# Define the Programs model
class Programs(Document):
    program_name = StringField(required=True)
    created_date = DateTimeField(default=datetime.now())
    config = DictField()
    scopes = ListField(StringField(), default=[])
    ooscopes = ListField(StringField(), default=[])

    meta = {
        'indexes': [
            {'fields': ['program_name'], 'unique': True}  # Create a unique index on 'name'
        ]
    }

# Define the Subdomains model
class Subdomains(Document):
    program_name = StringField(required=True)
    subdomain = StringField(required=True)
    scope = StringField(required=True)
    providers = ListField(StringField())
    created_date = DateTimeField(default=datetime.now())
    last_update = DateTimeField(default=datetime.now())

    meta = {
        'indexes': [
            {'fields': ['program_name', 'subdomain'], 'unique': True}  # Create a unique index on 'program_name' and 'subdomain'
        ]
    }

# Define the LiveSubdomains model
# todo: extend the model to store CNMAE, TXT, etc
class LiveSubdomains(Document):
    program_name = StringField(required=True)
    subdomain = StringField(required=True)
    scope = StringField(required=True)
    ips = ListField(StringField())
    tag = StringField()
    created_date = DateTimeField(default=datetime.now)
    last_update = DateTimeField(default=datetime.now)

    meta = {
        'indexes': [
            {'fields': ['program_name', 'subdomain'], 'unique': True}
        ]
    }

# Define the LiveSubdomains model
# todo: extend the model to store CNMAE, TXT, etc
class Http(Document):
    program_name = StringField(required=True)
    subdomain = StringField(required=True)
    scope = StringField(required=True)
    ips = ListField(StringField())
    tech = ListField(StringField())
    title = StringField()
    status_code = IntField()
    headers = DictField()
    url = StringField()
    final_url = StringField()
    favicon = StringField()
    created_date = DateTimeField(default=datetime.now())
    last_update = DateTimeField(default=datetime.now())

    meta = {
        'indexes': [
            {'fields': ['program_name', 'subdomain'], 'unique': True}  # Create a unique index on 'program_name' and 'subdomain'
        ]
    }

'''
1. http service to work on (general)
2. http fresh services to work on
3. searching through HTTP headers
4. changes of techs or status codes or etc
'''



# Upsert Programs
def upsert_program(program_name, scopes, ooscopes, config):
    program = Programs.objects(program_name=program_name).first()
    
    if program:
        # Update existing program fields
        program.config = config
        program.scopes = scopes
        program.ooscopes = ooscopes
        program.save()
        print(f"[{util.current_time()}] Updated program: {program.program_name}")
    else:
        # Create new program
        new_program = Programs(
            program_name=program_name,
            created_date=datetime.now(),
            config=config,
            scopes=scopes,
            ooscopes=ooscopes
        )
        new_program.save()
        print(f"[{util.current_time()}] Inserted new program: {new_program.program_name}")


def upsert_lives(domain, subdomain, ips, tag):
    program = Programs.objects(scopes=domain).first()
    existing = LiveSubdomains.objects(subdomain=subdomain).first()

    if existing:
        existing.ips.sort()
        ips.sort()
        if ips != existing.ips:
            existing.ips = ips
            print(f"[{util.current_time()}] Updated live subdomain: {subdomain}")
        existing.last_update = datetime.now()
        existing.save()
    else:
        new_live_subdomain = LiveSubdomains(
            program_name=program.program_name,
            subdomain=subdomain,
            scope=domain,
            ips=ips,
            tag=tag,
            created_date=datetime.now(),
            last_update=datetime.now(),
        )
        new_live_subdomain.save()
        util.send_discord_message(f"```'{subdomain}' (fresh live) has been added to '{program.program_name}' program```", config().get('WEBHOOK_URL_NS'))
        print(f"[{util.current_time()}] Inserted new live subdomain: {subdomain}")

    return True

def upsert_http(obj):
    # {'subdomain': 'dl-api.voorivex.academy', 'scope': 'voorivex.academy', 'ips': ['185.166.104.4', '185.166.104.3'], 'tech': ['HSTS'], 'title': '', 'status_code': 403, 'headers': {'accept_ranges': 'bytes', 'cache_control': 'no-store', 'content_length': '15', 'content_type': 'text/html; charset=utf-8', 'date': 'Thu, 15 Aug 2024 12:45:17 GMT', 'server': 'Delivery', 'strict_transport_security': 'max-age=31536000', 'x_zrk_sn': '2001'}, 'url': 'https://dl-api.voorivex.academy:443', 'final_url': ''}

    program = Programs.objects(scopes=obj.get('scope')).first()
    # program.program_name

    # already existed http service
    existing = Http.objects(subdomain=obj.get('subdomain')).first()
    if existing:

        if existing.title != obj.get('title'):
            util.send_discord_message(f"```'{obj.get('subdomain')}' title has been changed from '{existing.title}' to '{obj.get('title')}'```", config().get('WEBHOOK_URL_HTTP'))
            print(f"[{util.current_time()}] changes title for subdomain: {obj.get('subdomain')}")
            existing.title = obj.get('title')

        if existing.status_code != obj.get('status_code'):
            util.send_discord_message(f"```'{obj.get('subdomain')}' status code has been changed from '{existing.status_code}' to '{obj.get('status_code')}'```", config().get('WEBHOOK_URL_HTTP'))
            print(f"[{util.current_time()}] changes status code for subdmoain: {obj.get('subdomain')}")
            existing.status_code = obj.get('status_code')

        
        if existing.favicon != obj.get('favicon'):
            util.send_discord_message(f"```'{obj.get('subdomain')}' favhash has been changed from '{existing.favicon}' to '{obj.get('favicon')}'```", config().get('WEBHOOK_URL_HTTP'))
            print(f"[{util.current_time()}] changes favhash for subdomain: {obj.get('subdomain')}")
            existing.favicon = obj.get('favicon')

        existing.ips = obj.get('ips')
        existing.tech = obj.get('tech')
        existing.headers = obj.get('headers')
        existing.url = obj.get('url')
        existing.final_url = obj.get('final_url')
        existing.last_update = datetime.now()
        existing.save()

    else:
        new_http = Http(
            program_name = program.program_name,
            subdomain = obj.get('subdomain'),
            scope = obj.get('scope'),
            ips = obj.get('ips'),
            tech = obj.get('tech'),
            title = obj.get('title'),
            status_code = obj.get('status_code'),
            headers = obj.get('headers'),
            url = obj.get('url'),
            final_url = obj.get('final_url'),
            favicon = obj.get('favicon'),
            created_date = datetime.now(),
            last_update = datetime.now()
        )
        new_http.save()

        # todo: notify if new live subdomain is added!
        util.send_discord_message(f"```'{obj.get('subdomain')}' (fresh http) has been added to '{program.program_name}' program```", config().get('WEBHOOK_URL_HTTP'))
        print(f"[{util.current_time()}] Inserted new http service: {obj.get('subdomain')}")

    return True

# Check if subdomain exists, if not insert, if yes update providers
def upsert_subdomain(program_name, subdomain_name, provider):

    program = Programs.objects(program_name=program_name).first()

    if not util.is_in_scope(subdomain_name, program.scopes, program.ooscopes):
        print(f"[{util.current_time()}] subdomain is not in scope: {subdomain_name}")
        return True

    existing = Subdomains.objects(program_name=program_name, subdomain=subdomain_name).first()

    if existing:
        if provider not in existing.providers:
            existing.providers.append(provider)
            existing.last_update = datetime.now()
            existing.save()
            print(f"[{util.current_time()}] Updated subdomain: {subdomain_name}")
    else:
        new_subdomain = Subdomains(
            program_name=program_name,
            subdomain=subdomain_name,
            scope=util.get_domain_name(subdomain_name),
            providers=[provider],
            created_date=datetime.now(),
            last_update=datetime.now()
        )
        new_subdomain.save()
        print(f"[{util.current_time()}] Inserted new subdomain: {subdomain_name}")