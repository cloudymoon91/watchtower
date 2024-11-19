from mongoengine import Document, StringField, DateTimeField, ListField, DictField, IntField, connect
from datetime import datetime, timedelta
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

def upsert_program(program_name, scopes, ooscopes, config):
    program = Programs.objects(program_name=program_name).first()

    if program:
        program.config = config
        program.scopes = scopes
        program.ooscopes = ooscopes
        program.save()
        util.logger.debug(f"[{util.current_time()}] Updated program: {program.program_name}")
    else:
        new_program = Programs(
            program_name=program_name,
            created_date=datetime.now(),
            config=config,
            scopes=scopes,
            ooscopes=ooscopes
        )
        new_program.save()
        util.logger.debug(f"[{util.current_time()}] Inserted new program: {new_program.program_name}")


def upsert_lives(domain, subdomain, ips, tag):
    subdomain = subdomain.lower()
    program = Programs.objects(scopes=domain).first()
    existing = LiveSubdomains.objects(subdomain=subdomain).first()

    if existing:
        existing.ips.sort()
        ips.sort()
        if ips != existing.ips:
            existing.ips = ips
            util.logger.debug(f"[{util.current_time()}] Updated live subdomain: {subdomain}")
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
        util.send_discord_message(f"```'{subdomain}' (fresh live) has been added to '{program.program_name}' program```", "WEBHOOK_URL_NS")
        util.logger.debug(f"[{util.current_time()}] Inserted new live subdomain: {subdomain}")

    return True

def upsert_http(subdomain, scope, ips, tech, title, status_code, headers, url, final_url, favicon):
    # {'subdomain': 'dl-api.voorivex.academy', 'scope': 'voorivex.academy', 'ips': ['185.166.104.4', '185.166.104.3'], 'tech': ['HSTS'], 'title': '', 'status_code': 403, 'headers': {'accept_ranges': 'bytes', 'cache_control': 'no-store', 'content_length': '15', 'content_type': 'text/html; charset=utf-8', 'date': 'Thu, 15 Aug 2024 12:45:17 GMT', 'server': 'Delivery', 'strict_transport_security': 'max-age=31536000', 'x_zrk_sn': '2001'}, 'url': 'https://dl-api.voorivex.academy:443', 'final_url': ''}

    program = Programs.objects(scopes=scope).first()
    # program.program_name

    # already existed http service
    existing = Http.objects(subdomain=subdomain).first()
    if existing:

        if existing.title != title:
            util.send_discord_message(f"```'{subdomain}' title has been changed from '{existing.title}' to '{title}'```", "WEBHOOK_URL_HTTP")
            util.logger.debug(f"[{util.current_time()}] changes title for subdomain: {subdomain}")
            existing.title = title

        if existing.status_code != status_code:
            util.send_discord_message(f"```'{subdomain}' status code has been changed from '{existing.status_code}' to '{status_code}'```", "WEBHOOK_URL_HTTP")
            util.logger.debug(f"[{util.current_time()}] changes status code for subdmoain: {subdomain}")
            existing.status_code = status_code

        
        if existing.favicon != favicon:
            util.send_discord_message(f"```'{subdomain}' favhash has been changed from '{existing.favicon}' to '{favicon}'```", "WEBHOOK_URL_HTTP")
            util.logger.debug(f"[{util.current_time()}] changes favhash for subdomain: {subdomain}")
            existing.favicon = favicon

        existing.ips = ips
        existing.tech = tech
        existing.headers = headers
        existing.url = url
        existing.final_url = final_url
        existing.last_update = datetime.now()
        existing.save()

    else:
        new_http = Http(
            program_name = program.program_name,
            subdomain = subdomain,
            scope = scope,
            ips = ips,
            tech = tech,
            title = title,
            status_code = status_code,
            headers = headers,
            url = url,
            final_url = final_url,
            favicon = favicon,
            created_date = datetime.now(),
            last_update = datetime.now()
        )
        new_http.save()

        util.send_discord_message(f"```'{subdomain}' (fresh http) has been added to '{program.program_name}' program```", "WEBHOOK_URL_HTTP")
        util.logger.debug(f"[{util.current_time()}] Inserted new http service: {subdomain}")

    return True

# Check if subdomain exists, if not insert, if yes update providers
def upsert_subdomain(program_name, subdomain, provider):
    program = Programs.objects(program_name=program_name).first()
    subdomain = subdomain.lower()
    if not util.is_in_scope(subdomain, program.scopes, program.ooscopes):
        util.logger.debug(f"[{util.current_time()}] subdomain is not in scope: {subdomain}")
        return True

    existing = Subdomains.objects(program_name=program_name, subdomain=subdomain).first()

    if existing:
        if provider not in existing.providers:
            existing.providers.append(provider)
            existing.last_update = datetime.now()
            existing.save()
            util.logger.debug(f"[{util.current_time()}] Updated subdomain: {subdomain}")
    else:
        new_subdomain = Subdomains(
            program_name=program_name,
            subdomain=subdomain,
            scope=util.get_domain_name(subdomain),
            providers=[provider],
            created_date=datetime.now(),
            last_update=datetime.now()
        )
        new_subdomain.save()
        util.logger.debug(f"[{util.current_time()}] Inserted new subdomain: {subdomain}")
        
def get_subdomains(
    program=None,
    scope=None,
    provider=None,
    fresh=False,
    count=False,
    limit=None,
    page=None,
):
    filters = {}
    if program:
        filters["program_name"] = program
    if scope:
        filters["scope"] = scope
    if provider:
        filters["providers"] = [provider]
    if fresh:
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        filters["created_date__gte"] = twenty_four_hours_ago

    subdomains = Subdomains.objects(**filters)
    if count:
        return subdomains.count()

    if limit is not None and page is not None:
        offset = (page - 1) * limit
        subdomains = subdomains.skip(offset).limit(limit)

    return subdomains

def get_lives(
    program=None,
    scope=None,
    provider=None,
    tag=None,
    fresh=False,
    count=False,
    limit=None,
    page=None,
):
    filters = {}
    if program:
        filters["program_name"] = program
    if scope:
        filters["scope"] = scope
    if fresh:
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        filters["created_date__gte"] = twenty_four_hours_ago
    if provider:
        twelve_hours_ago = datetime.now() - timedelta(hours=12)
        subdomains = Subdomains.objects(providers=[provider])
        sub_urls = [sub.subdomain for sub in subdomains]
        filters["subdomain__in"] = sub_urls
        filters["last_update__gte"] = twelve_hours_ago
    if tag != None:
        filters["tag"] = tag

    subdomains = LiveSubdomains.objects(**filters)
    if count:
        return subdomains.count()

    if limit is not None and page is not None:
        offset = (page - 1) * limit
        subdomains = subdomains.skip(offset).limit(limit)

    return subdomains


def get_http_services(
    program=None,
    scope=None,
    provider=None,
    title=None,
    status=None,
    fresh=False,
    latest=False,
    count=False,
    limit=None,
    page=None,
):
    filters = {}
    if program:
        filters["program_name"] = program
    if scope:
        filters["scope"] = scope
    if fresh:
        twenty_four_hours_ago = datetime.now() - timedelta(hours=24)
        filters["created_date__gte"] = twenty_four_hours_ago
    if provider:
        subdomains = Subdomains.objects(providers=[provider])
        sub_urls = [sub.subdomain for sub in subdomains]
        filters["subdomain__in"] = sub_urls
    if title:
        filters["title"] = title
    if status:
        filters["status_code"] = status
    if latest:
        twelve_hours_ago = datetime.now() - timedelta(hours=12)
        filters["last_update__gte"] = twelve_hours_ago

    http = Http.objects(**filters)
    if count:
        return http.count()

    if limit is not None and page is not None:
        offset = (page - 1) * limit
        http = http.skip(offset).limit(limit)

    return http
