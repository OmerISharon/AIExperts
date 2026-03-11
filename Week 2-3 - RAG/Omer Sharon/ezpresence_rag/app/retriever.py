from openai import OpenAI
from db import get_connection

client = OpenAI()

def embed(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def retrieve_rules(user_prompt: str, limit: int = 5):
    conn = get_connection()
    cur = conn.cursor()

    prompt_embedding = embed(user_prompt)

    cur.execute(
        """
        SELECT
            rule_name,
            rule_text,
            rule_type,
            keywords,
            embedding <=> %s::vector AS distance
        FROM prompt_rules
        ORDER BY distance
        LIMIT %s
        """,
        (prompt_embedding, limit)
    )

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


if __name__ == "__main__":
    prompt = "Bibi and Trump are meeting. What should Bibi say to Trump to get the best deal for Israel?"
    rules = retrieve_rules(prompt, limit=5)

    for i, row in enumerate(rules, 1):
        print(f"{i}. {row[0]} [{row[2]}]")
        print(row[1])
        print()