# Connect to VNC via Guacamole (GCP kaggle-vm)
 
Quick reference for reconnecting to the VNC desktop through Guacamole, assuming XFCE/VNC and the Guacamole containers are already installed on kaggle-vm.
 
## 1. SSH into kaggle-vm (Cloud Shell or local terminal)
 
```bash
gcloud compute ssh kaggle-vm --zone=us-central1-a
```
 
## 2. Inside kaggle-vm SSH — start VNC if not running
 
```bash
vncserver
```
*(If it's already running, this will error out safely — that's fine.)*
 
## 3. Inside kaggle-vm SSH — start Guacamole containers
 
```bash
cd ~/guacamole
docker compose up -d
docker compose ps
```
 
## 4. In Cloud Shell (NOT kaggle-vm) — open firewall for your IP
 
```bash
gcloud compute firewall-rules create allow-guacamole \
  --allow=tcp:8080 \
  --source-ranges=211.223.33.71/32 \
  --target-tags=kaggle-vm
 
gcloud compute instances add-tags kaggle-vm --zone=us-central1-a --tags=kaggle-vm
```
*Skip this step if the rule already exists — running it twice just errors "already exists", which is fine.*
 
## 5. In Cloud Shell — get the external IP
 
```bash
gcloud compute instances describe kaggle-vm --zone=us-central1-a \
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
```
 
## 6. In your browser
 
```
http://<external_IP>:8080/guacamole
```
 
Login: `guacadmin` / `guacadmin` (or your changed password)
 
## 7. Open the desktop
 
Click the **kaggle-desktop** connection on the home screen — that opens the VNC desktop.
 
If it's not there yet, add it under Settings → Connections → New Connection:
 
| Field | Value |
|---|---|
| Protocol | VNC |
| Hostname | `172.17.0.1` (or kaggle-vm's internal IP `10.128.0.x` if that doesn't work) |
| Port | 5901 |
| Password | kaggle1 |
