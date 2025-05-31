#!/bin/bash

echo "=== Discord Bot Setup Script ==="

echo "Updating system packages..."
sudo apt update -y

echo "Installing required packages..."
sudo apt install -y git python3 python3-pip python3-venv

if ! command -v git &> /dev/null; then
    echo "Error: Failed to install git."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: Failed to install python3."
    exit 1
fi

echo "Setting up bot directory at /home/..."
sudo mkdir -p /home/
cd /home/

echo "Downloading Discord bot from GitHub..."
if [ -d "contestbot" ]; then
    echo "Directory 'contestbot' already exists. Removing it..."
    sudo rm -rf contestbot
fi

sudo git clone https://github.com/MorrowShore/contestbot.git
if [ $? -ne 0 ]; then
    echo "Error: Failed to clone the repository."
    exit 1
fi

sudo chown -R $USER:$USER /home/
cd contestbot

if [ ! -f ".env" ]; then
    echo ".env file not found. Creating it..."
    cat > .env << EOF
DISCORD_TOKEN="1234"
MONGO_URI="4321"
EOF
    echo ".env file created at: $(pwd)/.env"
    echo ".env file created successfully!"
else
    echo ".env file found at: $(pwd)/.env"
fi

echo ""
echo "=== Environment Configuration ==="
read -p "Enter your Discord token: " discord_token
if [ -z "$discord_token" ]; then
    echo "Error: Discord token cannot be empty."
    exit 1
fi

read -p "Enter your MongoDB URI: " mongo_uri
if [ -z "$mongo_uri" ]; then
    echo "Error: MongoDB URI cannot be empty."
    exit 1
fi

echo "Current .env content before changes:"
echo "--------------------------------"
cat /home/contestbot/.env
echo "--------------------------------"

echo "Updating .env file..."
sed -i "s|DISCORD_TOKEN=\"1234\"|DISCORD_TOKEN=\"$discord_token\"|" .env
sed -i "s|MONGO_URI=\"4321\"|MONGO_URI=\"$mongo_uri\"|" .env

echo "Updated .env content:"
echo "--------------------------------"
cat /home/contestbot/.env
echo "--------------------------------"

echo ".env file updated successfully!"

if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    python3 -m pip install --upgrade pip
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies. Please check requirements.txt"
        exit 1
    fi
else
    echo "No requirements.txt found. Installing common Discord bot dependencies..."
    python3 -m pip install --upgrade pip discord.py pymongo python-dotenv
fi

MAIN_PY_PATH="/home/contestbot/main.py"
if [ ! -f "$MAIN_PY_PATH" ]; then
    echo "Error: main.py not found in the bot directory."
    exit 1
fi

SERVICE_NAME="contestbot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo ""
echo "=== Setting up persistent service ==="
echo "This requires sudo privileges to create a systemd service..."

sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Discord Contest Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/contestbot
ExecStart=/usr/bin/python3 $MAIN_PY_PATH
Restart=always
RestartSec=10
Environment=PYTHONUNBUFFERED=1
Environment=PYTHONPATH=/home/$USER/.local/lib/python3.$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")/site-packages

[Install]
WantedBy=multi-user.target
EOF

if [ $? -eq 0 ]; then
    echo "Systemd service created successfully!"
    
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE_NAME"
    sudo systemctl start "$SERVICE_NAME"
    
    echo ""
    echo "=== Bot Status ==="
    echo "Bot service started and enabled for auto-start on boot!"
    echo ""
    echo "Useful commands:"
    echo "  Check status: sudo systemctl status $SERVICE_NAME"
    echo "  View logs:    sudo journalctl -u $SERVICE_NAME -f"
    echo "  Stop bot:     sudo systemctl stop $SERVICE_NAME"
    echo "  Start bot:    sudo systemctl start $SERVICE_NAME"
    echo "  Restart bot:  sudo systemctl restart $SERVICE_NAME"
    echo ""
    
    sudo systemctl status "$SERVICE_NAME" --no-pager
else
    echo "Failed to create systemd service. Falling back to nohup method..."
    
    echo "Starting bot with nohup..."
    cd /home/contestbot
    nohup python3 main.py > bot.log 2>&1 &
    BOT_PID=$!
    echo "Bot started with PID: $BOT_PID"
    echo "Log file: /home/contestbot/bot.log"
    echo "To stop the bot, run: kill $BOT_PID"
    
    echo $BOT_PID > bot.pid
    echo "PID saved to bot.pid file"
fi

echo ""
echo "=== Setup Complete ==="

echo "Checking if bot is running..."
sleep 3 

if pgrep -f "python3.*main.py" > /dev/null; then
    echo "✅ Contest bot is running successfully!"
    echo "Bot process found: PID $(pgrep -f 'python3.*main.py')"
else
    echo "❌ Warning: Bot process not detected!"
    echo "Checking service status..."
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
    echo ""
    echo "Try these troubleshooting steps:"
    echo "1. Check logs: sudo journalctl -u $SERVICE_NAME -f"
    echo "2. Check .env file: cat /home/contestbot/.env"
    echo "3. Test manually: cd /home/contestbot && python3 main.py"
fi

echo ""

echo "Contest bot should now be running!"
echo "If there's an issue, join Morrow Shore's Discord server here: https://discord.gg/2sbnwze753"