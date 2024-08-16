# watchtower

watch_sync_programs
watch_enum_all
watch_name_resolution_all
watch_http_all
watch_nuclei_all

## setup
docker compose up -f
nano ~/.zshrc
    export GOPATH=$HOME/go
    export GOROOT=/usr/local/go
    export PATH=$GOPATH/bin:$GOROOT/bin:$PATH
source ~/.zshrc

killing other web server
 kill -9 `sudo lsof -t -i:5000`