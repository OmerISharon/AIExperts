import json
import uuid
from openai import OpenAI
from db import get_connection

client = OpenAI()

def embed(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def ingest_rules(path: str):
    conn = get_connection()
    cur = conn.cursor()

    inserted = 0

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            rule = json.loads(line)

            searchable_text = rule.get("searchable_text") or f"""rule_name: {rule['rule_name']}
rule_type: {rule['rule_type']}
keywords: {rule.get('keywords', '')}
rule_text: {rule['rule_text']}""".strip()

            vector = embed(searchable_text)

            cur.execute(
                """
                INSERT INTO prompt_rules
                (id, rule_name, rule_type, keywords, rule_text, searchable_text, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    rule["rule_name"],
                    rule["rule_type"],
                    rule.get("keywords"),
                    rule["rule_text"],
                    searchable_text,
                    vector,
                ),
            )
            inserted += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted {inserted} rules.")

if __name__ == "__main__":
    ingest_rules(fr"data\prompt_rules.jsonl")
