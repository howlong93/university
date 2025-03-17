import pandas as pd
from google import genai
from google.genai import types
from time import sleep

# Initialize Gemini API client
client = genai.Client(api_key="AIzaSyAGlbTuJ6NlpRtmQvoOEifVgIABHsn6R8s")

# Load datasets
sample_df = pd.read_csv("mmlu_sample.csv")
submit_df = pd.read_csv("mmlu_submit.csv")
output_file = "mmlu_answers_final.csv"

# Function to prepare few-shot examples for a specific category
def prepare_few_shot(category_df, limit = 3):
    examples = ""
    limited_df = category_df.sample(n=min(limit, len(category_df)), random_state=42)
    for _, row in limited_df.iterrows():
        examples += (
            f"Question:\n"
            f"{row['input']}\n"
            f"A. {row['A']}\n"
            f"B. {row['B']}\n"
            f"C. {row['C']}\n"
            f"D. {row['D']}\n"
            f"Answer: {row['target']}\n\n"
        )
    return examples

# Function to get answer for a question
def Gem_model (contents = '', model='gemini-2.0-flash', temperature=0.1):
    return client.models.generate_content(
        model=model,
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=temperature,
        )
    )

def get_answer(row, few_shot_examples, temperature=0.1):
    prompt = (
        "Examples: \n\n"
        f"{few_shot_examples}"
        "\nNow solve the following question,"
        " output a single line with the choice you choose,"
        " show only A/B/C/D\n"
        f"Question:\n"
        f"{row['input']}\n"
        f"A. {row['A']}\n"
        f"B. {row['B']}\n"
        f"C. {row['C']}\n"
        f"D. {row['D']}\n"
        "Answer:"
    )

    print('prompt sent, waiting response')
    response = Gem_model(contents=prompt)

    print("response received")
    answer = response.text.strip().upper()
    print("formatting response")

    print(answer)

    return answer

# Result list to store answers

# Process each category separately
cnt = 0
for category in submit_df['task'].unique():
    print(f"Processing category: {category}")

    # Few-shot examples for the current category
    few_shot_df = sample_df[sample_df['task'] == category]
    few_shot_examples = prepare_few_shot(few_shot_df)

    # Filter submit questions for the current category
    category_submit_df = submit_df[submit_df['task'] == category]

    print("prepare to send request")
    results = []

    for _, row in category_submit_df.iterrows():
        cnt = cnt+1
        print (f"Doing question {cnt}")

        answer = get_answer(row, few_shot_examples, temperature=0.1)
        sleep(1)

    results.append({'ID': row['Unnamed: 0'], 'target': answer})
    pd.DataFrame(results).to_csv(output_file, mode='a', index=False, header=False)

    print(f"Finished and saved category: {category}")

print("Answers have been saved to mmlu_answers.csv")