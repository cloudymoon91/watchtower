# watchtower

watch_sync_programs
watch_enum_all
watch_name_resolution_all
watch_http_all
watch_nuclei_all

## setup
1. inside the `database` folder run `docker compose up -d`
2. install requirements
```bash
pip3 install -r requirements.txt
```

3. configure zsh alias variables

## zshrc configurations
add following lines to your `~/.zshrc` file:
```bash
export GOPATH=$HOME/go
export GOROOT=/usr/local/go
export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
export WATCH="/root/watchtower"
alias watch_sync_programs="$WATCH/programs/watch_sync_programs.py"
alias watch_sync_chaos="$WATCH/chaos/watch_sync_chaos.py"
alias watch_subfinder="$WATCH/enumeration/watch_subfinder.py"
alias watch_crtsh="$WATCH/enumeration/watch_crtsh.py"
alias watch_abuseipdb="$WATCH/enumeration/watch_abuseipdb.py"
alias watch_chaos="$WATCH/enumeration/watch_chaos.py"
alias watch_wayback="$WATCH/enumeration/watch_wayback.py"
alias watch_gau="$WATCH/enumeration/watch_gau.py"
alias watch_enum_all="$WATCH/enumeration/watch_enum_all.py"
alias watch_ns="$WATCH/name_resolution/watch_ns.py"
alias watch_ns_brute="$WATCH/name_resolution/watch_ns_brute.py"
alias watch_ns_all="$WATCH/name_resolution/watch_ns_all.py"
alias watch_http="$WATCH/httpx/watch_http.py"
alias watch_http_all="$WATCH/httpx/watch_http_all.py"
alias watch_nuclei="$WATCH/nuclei/watch_nuclei.py"
alias watch_nuclei_all="$WATCH/nuclei/watch_nuclei_all.py"
```

```bash
chmod +x programs/watch_sync_programs.py
chmod +x chaos/watch_sync_chaos.py
chmod +x enumeration/watch_*
chmod +x name_resolution/watch_ns*
chmod +x httpx/watch_http*
chmod +x nuclei/watch_nuclei*
```
source ~/.zshrc

4. dns resolvers
nano ~/.resolvers
    8.8.4.4
    129.250.35.251
    208.67.222.222

5. tools must be installed
apt-get install unzip
apt-get install jq
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest
go install -v github.com/lc/gau/v2/cmd/gau@latest
go install -v github.com/tomnomnom/waybackurls@latest
go install -v github.com/tomnomnom/unfurl@latest
pip3 install dnsgen
go install -v github.com/projectdiscovery/shuffledns/cmd/shuffledns@latest
apt-get install crunch 
go install -v github.com/ImAyrix/cut-cdn@latest
go install -v github.com/tomnomnom/anew@latest
install massdns
    apt-get update
    apt-get install -y build-essential git
    git clone https://github.com/blechschmidt/massdns.git
    cd massdns
    make
    cp bin/massdns /usr/local/bin/

6. do the following commands for start:
```bash
watch_sync_programs
watch_sync_chaos
watch_enum_all
watch_ns_all
watch_http_all
watch_nuclei_all
```

7. run with this command:
```bash
tmux attach -t watchtower
python3 app.py
```

8. update nuclei
```bash
nuclei --update
```

9. killing other web server
 kill -9 `sudo lsof -t -i:5000`
