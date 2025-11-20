# Cypherify - Educational Cryptography Tool

An interactive web application for learning about classical and modern cryptography through hands-on experimentation.

## Features

- 🔐 **11 Cipher Types**: Caesar, Vigenère, Affine, ROT13, AES, RSA, and more
- 🤖 **AI Teacher**: Built-in AI assistant powered by OpenAI
- 🔓 **Auto-Detect**: Automatically identify and decrypt unknown ciphers
- 🔑 **Password Analysis**: Test password and PIN strength with brute force simulations
- 📊 **Visualizations**: Frequency analysis, RSA diagrams, and more
- 📚 **Educational**: Step-by-step explanations for every operation

## Deployment on Render

### Quick Deploy

1. **Fork/Clone this repository**

2. **Create account on Render**: https://render.com

3. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `Cypherify` repository

4. **Configure Service**:
   - **Name**: `cypherify` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:server --bind 0.0.0.0:$PORT`
   - **Instance Type**: Free (or paid for better performance)

5. **Add Environment Variables**:
   - Go to "Environment" tab
   - Add `OPENAI_API_KEY` with your OpenAI API key
   - (Optional for AI Teacher feature)

6. **Deploy**:
   - Click "Create Web Service"
   - Wait 3-5 minutes for build to complete
   - Your app will be live at: `https://cypherify.onrender.com`

### Environment Variables

- `OPENAI_API_KEY` (optional): Your OpenAI API key for AI Teacher feature
  - Get one at: https://platform.openai.com/api-keys
  - Without this, the AI Teacher will be disabled but all ciphers will work

### Local Development

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Cypherify
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

4. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

5. **Run the app**
   ```bash
   python app.py
   ```

6. **Open browser**
   - Navigate to: http://localhost:8050

## Tech Stack

- **Framework**: Dash (Plotly)
- **UI**: Dash Bootstrap Components
- **Cryptography**: PyCryptodome, Python cryptography library
- **AI**: OpenAI GPT-4
- **Deployment**: Gunicorn + Render

## Educational Purpose Only

⚠️ **Warning**: This tool is for educational purposes only. The cipher implementations are simplified for learning and should NOT be used for real-world security applications.

## License

MIT License - Feel free to use for educational purposes.

## Author

Created for educational cryptography learning.
