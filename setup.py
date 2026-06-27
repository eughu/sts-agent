from setuptools import find_packages, setup


setup(
    name="sts-agent",
    version="0.1.0",
    description=(
        "A local multi-agent Slay the Spire companion for route, card, combat, "
        "relic, and shop decisions."
    ),
    packages=find_packages(),
    include_package_data=True,
    package_data={"sts_agent": ["web/static/*"]},
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "sts-agent=sts_agent.cli:main",
            "sts-agent-web=sts_agent.web_server:main",
        ]
    },
)
