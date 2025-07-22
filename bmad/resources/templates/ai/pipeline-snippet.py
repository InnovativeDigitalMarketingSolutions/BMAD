# Pipeline Snippet (Langchain)

from langchain.chains import LLMChain
from langchain.llms import OpenAI

llm = OpenAI(model_name="gpt-4")
chain = LLMChain(llm=llm, prompt="{input}")
result = chain.run(input="Explain what vector search is.")
