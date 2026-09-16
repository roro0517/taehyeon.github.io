# Deploy Guacamole via Docker + Firewall Setup (kaggle-vm)
 
## 0. SSH into kaggle-vm
 
```bash
gcloud compute ssh kaggle-vm --zone=us-central1-a
```
 
## 1. Check Docker is installed (inside kaggle-vm SSH)
 
```bash
docker --version
```
 
If not installed:
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
exit
```
Reconnect via SSH and continue.
 
## 2. Create working folder and docker-compose.yml
 
```bash
mkdir -p ~/guacamole && cd ~/guacamole
cat > docker-compose.yml << 'EOF'
services:
  guacd:
    image: guacamole/guacd
    restart: always
  guacamole:
    image: guacamole/guacamole
    restart: always
    ports:
      - "8080:8080"
    environment:
      GUACD_HOSTNAME: guacd
      MYSQL_HOSTNAME: mysql
      MYSQL_DATABASE: guacamole_db
      MYSQL_USER: guacamole_user
      MYSQL_PASSWORD: changeme123
    depends_on:
      - guacd
      - mysql
  mysql:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: rootpass123
      MYSQL_DATABASE: guacamole_db
      MYSQL_USER: guacamole_user
      MYSQL_PASSWORD: changeme123
    volumes:
      - mysql-data:/var/lib/mysql
volumes:
  mysql-data:
EOF
```
 
## 3. Generate DB init SQL
 
```bash
docker run --rm guacamole/guacamole /opt/guacamole/bin/initdb.sh --mysql > initdb.sql
```
 
## 4. Start MySQL first, then inject schema
 
```bash
docker compose up -d mysql
sleep 20
docker exec -i $(docker compose ps -q mysql) mysql -u root -prootpass123 guacamole_db < initdb.sql
```
 
## 5. Start everything
 
```bash
docker compose up -d
```
 
## 6. Check status
 
```bash
docker compose ps
```
Success if all three containers (`guacd`, `guacamole`, `mysql`) show `Up`.
 
---
 
## 7. Open firewall (in Cloud Shell, NOT kaggle-vm)
 
```bash
gcloud compute firewall-rules create allow-guacamole \
  --allow=tcp:8080 \
  --source-ranges=211.223.33.71/32 \
  --target-tags=kaggle-vm
```
 
**Add tag to VM**
```bash
gcloud compute instances add-tags kaggle-vm --zone=us-central1-a --tags=kaggle-vm
```
 
**Get external IP**
```bash
gcloud compute instances describe kaggle-vm --zone=us-central1-a \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
```
 
## 8. Connect in browser
 
```
http://<external_IP>:8080/guacamole
```
Example: if external IP is `34.57.190.113` → `http://34.57.190.113:8080/guacamole`
 
**Login**
- ID: `guacadmin`
- PW: `guacadmin`
Change the password right after logging in: top-right account icon → Settings → Preferences tab → Update Password
 
## 9. Register the VNC connection
 
If you're logged in but see nothing, it's because no connection has been registered yet. Guacamole shows a blank home screen until you add one.
 
Settings → Connections tab → New Connection:
 
| Field | Value |
|---|---|
| Name | kaggle-desktop (any name) |
| Protocol | VNC |
| Hostname | 172.17.0.1 |
| Port | 5901 |
| Password | kaggle1 |
 
Save, then go back to the home screen — the new `kaggle-desktop` connection will appear in the list. Click it to open the VNC desktop.
 
If you click it and nothing loads, check what error appears (e.g. "Connection refused", stuck loading, or a black screen) — that determines the next fix.
