# Discord Contest Bot


![image](https://github.com/user-attachments/assets/002bfe1e-8248-4c72-b868-22a30555d7b2)

This bot:

1- Announces the beginning of art contest submission.

2- Captures all art sent to the submission channel, resizing them and converting them to WEBP.

3- Sends all submitted art to the art contest voting gallery type channel.

4- Closes submission channel and announces the beginning of voting.

5- Members will vote for their favorite artwork in the voting gallery by upvoting.

6- Bot counts the upvotes by the end of voting period.

7- Bot announces winner.

---

Since this bot was developed with a monthly art contest in mind, the default timing of the bot (adjustible in jobs.py) is as follows:

2 ~ 14 of the month = submission period

17 ~ 23 of the month = voting period

Winner is decided on the the 24th.

---

This bot needs permission integer of 532911877200

So edit your bot link's integer accordingly:

discord.com/oauth2/authorize?client_id=   &permissions=532911877200&integration_type=0&scope=bot+applications.commands

---

1- To set up this bot, first, get a Mongo Database.

You can get a completely free Mongo Database from their official website here:

https://www.mongodb.com/resources/basics/databases/cloud-databases/free-cloud-database


2- After you've made your database, find its connection string / link. You can use this guide:

https://www.mongodb.com/resources/products/fundamentals/mongodb-connection-string


3- Now, SSH to your VPS.

4- To install, run:
```bash
bash <(curl -s https://raw.githubusercontent.com/MorrowShore/ContestBot/main/install.sh)
```

5- It'll ask for your bot token and the MongoDB connection string. Just paste em and you're done. 


To uninstall, run:
```bash
sudo systemctl stop contestbot 2>/dev/null && sudo systemctl disable contestbot 2>/dev/null && sudo rm -f /etc/systemd/system/contestbot.service && sudo systemctl daemon-reload && sudo rm -rf /home/contestbot && pkill -f "python3 main.py" 2>/dev/null; echo "Contest bot uninstalled successfully!"
```

---


Commands:

![image](https://github.com/user-attachments/assets/5eb68b9b-f576-4f06-9786-49742cd8b66c)

