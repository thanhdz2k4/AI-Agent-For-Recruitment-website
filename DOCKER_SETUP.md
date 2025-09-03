# Docker Hub Setup Instructions

## 📋 Required GitHub Secrets

To enable Docker Hub deployment, you need to configure these secrets in your GitHub repository:

### 1. DOCKERHUB_USERNAME
- Your Docker Hub username: `tthanhhh`

### 2. DOCKERHUB_TOKEN
- A Docker Hub access token (NOT your password)

## 🔧 How to Setup GitHub Secrets

### Step 1: Create Docker Hub Access Token
1. Go to [Docker Hub](https://hub.docker.com)
2. Sign in to your account
3. Click on your username → **Account Settings**
4. Go to **Security** tab
5. Click **New Access Token**
6. Give it a name (e.g., "GitHub Actions CI/CD")
7. Select permissions: **Read, Write, Delete**
8. Click **Generate**
9. **Copy the token immediately** (you won't see it again!)

### Step 2: Add Secrets to GitHub Repository
1. Go to your GitHub repository: `https://github.com/thanhdz2k4/AI-Agent-For-Recruitment-website`
2. Click **Settings** tab
3. In the left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret**

Add these two secrets:

**Secret 1:**
- Name: `DOCKERHUB_USERNAME`
- Value: `tthanhhh`

**Secret 2:**
- Name: `DOCKERHUB_TOKEN`
- Value: `[paste your Docker Hub access token here]`

## 🚀 Docker Images Will Be Available At:

After successful CI/CD runs, your Docker images will be pushed to:
- Repository: `tthanhhh/ai_agent_for_recruitment_website`
- Latest: `tthanhhh/ai_agent_for_recruitment_website:latest`
- Branch tags: `tthanhhh/ai_agent_for_recruitment_website:main-<sha>`
- URL: https://hub.docker.com/r/tthanhhh/ai_agent_for_recruitment_website

## 🐳 How to Use the Docker Image

```bash
# Pull and run the latest image
docker pull tthanhhh/ai_agent_for_recruitment_website:latest
docker run -p 5000:5000 tthanhhh/ai_agent_for_recruitment_website:latest

# Or run directly
docker run -p 5000:5000 tthanhhh/ai_agent_for_recruitment_website:latest
```

## 🔒 Security Notes

- **Never commit Docker Hub passwords to git**
- **Use access tokens instead of passwords**
- **Limit token permissions to what's needed**
- **Rotate tokens regularly**
- **Use repository secrets, not environment secrets for this use case**

## ✅ Verification

After setting up the secrets:
1. Push code to the `main` branch
2. Check GitHub Actions tab for the workflow run
3. Verify the Docker build and push steps succeed
4. Check Docker Hub for your new images
