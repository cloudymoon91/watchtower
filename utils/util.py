
import tldextract, requests, time, subprocess
from datetime import datetime
import fnmatch, tempfile, os, re, logging, json
from config import config


# Step 3: Configure Flask logger
log_handler = logging.FileHandler(os.path.join('log', 'watchtower.log'))
log_handler.setLevel(logging.INFO)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

# Step 4: Configure stdout handler for Flask
flask_console_handler = logging.StreamHandler()
flask_console_handler.setLevel(logging.INFO)
flask_console_handler.setFormatter(log_formatter)

logger = logging.getLogger('watchtower_app')
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(flask_console_handler)  # Log to console


class colors:
    GRAY = "\033[90m"
    RESET = "\033[0m"

index_programs = 1
index_enumeration = 1
index_ns = 1
index_httpx = 1
index_nuclei = 1

http_messages = []
ns_messages = []
    
def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_domain_name(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"


def send_discord_file(message, webhook_name):
    # Open the file to send
    file_path = ""
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
            temp_file.write(f"{message}\n")
            file_path = temp_file.name
            
    files = {
        'file': ("{}.txt".format(file_path), message),
    }
    data = {
        'content': message[:100] if len(message) > 100 else message
    }
    while True: 
        # Prepare the data to send
        # Send the request to the webhook
        response = requests.post(config().get(webhook_name), data=data, files=files)
        
        if response.status_code == 204 or response.status_code == 200:
            if os.path.exists(file_path):
                os.remove(file_path)
            break
        else:
            logger.info(f"Failed to send message. Status code: {response.status_code} -> webhook: {webhook_name} -> response: {response.text}")
            time.sleep(1)

def send_discord_message(message, webhook_name):
    global http_messages, ns_messages
    if webhook_name == "WEBHOOK_URL_HTTP":
        http_messages.append(message)
    elif webhook_name == "WEBHOOK_URL_NS":
        ns_messages.append(message)
    else:
        logger.error("invalid webhook_name: {}".format(webhook_name))
        os._exit(1)
        
    with open('settings.json', 'r') as file:
        settings = json.load(file)

    if len(http_messages) >= settings.get("DISCORD_BATCH_SIZE_HTTP"): 
        send_discord_message_bath("\n".join(http_messages), webhook_name)
        http_messages = []
        
    if len(ns_messages) >= settings.get("DISCORD_BATCH_SIZE_NS"): 
        send_discord_message_bath("\n".join(ns_messages), webhook_name)
        ns_messages = []
    
def send_discord_message_bath(message, webhook_name):
    
    while True: 
        data = {
            "content": message
        }

        response = requests.post(config().get(webhook_name), json=data)

        if response.status_code == 204:
            break
        else:
            logger.info(f"Failed to send message. Status code: {response.status_code} -> webhook: {webhook_name} -> response: {response.text}")
            time.sleep(1)


def split_list_into_chunks(input_list, chunk_size):
    # Use list comprehension to split the list into chunks
    return [input_list[i:i + chunk_size] for i in range(0, len(input_list), chunk_size)]


def run_command_in_zsh(command, read_line=True):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True)
        if result.returncode != 0:
            logger.info("Error occurred: {}".format(result.stderr))
            return False
        if read_line:
            return result.stdout.splitlines()
        return result.stdout
    except subprocess.CalledProcessError as exc:
        logger.info("Status {}: FAIL: {}".format(exc.returncode, exc.output))
        

def matches_wildcard(domain, wildcard):
    # Convert domain and wildcard to lowercase
    domain = domain.lower()
    wildcard = wildcard.lower()
    
    # Use fnmatch to handle wildcard patterns
    return fnmatch.fnmatch(domain, wildcard)


def is_in_scope(subdomain_name, scopes, ooscopes):
    domain_name = get_domain_name(subdomain_name).lower()
    
    # Check if domain matches any out-of-scope patterns
    for ooscape in ooscopes:
        if matches_wildcard(subdomain_name, ooscape):
            return False
    
    # Check if domain is in scope
    if domain_name in scopes:
        return True

    return False

def get_ip_tag(ips):
    # Create a temporary file to store the list of ips
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        for ip in ips:
            temp_file.write(f"{ip}\n")

    ips_file = temp_file.name
    command = f"cut-cdn -i {ips_file} --silent"

    results = run_command_in_zsh(command)
    if os.path.exists(ips_file):
        os.remove(ips_file) 
        
    if not len(results) == len(ips):
        return "cdn"

    for ip in ips:
        if not is_private_ip(ip):
            return "public"
    return "private"

def is_private_ip(ip):
    """
    Check if the provided IP address is a private IPv4 address.

    Args:
    - ip (str): The IP address to check.

    Returns:
    - bool: True if the IP address is private, False otherwise.
    """
    # Regex pattern for private IPv4 addresses
    private_ipv4_pattern = re.compile(
        r"""
        \b
        (?:
            10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}              |   # 10.0.0.0 - 10.255.255.255
            172\.(?:1[6-9]|2[0-9]|3[01])\.(?:[0-9]{1,3}\.){1}[0-9]{1,3}   |   # 172.16.0.0 - 172.31.255.255
            192\.168\.(?:[0-9]{1,3}\.){1}[0-9]{1,3}          # 192.168.0.0 - 192.168.255.255
        )\b
    """,
        re.VERBOSE,
    )

    return bool(private_ipv4_pattern.match(ip))
