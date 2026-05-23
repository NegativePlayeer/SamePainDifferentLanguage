depression_abstracts = get_abstracts("depression", max_results=5)

for i, abstract in enumerate(depression_abstracts):
    print(f"--- Abstract {i + 1} ---")
    print(abstract[:200])
    print()
