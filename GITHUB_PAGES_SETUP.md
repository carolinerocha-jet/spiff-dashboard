# GitHub Pages Setup - Step-by-Step Guide

## 🎯 Goal
Set up automated SPIFF dashboard that updates every Monday at a permanent URL.

---

## 📋 Prerequisites

- GitHub account
- Git installed on your computer
- Python 3.8+ installed
- Latest SPIFF ticket export CSV

---

## 🚀 Step 1: Create GitHub Repository

### Option A: Via GitHub Website (Easier)

1. Go to https://github.com/new
2. Repository name: `spiff-dashboard`
3. Description: "Weekly SPIFF ticket dashboard"
4. Choose: **Public** (required for free GitHub Pages)
5. ✅ Check "Add a README file"
6. Click **Create repository**

### Option B: Via Command Line

```bash
# 1. Create local directory
mkdir spiff-dashboard
cd spiff-dashboard

# 2. Initialize git
git init

# 3. Create on GitHub (requires GitHub CLI)
gh repo create spiff-dashboard --public --source=. --remote=origin
```

---

## 📦 Step 2: Add Files to Repository

### Via GitHub Website (Upload Files)

1. Go to your repo: `https://github.com/YOUR-USERNAME/spiff-dashboard`
2. Click **Add file** → **Upload files**
3. Upload these files:
   - `generate_spiff_report.py`
   - `tickets.csv` (your SPIFF export)
   - `spiff_dashboard.html` (generated dashboard)
   - `slack_report.txt` (generated Slack report)
   - `.gitignore`
   - `README.md`
4. Click **Commit changes**

### Via Command Line (Recommended)

```bash
# 1. Navigate to your local directory
cd spiff-dashboard

# 2. Copy all the files you received into this directory:
#    - generate_spiff_report.py
#    - tickets.csv
#    - .gitignore
#    - README.md

# 3. Generate initial dashboard
python generate_spiff_report.py tickets.csv

# 4. Add all files
git add .

# 5. Commit
git commit -m "Initial dashboard setup"

# 6. Add remote (replace YOUR-USERNAME)
git remote add origin https://github.com/YOUR-USERNAME/spiff-dashboard.git

# 7. Push
git push -u origin main
```

---

## 🌐 Step 3: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Click **Pages** in left sidebar
4. Under "Source":
   - Branch: `main`
   - Folder: `/ (root)`
5. Click **Save**

**Your dashboard will be available at:**
```
https://YOUR-USERNAME.github.io/spiff-dashboard/spiff_dashboard.html
```

⏳ *Wait 1-2 minutes for GitHub to build and deploy*

---

## ⚙️ Step 4: Set Up GitHub Actions (Automated Updates)

### 4.1 Add Workflow File

```bash
# Create directory
mkdir -p .github/workflows

# Copy the workflow file
# Place update-dashboard.yml into .github/workflows/

# Or create it directly:
cat > .github/workflows/update-dashboard.yml << 'EOF'
[paste the workflow content here]
EOF
```

### 4.2 Configure Workflow

Edit `.github/workflows/update-dashboard.yml`:

**Option A: Manual CSV Upload (Simplest)**
```yaml
# In the "Download latest SPIFF export" step, just use:
- name: Download latest SPIFF export
  run: |
    echo "Using manually uploaded tickets.csv"
    # File must be committed to repo
```

**Option B: Download from URL**
```yaml
- name: Download latest SPIFF export
  run: |
    curl -o tickets.csv https://your-spiff-url/export
```

**Option C: Use API with Authentication**
```yaml
- name: Download latest SPIFF export
  run: |
    curl -H "Authorization: Bearer ${{ secrets.SPIFF_API_TOKEN }}"          -o tickets.csv https://your-api-url/tickets/export
```

### 4.3 Commit Workflow

```bash
git add .github/workflows/update-dashboard.yml
git commit -m "Add automated update workflow"
git push
```

---

## 🔐 Step 5: Add Secrets (Optional)

If using API authentication or Slack webhooks:

1. Go to repository **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add secrets:
   - Name: `SPIFF_API_TOKEN` → Value: your API token
   - Name: `SLACK_WEBHOOK_URL` → Value: your Slack webhook

---

## ✅ Step 6: Test It Out

### Test Manual Run

1. Go to **Actions** tab in your repo
2. Click **Update SPIFF Dashboard**
3. Click **Run workflow** → **Run workflow**
4. Watch it run (takes ~30 seconds)
5. Check your dashboard URL - should be updated!

### Test Scheduled Run

The workflow runs every Monday at 8 AM UTC automatically.

To test without waiting:
- Change the cron schedule to `*/5 * * * *` (every 5 minutes)
- Push the change
- Wait 5 minutes
- Change it back to `0 8 * * 1`

---

## 📱 Step 7: Share with Team

Send this message to your team:

```
🎯 SPIFF Ticket Dashboard is now live!

📊 Dashboard: https://YOUR-USERNAME.github.io/spiff-dashboard/spiff_dashboard.html

✅ Updates automatically every Monday with last week's data
✅ Interactive charts - hover, zoom, and explore
✅ Works on desktop and mobile

Bookmark it for quick access! 🔖
```

---

## 🔄 Weekly Workflow

### Automated (Recommended)
- **Nothing to do!** GitHub Actions updates everything every Monday.
- Check the Actions tab if you want to see the status.

### Manual (If needed)
```bash
# 1. Get latest CSV from SPIFF
# 2. Save as tickets.csv in repo directory
# 3. Run:
python generate_spiff_report.py tickets.csv
git add spiff_dashboard.html slack_report.txt tickets.csv
git commit -m "Weekly update - $(date +%Y-%m-%d)"
git push
```

The dashboard updates within 1-2 minutes.

---

## 🐛 Troubleshooting

### Dashboard not updating?

1. Check **Actions** tab for errors
2. Verify workflow file is in `.github/workflows/`
3. Make sure repo is public (or have GitHub Pro for private Pages)

### "404 Not Found" error?

1. Verify Pages is enabled in Settings
2. Wait 2-3 minutes after pushing
3. Check the exact URL (case-sensitive!)
4. Try: `https://YOUR-USERNAME.github.io/spiff-dashboard/`

### Workflow not running?

1. Check **.github/workflows/update-dashboard.yml** exists
2. Verify cron syntax is correct
3. Make sure repo has Actions enabled (Settings → Actions)

### Charts not showing?

1. Check browser console for errors
2. Ensure internet connection (needs Plotly CDN)
3. Try clearing cache (Ctrl+Shift+R)

---

## 📊 What Happens Every Monday?

```
8:00 AM UTC - GitHub Actions triggers
  ↓
Downloads/uses tickets.csv
  ↓
Runs generate_spiff_report.py
  ↓
Creates new spiff_dashboard.html & slack_report.txt
  ↓
Commits and pushes to repo
  ↓
GitHub Pages rebuilds (1-2 min)
  ↓
Dashboard updated at same URL! ✅
```

---

## 🎉 You're Done!

Your dashboard is now live and will update automatically every Monday morning.

**Bookmark this:** `https://YOUR-USERNAME.github.io/spiff-dashboard/spiff_dashboard.html`
