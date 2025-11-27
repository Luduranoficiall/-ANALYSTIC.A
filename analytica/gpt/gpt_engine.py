def generate_insights(question):
    from gpt.local_engine import local_llm
    from gpt.cloud_engine import cloud_llm
    try:
        local = local_llm(question)
        if local and len(local) > 30:
            return local + "\n\n(gerado pela IA local)"
    except:
        pass
    return cloud_llm(question) + "\n\n(gerado pela OpenAI)"
