# Tensor Talezz Certificate Verification Portal

A secure web portal built with Flask and Python for verifying certificates issued by Tensor Talezz.

## Features Included
1. **Public Verification Page**: Enter a Certificate ID to verify its authenticity, showing participant details, program name, issue date, and optional GitHub repo link.
2. **Admin Dashboard (`/admin`)**: Secure login with username and password. Features include issuing new certificates, automatic ID generation (`TT-AI-2026-###`), table view of all certificates, and export to CSV.
3. **Database Schema**: Utilizes MongoDB for a flexible and cloud-deployable database containing `certificates` and `admins` collections.
4. **ID Generation Logic**: Generates an auto-incrementing numeric suffix dynamically queried from the database to ensure uniqueness.
5. **QR Integration**: Links to specific certificates are exposed natively. E.g. `/?cert_id=TT-AI-2026-001` auto-fills the verification input.
6. **Design**: Features Blue (`#1E3A8A`), Silver (`#C0C0C0`), and White backgrounds. Uses the `Poppins` font via Google Fonts, and incorporates glassmorphism styling and smooth background blobs for high-quality, vibrant aesthetics.
7. **Security**: Uses `werkzeug.security` for hashing and storing admin passwords safely.

## Setup Instructions

### 1. Prerequisites
- Python 3.8+ installed.
- A running MongoDB instance (local or MongoDB Atlas in the cloud).

### 2. Local Configuration
1. Clone the repository and navigate to its folder.
2. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```
3. Open `.env` and set your `MONGO_URI` and `FLASK_SECRET_KEY`.

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```
- Access the web portal at: `http://127.0.0.1:5000/`
- **Admin Access**: Navigate to `http://127.0.0.1:5000/admin`
  - Default Username: `TT-ADMIN`
  - Default Password: `Sakhii_Aarvi` *(The admin document is auto-initialized on first run)*

## Deployment to Vercel

This repository is pre-configured for serverless deployment on Vercel via [vercel.json](file:///d:/Hacks/TTcert-verify/vercel.json).

### Steps to Deploy:
1. **Install Vercel CLI**:
   ```bash
   npm install -g vercel
   ```
2. **Initialize Deployment**:
   Run `vercel` in the project root:
   ```bash
   vercel
   ```
   Follow the CLI prompts to link and set up your project.
3. **Add Environment Variables**:
   Go to your Vercel Project Dashboard under **Settings > Environment Variables** and add:
   * `MONGO_URI` (Your MongoDB connection string, e.g., MongoDB Atlas SRV URI)
   * `FLASK_SECRET_KEY` (A secure random string for signing sessions)
4. **Deploy to Production**:
   Deploy the live production version:
   ```bash
   vercel --prod
   ```

## Directory Structure
- [app.py](file:///d:/Hacks/TTcert-verify/app.py): Main application logic, MongoDB connection, and routing.
- [vercel.json](file:///d:/Hacks/TTcert-verify/vercel.json): Vercel configuration for Python WSGI routing.
- [templates/](file:///d:/Hacks/TTcert-verify/templates/): Contains HTML templates (`base.html`, `index.html`, `login.html`, `admin.html`).
- [static/](file:///d:/Hacks/TTcert-verify/static/): Contains static CSS assets (`style.css`).
