
import tldextract, requests, time, subprocess
from datetime import datetime
import fnmatch, tempfile, os, re, json


class colors:
    GRAY = "\033[90m"
    RESET = "\033[0m"
    
def current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_domain_name(url):
    ext = tldextract.extract(url)
    return f"{ext.domain}.{ext.suffix}"

def send_discord_message(message, webhook_url):
    with open('settings.json', 'r') as file:
        settings = json.load(file)
        
    if not settings.get("NOTIF"):
        return
    
    while True: 
        data = {
            "content": message
        }

        response = requests.post(webhook_url, json=data)

        if response.status_code == 204:
            break
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
            time.sleep(1)


def run_command_in_zsh(command, read_line=True):
    try:
        result = subprocess.run(["zsh", "-c", command], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error occurred:", result.stderr)
            return False
        if read_line:
            return result.stdout.splitlines()
        return result.stdout
    except subprocess.CalledProcessError as exc:
        print("Status : FAIL", exc.returncode, exc.output)
        

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

def get_ip_tag(ips):
    # Create a temporary file to store the list of ips
    with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
        for ip in ips:
            temp_file.write(f"{ip}\n")

    ips_file = temp_file.name
    command = f"cut-cdn -i {ips_file} --silent"

    results = run_command_in_zsh(command)
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
