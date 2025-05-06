# Aircall Missed Calls Monitor 📞📊

A Python script that analyzes missed calls from Aircall API and updates real-time Google Sheets reports to help teams monitor performance and follow up with clients.

![Google Sheets Dashboard Example](https://via.placeholder.com/800x400.png?text=Google+Sheets+Dashboard+Example)

## Key Features ✨
- **Real-time Monitoring**: Pulls call data directly from Aircall API
- **Smart Categorization**: Automatically sorts missed calls by department (Sales, CS, etc.)
- **Time Tracking**: Calculates time since call was missed for prioritization
- **Multi-Sheet Reporting**: Updates multiple Google Sheets tabs simultaneously
- **Secure**: Uses environment variables for credentials management
- **Automated Formatting**: Maintains clean spreadsheet structure with timestamps

## Prerequisites 📋
- Python 3.8+
- [Aircall API Access](https://developer.aircall.io/)
- Google Service Account credentials
- Google Sheet with pre-configured tabs:
  - `missed_all` (All missed calls)
  - `missed_sales` (Sales-related missed calls)
  - `missed_cs` (Customer Service missed calls)
  - `missed_nmc` (NMC department calls)
  - `missed_pro` (Promedia department calls)

## Setup Instructions 🛠️

### 1. Install Requirements
```bash
pip install pandas requests gspread oauth2client python-dotenv


### 2. Configure Environment Variables

Create .env file:

AIR_CALL_API_TOKEN=your_api_token_here
GOOGLE_CREDS_JSON='{"type": "service_account", ...}'  # Full JSON credentials
SHEET_NAME="Call Monitoring Dashboard"


Get Credentials:

Aircall API Token: Aircall Dashboard

Google Credentials: Google Cloud Console

3. Configure Script
python
# In air_call_analysis.py
API_BASE_URL = "https://api.aircall.io/v1/"
DATE_RANGE = {
    "start": datetime(2023, 1, 1),  # Update with your desired start date
    "end": datetime.now()
}
Running the Script ▶️
bash
python air_call_analysis.py
Google Sheets Structure 📑
The script maintains these columns automatically:

Call ID: Unique call identifier

Start Time: When call was initiated (UTC)

Missed Reason: Categorization from Aircall

Phone Numbers: Cleaned format (no spaces/special chars)

Line: Which department/number received call

Duration: Call length in seconds

Tags/Comments: Any metadata from Aircall

Update Time: Last refresh time (auto-updating)

Time Since Missed: Formula column (auto-calculating)

Column Structure

Automation Options 🤖
Set up regular updates with:

cron Job (Linux/Mac):

bash
*/30 * * * * /path/to/python /path/to/air_call_analysis.py
Windows Task Scheduler

GitHub Actions (for cloud-based scheduling)

Notification Setup 🔔
Add these to automatically notify your team:

Email Alerts (Add to script):

python
import smtplib
# Add notification logic when high-priority calls are detected
Slack Integration:

python
slack_webhook_url = os.getenv("SLACK_WEBHOOK")
requests.post(slack_webhook_url, json={"text": "New missed call detected!"})
Troubleshooting 🚨
Issue	Solution
Authentication Errors	Verify JSON credentials format in .env
Empty Sheets	Check API token permissions
Timezone Issues	Add pd.to_datetime(...).dt.tz_localize('UTC')
Rate Limits	Add time.sleep(1) between API calls
Security Best Practices 🔒
Never commit .env files

Use restricted Google API credentials

Regularly rotate API tokens

Store Sheets with view-only access for most users

License 📄
MIT License - Free for personal and commercial use
