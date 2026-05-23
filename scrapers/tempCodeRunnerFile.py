for feature in ["depression", "chronic pain", "neurology brain"]:
    save_to_json(
        get_abstracts(feature, max_results=50),
        f"data/raw/pubmed_{feature.replace(' ', '_')}.json",
    )
