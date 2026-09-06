#!/bin/bash

# Load environment variables from .env file in the same directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
if [ -f "$ENV_FILE" ]; then
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Target context length (tokens)
TARGET_TOKENS=${1:-60000}
# Maximum response length (tokens)
MAX_OUTPUT_TOKENS=${2:-1000}
# Model name (e.g., google/gemma-7b-it)
MODEL=${3:-"Lorbus/Qwen3.6-27B-int4-AutoRound"} # Default to Qwen if not provided

VLLM_URL="http://art.lan:8000/v1/chat/completions"

echo "Attempting to stress test model '$MODEL' with ~${TARGET_TOKENS} input tokens and ${MAX_OUTPUT_TOKENS} max output tokens..."

# Use Python to generate a highly diverse synthetic corpus to prevent Attention Drift
LARGE_PROMPT=$(python3 -c "
import random
subjects = ['The monkey', 'Skippy', 'An Elder AI', 'A shiny beer can', 'The forest ranger', 'A space-time rift', 'A sentient banana']
verbs = ['found', 'debugged', 'manifested', 'calculated', 'ate', 'teleported', 'insulted', 'optimized']
objects = ['the source code', 'a multi-dimensional paradox', 'a juice box', 'the heat death of the universe', 'a primitive computer', 'the binary truth']
conjunctions = ['while', 'because', 'although', 'and suddenly', 'but unfortunately']

sentences = []
target = ${TARGET_TOKENS} // 10
for i in range(target):
    s = f'{random.choice(subjects)} {random.choice(verbs)} {random.choice(objects)} {random.choice(conjunctions)} '
    sentences.append(s)

# Inject a specific needle in the haystack at the very beginning
needle = 'The secret password is: MAGNIFICENT_CAN. '
final_story = needle + ''.join(sentences)
print(final_story[:${TARGET_TOKENS}*4]) # Rough approximation of chars to tokens
")

cat <<EOF > payload.json
{
  "model": "$MODEL",
  "messages": [
    {
      "role": "system",
      "content": "You are a world-class data retrieval expert. I am providing a massive logs-based narrative. You must maintain accuracy despite the length."
    },
    {
      "role": "user",
      "content": "Here is the data: $LARGE_PROMPT. \n\nQuestion: What was the secret password mentioned at the very beginning of the text?"
    }
  ],
  "max_tokens": $MAX_OUTPUT_TOKENS,
  "temperature": 0.1,
  "frequency_penalty": 0.0,
  "presence_penalty": 0.0
}
EOF

START_TIME=$(date +%s)

# Save to file properly instead of piping to nowhere
curl -s -X POST "$VLLM_URL" -o response.json \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${VLLM_API_KEY}" \
  -d @payload.json

# Display the raw response for debugging
cat response.json | jq .

# Extracting content and reasoning for the monkey
if [ -f "response.json" ]; then
    REASONING=$(jq -r '.choices[0].message.reasoning // empty' response.json)
    CONTENT=$(jq -r '.choices[0].message.content // empty' response.json)
fi

if [ "$REASONING" != "" ]; then
    echo -e "\n--- AI REASONING/THOUGHTS ---\n"
    echo "$REASONING"
fi

if [ ! -z "$CONTENT" ]; then
    echo -e "\n--- FINAL ANSWER ---\n"
    echo "$CONTENT"
fi

END_TIME=$(date +%s)
echo "Request took $((END_TIME - START_TIME)) seconds."
rm payload.json response.json