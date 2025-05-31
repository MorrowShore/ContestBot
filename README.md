# Discord Contest Bot



---

This bot needs permission integer of 532911877200

So edit your bot link's integer:

discord.com/oauth2/authorize?client_id=123123123123123123123&permissions=532911877200&integration_type=0&scope=bot+applications.commands

---

To install, first, SSH to your VPS.

run:
```bash
bash <(curl -s https://raw.githubusercontent.com/MorrowShore/ContestBot/main/install.sh)
```

To uninstall, run:
```bash
sudo systemctl stop contestbot 2>/dev/null && sudo systemctl disable contestbot 2>/dev/null && sudo rm -f /etc/systemd/system/contestbot.service && sudo systemctl daemon-reload && sudo rm -rf /home/contestbot && pkill -f "python3 main.py" 2>/dev/null; echo "Contest bot uninstalled successfully!"
```