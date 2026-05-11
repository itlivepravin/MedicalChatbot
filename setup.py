from setuptools import setup, find_packages
setup(
    name='MedicalChatbot',
    version='0.1.0',
    author='Pravin Prakash',
    description='A medical chatbot using LangChain and Pinecone',
    author_email="itlivepravin@gmail.com",
    packages=find_packages(),
    install_requires=[
        'langchain==0.3.26',
        'Flask==3.1.1',
        'sentence-transformers==4.1.0',
        'langchain-huggingface==0.1.2',
        'pypdf==5.6.1',
        'python-dotenv==1.1.0',
        'langchain-pinecone==0.2.8',
        'langchain-openai==0.3.24',
        'langchain-community==0.3.26'
    ],
)