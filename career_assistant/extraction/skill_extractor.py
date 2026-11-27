
import re


SKILL_TAXONOMY = {
    # Programming languages
    "Python": ["python"],
    "SQL": ["sql", "structured query language"],
    "Java": ["java"],
    "C++": ["c++"],
    "C#": ["c sharp"],
    "JavaScript": ["javascript", "java script", "js"],
    "TypeScript": ["typescript", "type script"],
    "PHP": ["php"],
    "Ruby": ["ruby"],
    "Swift": ["swift"],
    "Kotlin": ["kotlin"],
    "Scala": ["scala"],
    "Bash": ["bash", "shell scripting"],
    "PowerShell": ["powershell"],

    # Web development
    "HTML": ["html", "hypertext markup language"],
    "CSS": ["css", "cascading style sheets"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular", "angular.js"],
    "Vue.js": ["vue.js", "vuejs"],
    "Node.js": ["node.js", "nodejs"],
    "ASP.NET Core": ["asp.net core", "aspnet core"],
    "Spring Boot": ["spring boot"],
    "FastAPI": ["fastapi"],
    "Flask": ["flask"],
    "Django": ["django"],
    "REST API": [
        "rest api",
        "rest apis",
        "restful api",
        "restful apis",
        "restful services"
    ],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "micro-services"],

    # Databases
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "Microsoft SQL Server": ["sql server", "microsoft sql server"],
    "Oracle Database": ["oracle database", "oracle db"],
    "MongoDB": ["mongodb", "mongo db"],
    "Redis": ["redis"],
    "Elasticsearch": ["elasticsearch"],
    "Cassandra": ["cassandra"],
    "Neo4j": ["neo4j"],
    "PostGIS": ["postgis"],

    # Data Science and Machine Learning
    "Data Science": ["data science", "data scientist"],
    "Data Analysis": ["data analysis", "data analytics"],
    "Data Engineering": ["data engineering", "data engineer"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "Supervised Learning": ["supervised learning"],
    "Unsupervised Learning": ["unsupervised learning"],
    "Reinforcement Learning": ["reinforcement learning"],
    "Natural Language Processing": [
        "natural language processing",
        "nlp"
    ],
    "Computer Vision": ["computer vision"],
    "Statistics": ["statistics", "statistical analysis"],
    "Scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "Keras": ["keras"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Matplotlib": ["matplotlib"],
    "Seaborn": ["seaborn"],
    "XGBoost": ["xgboost"],
    "OpenCV": ["opencv", "open cv"],

    # Generative AI and LLM
    "Artificial Intelligence": ["artificial intelligence", "ai"],
    "LLM": [
        "large language model",
        "large language models",
        "llm",
        "llms"
    ],
    "Generative AI": ["generative ai", "genai", "gen ai"],
    "RAG": [
        "retrieval augmented generation",
        "retrieval-augmented generation",
        "rag"
    ],
    "LangChain": ["langchain"],
    "LlamaIndex": ["llamaindex", "llama index"],
    "Hugging Face": ["hugging face", "huggingface"],
    "Transformers": ["transformers"],
    "Vector Database": [
        "vector database",
        "vector databases",
        "vector db",
        "vector store"
    ],
    "Embeddings": ["embeddings", "embedding models"],
    "Prompt Engineering": ["prompt engineering"],
    "Fine-tuning": ["fine-tuning", "fine tuning", "finetuning"],
    "Ollama": ["ollama"],
    "OpenAI API": ["openai api"],

    # Big Data and Data Engineering
    "ETL": ["etl", "extract transform load"],
    "ELT": ["elt", "extract load transform"],
    "Apache Spark": ["apache spark", "pyspark", "spark"],
    "Hadoop": ["hadoop"],
    "Apache Kafka": ["apache kafka", "kafka"],
    "Apache Airflow": ["apache airflow", "airflow"],
    "dbt": ["dbt", "data build tool"],
    "Snowflake": ["snowflake"],
    "Databricks": ["databricks"],
    "Data Warehouse": ["data warehouse", "data warehousing"],
    "Data Lake": ["data lake", "data lakes"],
    "Apache Flink": ["apache flink", "flink"],

    # Cloud and DevOps
    "AWS": ["amazon web services", "aws"],
    "Azure": ["microsoft azure", "azure"],
    "Google Cloud": ["google cloud", "gcp"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "Jenkins": ["jenkins"],
    "Git": ["git", "github"],
    "GitLab": ["gitlab"],
    "CI/CD": ["ci/cd", "continuous integration", "continuous delivery"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
    "Linux": ["linux"],
    "Nginx": ["nginx"],

    # BI and Visualization
    "Power BI": ["power bi", "powerbi"],
    "Tableau": ["tableau"],
    "Excel": ["excel", "microsoft excel"],
    "Looker": ["looker"],
    "Qlik Sense": ["qlik sense"],

    # GIS
    "QGIS": ["qgis"],
    "ArcGIS": ["arcgis", "arcgis pro"],
    "Geographic Information Systems": [
        "geographic information systems",
        "geographical information systems",
        "gis"
    ],

    # Software engineering and testing
    "Software Engineering": ["software engineering"],
    "Object-Oriented Programming": [
        "object-oriented programming",
        "object oriented programming",
        "oop"
    ],
    "Unit Testing": ["unit testing", "unit tests"],
    "Integration Testing": ["integration testing"],
    "Pytest": ["pytest"],
    "JUnit": ["junit"],
    "Selenium": ["selenium"],
    "JMeter": ["jmeter", "apache jmeter"],
    "Agile": ["agile", "agile methodology"],
    "Scrum": ["scrum"],
}


class SkillExtractor:
    """
    Extract technical skills from text using a predefined taxonomy.

    Output format remains compatible with the existing application:
    [
        {
            "skill": "Python",
            "occurrences": 2,
            "evidence": ["..."]
        }
    ]
    """

    @staticmethod
    def _build_pattern(alias: str) -> re.Pattern:
        """
        Build a case-insensitive regex with word boundaries.
        Spaces in aliases can match one or more whitespace characters.
        """
        escaped_alias = re.escape(alias.strip())
        escaped_alias = escaped_alias.replace(r"\ ", r"\s+")

        return re.compile(
            r"(?<!\w)" + escaped_alias + r"(?!\w)",
            flags=re.IGNORECASE
        )

    @classmethod
    def extract(cls, text: str) -> list[dict]:
        if not isinstance(text, str) or not text.strip():
            return []

        detected_skills = []

        for skill, aliases in SKILL_TAXONOMY.items():
            matches = {}

            for alias in aliases:
                pattern = cls._build_pattern(alias)

                for match in pattern.finditer(text):
                    # Use positions to avoid counting the same
                    # occurrence twice through overlapping aliases.
                    matches[(match.start(), match.end())] = match.span()

            if not matches:
                continue

            sorted_matches = sorted(matches.values())
            evidence = []

            for start, end in sorted_matches:
                snippet_start = max(0, start - 60)
                snippet_end = min(len(text), end + 60)

                snippet = re.sub(
                    r"\s+",
                    " ",
                    text[snippet_start:snippet_end]
                ).strip()

                if snippet and snippet not in evidence:
                    evidence.append(snippet)

                if len(evidence) >= 3:
                    break

            detected_skills.append({
                "skill": skill,
                "occurrences": len(sorted_matches),
                "evidence": evidence
            })

        return detected_skills
