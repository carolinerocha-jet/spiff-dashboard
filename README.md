# SPIFF Ticket Dashboard

📊 **Live Dashboard:** [View Dashboard](https://YOUR-ORG.github.io/spiff-dashboard/spiff_dashboard.html)

> **Note:** Replace `YOUR-ORG` with your actual GitHub organization/username

---

## 📈 What This Dashboard Shows

- **Last Week's Metrics:** Ticket volume and average SLA
- **This Quarter's Performance:** Cumulative stats
- **Weekly Trends:** Last 6 weeks of ticket volume and SLA
- **Team Performance:** Top 8 ticket handlers (last 3 months)
- **Status Overview:** Current ticket status distribution

---

## 🔄 Update Schedule

The dashboard automatically updates **every Monday at 8:00 AM UTC** with the previous week's data.

You can also trigger a manual update:
1. Go to the **Actions** tab
2. Select **Update SPIFF Dashboard**
3. Click **Run workflow**

---

## 📱 Slack Report

Every week, a Slack-formatted report is also generated in `slack_report.txt`.

To automatically post to Slack:
1. Create a Slack webhook URL
2. Add it as a repository secret: `SLACK_WEBHOOK_URL`
3. Uncomment the Slack notification step in `.github/workflows/update-dashboard.yml`

---

## 🛠️ Manual Update

If you need to update the dashboard manually:

```bash
# 1. Export tickets from SPIFF system to tickets.csv
# 2. Run the generator
python generate_spiff_report.py tickets.csv

# 3. Commit and push
git add spiff_dashboard.html slack_report.txt
git commit -m "Manual update"
git push
```

---

## 📂 Repository Structure

```
spiff-dashboard/
├── .github/
│   └── workflows/
│       └── update-dashboard.yml    # Automated update workflow
├── spiff_dashboard.html            # Main interactive dashboard
├── slack_report.txt                # Slack message for the week
├── generate_spiff_report.py        # Dashboard generator script
├── tickets.csv                     # Latest SPIFF export (update weekly)
└── README.md                       # This file
```

---

## 🔐 Security Notes

- The dashboard is **publicly accessible** via the GitHub Pages URL
- To restrict access, consider:
  - Using a private repo with authenticated access
  - Moving to internal hosting
  - Removing sensitive data before publishing

---

## 📞 Support

For issues or questions:
1. Check the **Actions** tab for build logs
2. Review `generate_spiff_report.py` error messages
3. Verify `tickets.csv` format matches expected structure

---

## 📊 Quick Links

- 🌐 [Live Dashboard](https://YOUR-ORG.github.io/spiff-dashboard/spiff_dashboard.html)
- 📈 [GitHub Actions](../../actions)
- ⚙️ [Workflow Configuration](.github/workflows/update-dashboard.yml)

---

**Last Updated:** Automatically via GitHub Actions
