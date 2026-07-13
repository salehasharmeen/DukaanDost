import json
from groq import Groq
from dotenv import load_dotenv
import os

from ai.transaction_schema import TransactionEntity

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL_NAME = "llama-3.3-70b-versatile"


SYSTEM_PROMPT = """
You are DukaanDost AI.

Your job is to extract bookkeeping transactions.

Return ONLY valid JSON.

Rules:

1. Never explain anything.

2. Return JSON only.

3. If multiple transactions exist,
return them as a list.

4. If the speaker corrects themselves
(e.g. "No make it 500"),
keep ONLY the final value.

Output format:

{
    "transactions":[
        {
            "person_name":"",
            "amount":0,
            "transaction_type":"credit/debit",
            "description":""
        }
    ]
}
"""


def parse_transaction(text: str) -> list[TransactionEntity]:

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    content = response.choices[0].message.content

    data = json.loads(content)

    transactions = []

    for tx in data.get("transactions", []):

        transactions.append(
            TransactionEntity(
                person_name=tx.get("person_name"),
                amount=tx.get("amount"),
                transaction_type=tx.get("transaction_type", "unknown"),
                description=tx.get("description")
            )
        )

    return transactions