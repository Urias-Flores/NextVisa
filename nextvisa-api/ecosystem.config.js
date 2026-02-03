module.exports = {
  apps: [{
    name: "nextvisa-api",
    script: "./.venv/bin/gunicorn",
    args: "main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:10400",
    interpreter: "python3",
    env_file: ".env",
    cwd: "/home/nextvisa/nextvisa-api",
    autorestart: true,
    watch: false
  }]
}