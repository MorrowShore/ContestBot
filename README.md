# Discord Contest Bot


SSH to your VPS

To install, run:

```bash
bash <(curl -s https://raw.githubusercontent.com/MorrowShore/ContestBot/main/install.sh)
```


To uninstall, run:
```bash
sudo systemctl stop contestbot 2>/dev/null && sudo systemctl disable contestbot 2>/dev/null && sudo rm -f /etc/systemd/system/contestbot.service && sudo systemctl daemon-reload && sudo rm -rf /home/contestbot && pkill -f "python3 main.py" 2>/dev/null; echo "Contest bot uninstalled successfully!"
```
