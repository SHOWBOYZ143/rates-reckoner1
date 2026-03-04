# 📊 Rates Reckoner - Gazetted Rates Calculator

A Streamlit-based application for managing and calculating gazetted rates with Supabase database integration. Perfect for healthcare, hospitality, and service-based organizations.

## ✨ Features

- 🧮 **Rate Calculator** - Calculate total amounts based on rates and quantities
- 📊 **Data Management** - View all rates in organized, filterable tables
- ➕ **Rate Management** - Add single rates or bulk upload from CSV
- ⚙️ **Admin Panel** - Update rates, track audit history, view database statistics
- 💾 **Database Integration** - Powered by Supabase (PostgreSQL)
- 📝 **Audit Trail** - Track all changes with timestamps and user info
- 📥 **Export** - Download data as CSV or Excel
- 🔐 **Secure** - Password-protected admin panel

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Supabase account (free tier available at https://supabase.com)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/SHOWBOYZ143/rates-reckoner.git
   cd rates-reckoner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your Supabase credentials

5. **Create Supabase tables**
   - Go to Supabase Dashboard → SQL Editor
   - Create new query
   - Copy content from `database_schema.sql`
   - Execute

6. **Run the app**
   ```bash
   streamlit run app.py
   ```

The app will open in your browser at `http://localhost:8501`

## 📋 Setup Instructions

### Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com)
2. Sign up / Log in
3. Create new project
   - Project name: `rates-reckoner`
   - Choose region closest to you
   - Set database password
4. Wait for project to be ready (2-3 minutes)

### Step 2: Get Your API Keys

1. Go to **Settings** → **API**
2. Copy:
   - **Project URL** (looks like: `https://xxxxx.supabase.co`)
   - **Anon Public Key** (looks like: `eyJhbGc...`)

### Step 3: Configure Environment

1. Open `.env` file
2. Replace placeholders:
   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-public-key
   ADMIN_PASSWORD=your-secure-password
   ```

### Step 4: Create Database Tables

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **New Query**
3. Copy entire content from `database_schema.sql`
4. Click **Run**
5. You should see success message ✅

### Step 5: Test Connection

Create `test_connection.py`:
```python
from dotenv import load_dotenv
from supabase_client import SupabaseRatesClient

load_dotenv()

try:
    db = SupabaseRatesClient()
    print("✅ Connected to Supabase!")
    years = db.get_all_years()
    print(f"Years: {years}")
except Exception as e:
    print(f"❌ Error: {e}")
```

Run:
```bash
python test_connection.py
```

## 📖 Usage

### Calculator Page
1. Select year from dropdown
2. Choose service category
3. Select specific service
4. Enter quantity
5. View calculated total amount

### View Data Page
1. Select year
2. View all rates in table
3. Filter by category or type
4. Download as CSV or Excel

### Manage Rates Page

**Add Single Rate:**
1. Fill in rate details
2. Click "Add Rate"
3. Rate is added to database

**Bulk Upload:**
1. Prepare CSV file with columns: `service_category`, `service_name`, `amount`, `unit`, `remarks`
2. Upload file
3. Select year and rate type
4. Click "Upload Rates"

### Admin Panel (Password Required)
1. Enter admin password
2. **Update Rate Tab** - Modify existing rates
3. **Audit Log Tab** - View change history
4. **Database Stats Tab** - View statistics

## 📊 CSV Format

For bulk upload, CSV should have these columns:
```
service_category,service_name,amount,unit,remarks
Healthcare,General Consultation,500.00,per visit,Standard fee
```

## 🔧 File Structure

```
rates-reckoner/
├── app.py                  # Main Streamlit application
├── supabase_client.py      # Database client module
├── requirements.txt        # Python dependencies
├── database_schema.sql     # Database schema
├── sample_rates.csv        # Sample data
├── .env.example            # Environment template
├── .env                    # (Local only) Your credentials
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## 🔑 Environment Variables

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase anon public key |
| `ADMIN_PASSWORD` | Password for admin panel |

## 🚨 Security Notes

- ⚠️ **Never commit `.env` file** - it contains secrets
- ✅ Use `.env.example` as template
- ✅ Keep `ADMIN_PASSWORD` strong
- ✅ Use Supabase's Row Level Security (RLS) in production

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'supabase'"
```bash
pip install supabase python-dotenv
```

### "SUPABASE_URL and SUPABASE_KEY must be set"
1. Check `.env` file exists
2. Check values are correct
3. Restart Streamlit app

### Connection timeout
1. Check internet connection
2. Verify Supabase project is running
3. Check URL is correct

### "Access denied" error
1. Verify SUPABASE_KEY is correct
2. Copy it again from Supabase dashboard
3. Make sure you copied the entire key

## 📈 Features Roadmap

- [ ] User authentication
- [ ] Multi-user support
- [ ] Rate comparison reports
- [ ] Automatic rate escalation
- [ ] Email notifications
- [ ] Mobile app version

## 📝 License

This project is open source and available under the MIT License.

## 👥 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on GitHub.

---

**Made with ❤️ using Streamlit & Supabase**
