# Deal Multiple Company Similarity Analysis Tool

A secure web application for analyzing business model similarity between companies using AI-powered comparisons. This tool helps investment professionals identify comparable companies by analyzing business descriptions and rating their similarity on a 1-10 scale.

## 🚀 Features

- **AI-Powered Analysis**: Uses DeepSeek AI to evaluate business model similarity
- **Batch Processing**: Analyze multiple companies from Excel files
- **Interactive Interface**: User-friendly Streamlit web interface
- **Progress Tracking**: Real-time progress updates during processing
- **Export Results**: Download analysis results as CSV
- **Password Protection**: Secure access for team members only
- **Rating Scale**: Clear 1-10 similarity scoring system

## 📊 Rating Scale

| Rating | Description |
|--------|-------------|
| 1-2    | Very similar business models (strong comparables) |
| 3-4    | Similar with some differences |
| 5-6    | Moderately similar |
| 7-8    | Different business models |
| 9-10   | Completely unrelated |

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- DeepSeek API key

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/company-similarity-app.git
   cd company-similarity-app
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```
   API_KEY=your_deepseek_api_key_here
   APP_PASSWORD=your_secure_app_password_here
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. **Push your code to a private GitHub repository**
2. **Go to [share.streamlit.io](https://share.streamlit.io/)**
3. **Connect your GitHub account and select your repository**
4. **Set environment variables in the Streamlit dashboard:**
   - `API_KEY`: Your DeepSeek API key
   - `APP_PASSWORD`: Your chosen app password
5. **Deploy the application**

### Alternative Deployment Options

#### Heroku
```bash
# Install Heroku CLI and run:
heroku create your-app-name
heroku config:set API_KEY=your_api_key_here
heroku config:set APP_PASSWORD=your_password_here
git push heroku main
```

#### Railway
1. Connect your GitHub repository at [railway.app](https://railway.app/)
2. Add environment variables in the Railway dashboard
3. Deploy automatically

## 📁 File Structure

```
company-similarity-app/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (local only)
├── .gitignore           # Git ignore rules
├── README.md            # This file
└── venv/                # Virtual environment (not committed)
```

## 🔒 Security Features

- **Password Protection**: App requires password authentication
- **Environment Variables**: Sensitive data stored securely
- **Private Repository**: Code kept in private GitHub repo
- **No Data Persistence**: No user data stored on servers
- **API Key Protection**: DeepSeek API key never exposed in code

## 📋 Usage Instructions

### Step 1: Access the Application
- Navigate to your deployed app URL
- Enter the provided password to access the tool

### Step 2: Enter Target Company Description
- Provide a detailed description of the target company
- Include business model, industry, and key characteristics
- Click "Submit Description"

### Step 3: Upload Excel File
- Upload an Excel file containing company data
- **Required column**: `Description` (containing company descriptions)
- **File format**: Excel (.xlsx or .xls)
- **Data structure**: 
  - Skip first 6 rows (headers/metadata)
  - Remove last 2 rows (footers)
  - Remove 'Deal ID' column if present

### Step 4: Review Results
- View similarity rankings (1-10 scale)
- Results sorted by similarity (most similar first)
- Download results as CSV for further analysis
- Start over with new analysis if needed

## 📊 Excel File Requirements

Your Excel file should contain:
- A `Description` column with company business descriptions
- Data starting from row 7 (first 6 rows are skipped)
- No critical data in the last 2 rows (they're removed)

Example structure:
```
Row 1-6: Headers/metadata (skipped)
Row 7+:  | Company Name | Description | Other Data |
         | Company A    | Tech startup... | ... |
         | Company B    | Manufacturing... | ... |
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_KEY` | DeepSeek API key | Yes |
| `APP_PASSWORD` | Application access password | Yes |

### API Configuration

- **Provider**: DeepSeek AI
- **Model**: deepseek-chat
- **Base URL**: https://api.deepseek.com
- **Rate Limiting**: Built-in retry mechanism with delays

## 🔧 Troubleshooting

### Common Issues

**"API error" messages**
- Check your DeepSeek API key is valid
- Verify you have sufficient API credits
- Check internet connection

**"Excel file must have a 'Description' column"**
- Ensure your Excel file has a column named exactly "Description"
- Check column headers for extra spaces or special characters

**Password not working**
- Verify APP_PASSWORD environment variable is set correctly
- Check for extra spaces in password
- Contact administrator if password is forgotten

**File upload issues**
- Ensure file is in Excel format (.xlsx or .xls)
- Check file isn't corrupted
- Verify file size is reasonable (< 50MB)

### Getting Help

1. Check the error message displayed in the app
2. Verify all environment variables are set correctly
3. Test with a small sample Excel file first
4. Contact the repository maintainer for technical issues

## 🔄 Updates and Maintenance

### Regular Maintenance Tasks

- **Password Rotation**: Change APP_PASSWORD every 3-6 months
- **API Key Management**: Monitor DeepSeek API usage and costs
- **Dependency Updates**: Keep Python packages updated for security
- **Access Review**: Regularly review who has access to the application

### Updating the Application

1. Pull latest changes from the repository
2. Update dependencies if needed: `pip install -r requirements.txt`
3. Restart the application
4. For cloud deployments, push changes to trigger auto-deployment

## 📝 License

This project is for internal use only. All rights reserved.

## 👥 Support

For technical support or access requests, contact:
- Repository maintainer: [Your contact information]
- IT department: [Department contact]

---

**⚠️ Important Security Notes:**
- Never share your API keys publicly
- Use strong passwords for application access
- Keep the GitHub repository private
- Regularly rotate passwords and API keys
- Monitor API usage for unexpected activity