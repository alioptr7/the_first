from setuptools import setup, find_packages

setup(
    name="response_network",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.109.2",
        "uvicorn>=0.27.1",
        "sqlalchemy>=2.0.27",
        "psycopg[binary]>=3.1.18",
        "asyncpg>=0.30.0",
        "redis>=5.2.1",
        "celery>=5.5.3",
        "pydantic>=2.12.1",
        "pydantic-settings>=2.11.0",
        "python-jose>=3.5.0",
        "python-multipart>=0.0.20",
        "elasticsearch>=8.12.0",
    ],
    python_requires=">=3.11",
)