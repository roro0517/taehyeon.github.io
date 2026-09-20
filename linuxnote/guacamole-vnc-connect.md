# Connect to VNC via Guacamole (GCP kaggle-vm)
 
Quick reference for reconnecting to the VNC desktop through Guacamole, assuming XFCE/VNC and the Guacamole containers are already installed on kaggle-vm.


 ## 1. SSH into kaggle-vm (TURN ON/OFF the VM) 
```bash 
#start/resume
gcloud compute instances start kaggle-vm --zone=us-central1-a #(@Cloud Shell)
```
```bash 
#to reconnect
gcloud compute ssh kaggle-vm --zone=us-central1-a #(@Cloud Shell)
```
```bash
#stop
gcloud compute instances stop kaggle-vm --zone=us-central1-a #(@Cloud Shell)
```
## 2. Start VNC if not running
 
```bash 
vncserver #(@VM)
```
*(If it's already running, this will error out safely — that's fine.)*
 
## 3. Start Guacamole containers
 
```bash 
cd ~/guacamole #(@VM)
docker compose up -d
docker compose ps 
```
 
## 4. Open firewall for your IP
 
```bash
#(@Cloud Shell)
gcloud compute firewall-rules create allow-guacamole \ 
  --allow=tcp:8080 \
  --source-ranges=211.223.33.71/32 \
  --target-tags=kaggle-vm
 
gcloud compute instances add-tags kaggle-vm --zone=us-central1-a --tags=kaggle-vm
```
*Skip this step if the rule already exists — running it twice just errors "already exists", which is fine.*
 
## 5. Get the external IP
 
```bash
#(@Cloud Shell)
gcloud compute instances describe kaggle-vm --zone=us-central1-a \ 
  --format="value(networkInterfaces[0].accessConfigs[0].natIP)"
```
 
## 6. Open it in the browser (싸지방)
 
```
http://<VMExternalIP>:8080/guacamole
```
 
Login: `guacadmin` / `rlaxogus` (or your changed password)

 
## 7. Open the desktop
 
Click the **kaggle-desktop** connection on the home screen — that opens the VNC desktop.
 
If it's not there yet, add it under Settings → Connections → New Connection:



# When connecting at PC bang

1. Get the PC bang's public IP

Run this on the PC bang computer's browser (not in Cloud Shell, since that shows Google's IP): search "what is my IP", or open https://ifconfig.me.

2. Update the rule in Cloud Shell
```bash
gcloud compute firewall-rules update allow-guacamole --source-ranges=<PC_BANG_IP>/32 #(@Cloud Shell)
```
You can confirm it took effect with:

```bash 
gcloud compute firewall-rules describe allow-guacamole --format="value(sourceRanges)" #(@Cloud Shell)
```

3. Open it in the browser
```
http://<PC_BANG_IP>:8080/guacamole
```

 
| Field | Value |
|---|---|
| Protocol | VNC |
| Hostname | `172.17.0.1` (or kaggle-vm's internal IP `10.128.0.x` if that doesn't work) |
| Port | 5901 |
| Password | kaggle1 |
