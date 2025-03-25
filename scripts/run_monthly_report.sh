#!/bin/bash
# Script to run the SMTP2GO monthly usage reporter
# Intended to be executed by cron at the beginning of each month

# Define the project base path
PROJECT_PATH="/home/boz/Applications/smtp2go-usage"
LOG_FILE=~/smtp2go-cron.log

# Function to log and display a message
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" | tee -a $LOG_FILE
}

# Start fresh log for this run
echo "=== SMTP2GO Usage Reporter Started $(date '+%Y-%m-%d %H:%M:%S') ===" > $LOG_FILE

# Dump system information for debugging
log "Script started"
log "Current working directory: $(pwd)"
log "Running as user: $(whoami)"
log "System Python: $(which python 2>/dev/null || echo 'Python not in PATH')"
log "System Python version: $(python --version 2>&1 || echo 'Could not determine')"
log "PROJECT_PATH: $PROJECT_PATH"

# Check if PROJECT_PATH exists
if [ ! -d "$PROJECT_PATH" ]; then
    log "ERROR: Project directory $PROJECT_PATH does not exist!"
    exit 1
fi

# Create env directory if it doesn't exist
ENV_DIR=~/.smtp2go-usage
ENV_FILE=$ENV_DIR/env
if [ ! -d "$ENV_DIR" ]; then
    log "Creating config directory at $ENV_DIR"
    mkdir -p "$ENV_DIR"
fi

# List contents of the project directory
log "Contents of project directory:"
ls -la "$PROJECT_PATH" | tee -a $LOG_FILE

# Look for virtual environment in different possible locations
VENV_PATHS=(
    "$PROJECT_PATH/bin/activate"
    "$PROJECT_PATH/venv/bin/activate"
    "$PROJECT_PATH/.venv/bin/activate"
)

VENV_ACTIVATED=false
for venv_path in "${VENV_PATHS[@]}"; do
    if [ -f "$venv_path" ]; then
        log "Found virtual environment at: $venv_path"
        log "Activating virtual environment..."
        
        source "$venv_path"
        if [ $? -ne 0 ]; then
            log "ERROR: Failed to activate virtual environment at $venv_path"
            continue
        fi
        
        # Check if virtual environment was properly activated
        if [ -z "$VIRTUAL_ENV" ]; then
            log "ERROR: Virtual environment not properly activated. VIRTUAL_ENV variable is not set."
            continue
        else
            log "Virtual environment activated successfully at: $VIRTUAL_ENV"
            VENV_ACTIVATED=true
            break
        fi
    fi
done

if [ "$VENV_ACTIVATED" = false ]; then
    log "WARNING: Could not find or activate any virtual environment"
    log "Will try to continue with system Python, but this may fail"
fi

# Check Python environment after activation
log "Current Python: $(which python 2>/dev/null || echo 'Not found')"
log "Python version: $(python --version 2>&1 || echo 'Could not determine')"
log "Python executable path: $(which python)"

# Check for installed packages
log "Checking for required Python packages:"
python -m pip freeze | grep -E 'requests|matplotlib|pandas|numpy' | tee -a $LOG_FILE

# Load environment variables if available
if [ -f "$ENV_FILE" ]; then
    log "Loading environment variables from $ENV_FILE"
    
    # Check for JSON format
    if grep -q "api_key" "$ENV_FILE" || grep -q "{" "$ENV_FILE"; then
        log "ERROR: Your env file appears to be in JSON format!"
        log "Please update $ENV_FILE to use shell variable format with 'export VAR=value' syntax"
        log "Example:"
        log "export SMTP2GO_API_KEY=\"your-api-key\""
        log "export SMTP2GO_SMTP_USERNAME=\"your-username\""
        log "See env.sample for the correct format"
        exit 1
    fi
    
    source "$ENV_FILE"
    
    # List loaded environment variables (without values for security)
    log "Environment variables loaded. Available SMTP2GO variables:"
    env | grep SMTP2GO_ | cut -d= -f1 | while read var; do
        log "  - $var is set"
    done
else
    log "No environment file found at $ENV_FILE"
    
    # Check if env.sample exists and offer to copy it
    if [ -f "$PROJECT_PATH/env.sample" ]; then
        log "Found env.sample template in project directory"
        log "Copying env.sample to $ENV_FILE for you to edit"
        cp "$PROJECT_PATH/env.sample" "$ENV_FILE"
        log "Please edit $ENV_FILE to add your configuration and run the script again"
        log "IMPORTANT: Make sure to use shell variable format with 'export VAR=value' syntax"
        exit 1
    else
        log "Checking if required environment variables are already set in shell:"
        for var in SMTP2GO_API_KEY SMTP2GO_SMTP_USERNAME SMTP2GO_SMTP_PASSWORD SMTP2GO_SENDER_EMAIL; do
            if [ -z "${!var}" ]; then
                log "  - WARNING: $var is NOT set"
            else
                log "  - $var is set"
            fi
        done
    fi
fi

# Check if smtp2go_usage module is available
log "Checking if smtp2go_usage module is available"
if python -c "import smtp2go_usage" 2>/dev/null; then
    log "smtp2go_usage module is available in the current Python environment"
else
    log "WARNING: smtp2go_usage module is not available in the current Python environment"
    log "This might indicate a problem with the installation or virtual environment"
    
    # Check if the module exists in the project directory
    if [ -d "$PROJECT_PATH/smtp2go_usage" ]; then
        log "Found smtp2go_usage directory in the project"
        log "Contents of smtp2go_usage directory:"
        ls -la "$PROJECT_PATH/smtp2go_usage" | tee -a $LOG_FILE
    else
        log "ERROR: Could not find smtp2go_usage directory in the project"
    fi
fi

# Try all possible ways to run the application
if command -v smtp2go-usage &> /dev/null; then
    # If installed via pip in the virtual environment
    log "Found smtp2go-usage command at: $(which smtp2go-usage)"
    log "Running smtp2go-usage command..."
    
    # Run with full output capture
    smtp2go-usage 2>&1 | tee -a $LOG_FILE
    exit_code=${PIPESTATUS[0]}
    log "Command completed with exit code: $exit_code"
    
elif [ -f "$PROJECT_PATH/smtp2go_usage/main.py" ]; then
    # Run directly from source
    log "Running from source using main.py at $PROJECT_PATH/smtp2go_usage/main.py"
    
    # Check if the file is executable
    if [ -x "$PROJECT_PATH/smtp2go_usage/main.py" ]; then
        log "main.py is executable, running directly"
        "$PROJECT_PATH/smtp2go_usage/main.py" 2>&1 | tee -a $LOG_FILE
        exit_code=${PIPESTATUS[0]}
    else
        log "main.py is not executable, running with python"
        python "$PROJECT_PATH/smtp2go_usage/main.py" 2>&1 | tee -a $LOG_FILE
        exit_code=${PIPESTATUS[0]}
    fi
    
    log "Script completed with exit code: $exit_code"
    
else
    log "ERROR: Could not find the smtp2go-usage executable or main.py script."
    log "Searched for:"
    log "  - Command 'smtp2go-usage' in PATH: $(which smtp2go-usage 2>&1)"
    log "  - Python script at $PROJECT_PATH/smtp2go_usage/main.py"
    exit_code=1
fi

# Perform additional checks if the command failed
if [ $exit_code -ne 0 ]; then
    log "ERROR: Command failed with exit code $exit_code"
    log "Checking for common issues:"
    
    # Check Python dependencies
    log "Checking Python dependencies..."
    python -m pip list | grep -E 'requests|matplotlib|pandas|numpy' | tee -a $LOG_FILE
    
    # Check if main.py exists and is readable
    if [ -f "$PROJECT_PATH/smtp2go_usage/main.py" ]; then
        log "main.py exists and is readable"
        if [ -x "$PROJECT_PATH/smtp2go_usage/main.py" ]; then
            log "main.py is executable"
        else
            log "main.py is not executable"
        fi
    else
        log "main.py does not exist or is not readable"
    fi
fi

# Deactivate the virtual environment if it was activated
if [ "$VENV_ACTIVATED" = true ] && type deactivate &> /dev/null; then
    log "Deactivating virtual environment"
    deactivate
    log "Virtual environment deactivated"
fi

log "Script finished with exit code: $exit_code"
log "=== SMTP2GO Usage Reporter Completed $(date '+%Y-%m-%d %H:%M:%S') ==="

# Exit with the reporter's exit code
exit $exit_code