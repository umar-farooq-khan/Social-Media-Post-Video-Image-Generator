import boto3
import json
from botocore.exceptions import NoCredentialsError, ClientError

def call_bedrock_claude(prompt_text):
    try:
        # Initialize the client for Bedrock Runtime
        bedrock = boto3.client(
            "bedrock-runtime",
            region_name="eu-west-1",  # Or your specific region where Claude is available
        )

        # Prepare the payload
        payload = {
            "prompt": f"\n\nHuman: {prompt_text}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.7,
        }

        # Call the Claude model
        response = bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",  # Claude 3 Sonnet
            body=json.dumps(payload),
            contentType="application/json",
            accept="application/json"
        )

        # Parse and return the result
        result = json.loads(response["body"].read())
        return result.get("completion", "No completion returned.")

    except NoCredentialsError:
        return " AWS credentials not found."
    except ClientError as e:
        return f" ClientError: {e}"
    except Exception as e:
        return f" Error: {str(e)}"

# Example usage
if __name__ == "__main__":
    prompt = "Explain quantum computing in simple terms."
    output = call_bedrock_claude(prompt)
    print("Claude's Response:\n", output)
