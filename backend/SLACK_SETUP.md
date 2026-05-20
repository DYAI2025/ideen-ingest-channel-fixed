# Slack Integration Setup Guide

This guide explains how to configure the Slack integration for the Ideen Ingest Channel.

## Prerequisites

1. A Slack Workspace with admin access
2. Slack App created in the workspace (see Sprint 1 US1)

## Configuration Steps

### 1. Get Slack Credentials

From your Slack App configuration (https://api.slack.com/apps):

1. **Signing Secret**: 
   - Go to Basic Information → App Credentials
   - Copy the "Signing Secret"
   
2. **Bot Token**:
   - Go to OAuth & Permissions → Bot Tokens
   - Add scopes: `channels:history`, `channels:join`, `chat:write`, `files:read`
   - Install app to workspace
   - Copy the "Bot User OAuth Token" (starts with `xoxb-`)

3. **App-Level Token** (optional, for Socket Mode):
   - Go to Basic Information → App-Level Tokens
   - Create token with scope `connections:write`
   - Copy the token (starts with `xapp-`)

### 2. Configure Environment Variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and add your Slack credentials:
```bash
SLACK_SIGNING_SECRET=your_signing_secret_here
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_LEVEL_TOKEN=xapp-your-app-level-token-here
```

### 3. Enable Webhooks

In your Slack App configuration:

1. Go to Event Subscriptions
2. Enable Events
3. Set Request URL to: `https://your-domain.com/api/slack/events`
4. Subscribe to bot events:
   - `message.channels`
   - `file_shared`
5. Save changes

### 4. Test the Integration

Start the backend server:
```bash
cd backend
source venv/bin/activate
python -m src.main
```

Slack will send a URL verification challenge to your endpoint. If configured correctly, the challenge will be successful.

## Security Notes

- **Never commit `.env` file** to version control
- **Signing Secret is required** in production mode (app will fail to start without it)
- In development mode, a test secret is used if `SLACK_SIGNING_SECRET` is not set
- All webhook requests are verified using HMAC-SHA256 signature verification
- Timestamp validation prevents replay attacks (5-minute window)

## Troubleshooting

### "SLACK_SIGNING_SECRET must be set in production mode"
Set the `SLACK_SIGNING_SECRET` environment variable or set `DEBUG=True` for development.

### Signature verification failures
- Ensure the signing secret matches exactly (no extra spaces)
- Check that the request URL in Slack App settings matches your deployed endpoint
- Verify system time is synchronized (timestamp validation requires accurate time)

### Events not being received
- Check Event Subscriptions are enabled in Slack App
- Verify the Request URL is accessible from Slack's servers
- Check server logs for incoming webhook requests

## Next Steps

After Sprint 1 completion:
- Implement message persistence to database
- Add file download and storage
- Implement semantic analysis
- Add Obsidian/GBrain synchronization