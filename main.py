import subprocess
from typing import List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from fastapi import Header, Depends
from typing import Optional


app = FastAPI()


API_TOKEN = "secure_api_token"

# Pydantic model for the input
class AWSCommand(BaseModel):
    command: str
    args: List[str]


def verify_token(token: Optional[str] = Header(None, alias="x-api-key")):
    if token is None or token != API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token


@app.post("/run-aws-cli")
def run_aws_cli(command_data: AWSCommand, token: str = Depends(verify_token)):
    try:
        # Construct the AWS CLI command
        cli_command = [command_data.command] + command_data.args

        # Execute the command and capture output
        result = subprocess.run(cli_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Error: {result.stderr}")

        return {"output": result.stdout}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)