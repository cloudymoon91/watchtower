from mongoengine import Document, StringField, DateTimeField, ListField, DictField, connect
from datetime import datetime
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
    cdn = StringField()
    created_date = DateTimeField(default=datetime.now())
    last_update = DateTimeField(default=datetime.now())

    meta = {
        'indexes': [
            {'fields': ['program_name', 'subdomain'], 'unique': True}  # Create a unique index on 'program_name' and 'subdomain'
        ]
    }

# Define the LiveSubdomains model
# todo: extend the model to store CNMAE, TXT, etc
class HTTP(Document):
    program_name = StringField(required=True)
    subdomain = StringField(required=True)
    scope = StringField(required=True)
    ips = ListField(StringField())
    tech = ListField(StringField())
    title = StringField()
    status_code = ListField(StringField())
    headers = DictField()
    url = StringField()
    created_date = DateTimeField(default=datetime.now())
    last_update = DateTimeField(default=datetime.now())

    meta = {
        'indexes': [
            {'fields': ['program_name', 'subdomain'], 'unique': True}  # Create a unique index on 'program_name' and 'subdomain'
        ]
    }


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

def upsert_lives(obj):
    # obj: {'subdomain': 'account.web.superbet.ro', 'domain': 'superbet.ro', 'ips': ['18.245.253.35', '18.245.253.54', '18.245.253.9', '18.245.253.27']}

    program = Programs.objects(scopes=obj.get('domain')).first()
    # program.program_name

    existing = LiveSubdomains.objects(subdomain=obj.get('subdomain')).first()
    if existing:
        existing.ips.sort()
        obj.get('ips').sort()
        
        if obj.get('ips') != existing.ips:
            existing.ips = obj.get('ips')
            existing.last_update = datetime.now()
            existing.save()
            print(f"[{util.current_time()}] Updated live subdomain: {obj.get('subdomain')}")
            
    else:
        new_live_subdomain = LiveSubdomains(
            program_name=program.program_name,
            subdomain=obj.get('subdomain'),
            scope=obj.get('domain'),
            ips=obj.get('ips'),
            cdn=obj.get('cdn'),
            created_date=datetime.now(),
            last_update=datetime.now()
        )
        new_live_subdomain.save()

        # todo: notify if new live subdomain is added!
        util.send_discord_message(f"```'{obj.get('subdomain')}' (fresh live) has been added to '{program.program_name}' program```")
        print(f"[{util.current_time()}] Inserted new live subdomain: {obj.get('subdomain')}")

    return True

# Check if subdomain exists, if not insert, if yes update providers
def upsert_subdomain(program_name, subdomain_name, provider):

    program = Programs.objects(program_name=program_name).first()
    if util.get_domain_name(subdomain_name) not in program.scopes or subdomain_name in program.ooscopes:
        print(f"[{util.current_time()}] subdomain is not in scope: {subdomain_name}")
        return True
    
    # todo: check if subdomain exists or not, filter: domain.tld or *.domain.tld
    
    existing = Subdomains.objects(program_name=program_name, subdomain=subdomain_name).first()
    
    if existing:
        if provider not in existing.providers:
            existing.providers.append(provider)
            existing.last_update = datetime.now()
            existing.save()
            print(f"[{util.current_time()}] Updated subdomain: {subdomain_name}")
        else:
            pass
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