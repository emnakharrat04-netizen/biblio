set -e

# ── User-editable configuration ────────────────────────────────
export DB_HOST="${DB_HOST:-localhost}"
export DB_PORT="${DB_PORT:-3306}"
export DB_USER="${DB_USER:-root}"
export DB_PASSWORD="${DB_PASSWORD:-}"
export DB_NAME="${DB_NAME:-bibliotheque}"

export GEMINI_API_KEY="${GEMINI_API_KEY:-AQ.Ab8RN6Kmme-Za3mHcR5hUb153ztJGwxSDIY49XaQqDjklvOpMw}"

# ── Colour helpers ──────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

step()  { echo -e "${CYAN}${BOLD}[•]${RESET} $*"; }
ok()    { echo -e "${GREEN}${BOLD}[✓]${RESET} $*"; }
warn()  { echo -e "${YELLOW}${BOLD}[!]${RESET} $*"; }
error() { echo -e "${RED}${BOLD}[✗]${RESET} $*"; exit 1; }

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── Dependency check ────────────────────────────────────────────
command -v python3 &>/dev/null || error "python3 not found. Install Python 3.10+."
command -v pip3    &>/dev/null || error "pip3 not found."

# ── Install dependencies ────────────────────────────────────────
step "Installing Python dependencies…"
pip3 install -r "$SCRIPT_DIR/requirements.txt" -q
ok "Dependencies ready."

# ── Database import hint ────────────────────────────────────────
warn "Make sure you have already imported schema.sql into MySQL:"
warn "  mysql -u \$DB_USER -p \$DB_NAME < schema.sql"
echo ""

# ── Start backend ───────────────────────────────────────────────
step "Starting FastAPI backend on http://localhost:8000 …"
cd "$SCRIPT_DIR/backend"
python3 main.py &
BACKEND_PID=$!
ok "Backend started (PID $BACKEND_PID)"

# Give the API a moment to bind
sleep 2

# ── Health check ────────────────────────────────────────────────
if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    ok "Backend health check passed."
else
    warn "Backend did not respond yet; the UI will show a connection error."
fi

# ── Start frontend ──────────────────────────────────────────────
step "Launching Tkinter interface…"
cd "$SCRIPT_DIR/frontend"
python3 app.py

# ── Cleanup ─────────────────────────────────────────────────────
step "Shutting down backend (PID $BACKEND_PID)…"
kill "$BACKEND_PID" 2>/dev/null && ok "Backend stopped." || warn "Backend already stopped."
echo -e "${BOLD}Bye! 👋${RESET}"
