
import boto3
import json
from dotenv import load_dotenv
load_dotenv()

import boto3
sts = boto3.client("sts")
print(sts.get_caller_identity())
def call_bedrock_llm(prompt_text):
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",  # or any supported model
        body=json.dumps({
            "prompt": f"\n\nHuman: {prompt_text}\n\nAssistant:",
            "max_tokens_to_sample": 300,
            "temperature": 0.7,
        }),
        contentType="application/json",
        accept="application/json"
    )
    result = json.loads(response["body"].read())
    return result["completion"]

print(call_bedrock_llm('how are you'))
