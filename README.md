
# Telegram Cleanup Bot

This Telegram bot is designed to manage group cleanups and provide additional features like generating invite links, tracking user activity, sending daily reports, and allowing admins to manage the group with ease. The bot supports multiple groups and admins, offering various functionalities like removing inactive members, sending daily reports, and much more.

## Features
- **Daily Cleanup**: Automatically removes non-admin members at 12 AM.
- **Join Link**: Sends a unique invite link every day to users with an "Ask Join Link" button.
- **Admin Reports**: Admins can submit daily and weekly reports.
- **Activity Tracking**: Track user activity and group status.
- **Silent Mode**: Option to mute or restrict notifications during cleanup.
- **Whitelist**: Option to add users to the whitelist so they are not removed during cleanup.
- **Rejoin Requests**: Allows users who are removed to request to rejoin.

## Prerequisites
Before you begin, ensure that you have the following installed:

- **Python 3.7 or higher**
- **MongoDB** (for storing group settings, reports, and user activity)
- **Pyrogram** (Telegram Python library)
- **APSs Scheduler** (For scheduling cleanup tasks)

You can install the required Python packages by using `pip`:

```bash
pip install -r requirements.txt
```

### **MongoDB Setup**
Make sure you have a MongoDB database running. The bot will use MongoDB to store various data like reports, user activity, settings, and invite links.

- You can either run MongoDB locally or use a cloud provider (e.g., MongoDB Atlas).
- In the `.env` file, update the `MONGO_URI` to point to your MongoDB instance.

## Configuration
The bot configuration is stored in the `.env` file. Here's a sample configuration:

```plaintext
BOT_TOKEN=your_telegram_bot_token
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
MONGO_URI=your_mongodb_connection_string
```

### **Telegram API Setup**
To use the Telegram bot, you need to obtain an API ID and API hash by following these steps:

1. Go to [Telegram's Developer Site](https://my.telegram.org/auth).
2. Login and click on **API development tools**.
3. Create a new application and note down the **API ID** and **API hash**.

Update these values in the `.env` file.

### **Running the Bot**

1. **Start the bot**:
   After setting up everything, you can start the bot using:

   ```bash
   python bot/main.py
   ```

2. **Web Server (optional)**:
   If you want to run a web server alongside the bot (for metrics or other purposes), make sure to enable the web server in `webserver.py` and run:

   ```bash
   python bot/main.py
   ```

   This will run both the bot and web server concurrently.

---

## How It Works

### **Bot Features**
1. **Admin Functions**:
   - Admins can submit **daily** and **weekly reports**.
   - **Cleanup Mode**: Automatically removes non-admin members daily at 12 AM.
   - Admins can **request join links** and track user activity using a simple command interface.

2. **User Functions**:
   - Users can request their **join link** via the "Ask Join Link" button.
   - The bot tracks when users are **removed** and whether they can **rejoin**.
   
3. **Join Link Management**:
   - The bot generates **daily unique invite links** for the group. The link expires in 24 hours.
   - The **"Ask Join Link"** button allows users to get the current day’s join link.

4. **Activity and Reporting**:
   - The bot saves **activity logs** and **reports** submitted by admins.
   - Admins can view **past reports** using the `/get_reports` command.

5. **Cleanup Reports**:
   - Every night at **12 AM**, the bot generates a report of removed users, and sends a message about the users removed.

---

## How to Use

### **Bot Commands**
Here are the available commands and how to use them:

- **/start**: Start interacting with the bot.
- **/get_reports**: Retrieve and view the last 10 reports for a group.
- **/add_report <report_type> <report_data>**: Add a new report (admin only).
- **/ask_join_link**: Allows a user to receive the daily join link (available with a button).
- **/cleanup_now**: Perform an immediate cleanup of non-admin members (admin only).

### **Admin Panel**
Admin actions are available for managing the group:

- **Add/remove group settings**.
- **Enable/disable cleanup at 12 AM**.
- **Whitelist users** to prevent removal.
- **Review reports** submitted by admins.

### **Buttons in Messages**
- **"Ask Join Link"**: When clicked, users will receive the current day's join link.
- **"Rejoin Request"**: Allows users who have been removed to request to rejoin the group.

---

## Database Schema

### **Reports Collection (`reports`)**
- `group_id`: The ID of the group.
- `admin_id`: The ID of the admin who submitted the report.
- `report_type`: Type of the report (e.g., daily, weekly).
- `report_date`: The date when the report was submitted.
- `report_data`: The actual report content.

### **Settings Collection (`settings`)**
- `group_id`: The ID of the group.
- `welcome_enabled`: Whether the welcome message is enabled.
- `removal_msg_enabled`: Whether the removal message is enabled.
- `rejoin_enabled`: Whether rejoin is enabled.
- `welcome_text`: The welcome message.
- `removal_text`: The removal message.
- `silent_mode`: Whether silent mode is enabled.
- `whitelist`: List of user IDs who are exempt from cleanup.

### **Invite Links Collection (`invites`)**
- `group_id`: The ID of the group.
- `invite_link`: The generated invite link for the group.
- `expire_at`: The expiration time of the invite link.

### **User Activity Collection (`user_activity`)**
- `user_id`: The ID of the user.
- `group_id`: The ID of the group.
- `action`: The action the user took (e.g., "requested join link").
- `timestamp`: The timestamp when the action occurred.

---

## Troubleshooting

- **Bot not responding**: Ensure the bot token and API credentials are correct. Also, check if the bot is added to the group with sufficient permissions.
- **Invite link not working**: Verify that MongoDB is configured correctly and the `invite_link` in the database is valid.
- **Database issues**: Ensure that MongoDB is up and running. Check the database connection string in `.env`.

---

## Contributing

Feel free to contribute to the project. Here are ways you can help:
- Submit bug reports or feature requests.
- Open a pull request with improvements or bug fixes.
- Help write documentation or test new features.

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
