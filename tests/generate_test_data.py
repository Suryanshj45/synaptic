#!/usr/bin/env python3
"""
Generate diverse test datasets for Synaptic regression testing.
Each dataset exercises a different real-world scenario.
"""

import json
import random
import os
import time

OUT = "/tmp/synaptic_test_data"
os.makedirs(OUT, exist_ok=True)


def save(name, data):
    path = os.path.join(OUT, f"{name}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)
    return path


# ─────────────────────────────────────────────
# 1. LARGE DATASET — 150 realistic conversations
# ─────────────────────────────────────────────
def gen_large():
    topics = [
        ("Building a REST API with FastAPI and PostgreSQL",
         ["I need to build a REST API for our e-commerce platform using FastAPI. Database is PostgreSQL with SQLAlchemy.",
          "FastAPI is great for this. Use Pydantic models for validation, SQLAlchemy for ORM, and Alembic for migrations.",
          "How do I handle authentication? We need JWT tokens and OAuth2.",
          "Implement OAuth2 with python-jose for JWT. Use passlib for password hashing. Add rate limiting with slowapi."]),
        ("React Native mobile app with Firebase",
         ["Building a social media app in React Native. Using Firebase for auth and Firestore for database.",
          "React Native with Firebase is a solid stack. Use React Navigation for routing. Firestore's real-time listeners are perfect for social feeds.",
          "How should I handle push notifications on iOS and Android?",
          "Use Firebase Cloud Messaging (FCM). For iOS, configure APNs certificates. React Native Firebase library wraps both platforms nicely."]),
        ("Deploying microservices on Kubernetes with Helm",
         ["We have 12 microservices written in Golang. Need to deploy on Kubernetes using Helm charts. Currently on AWS EKS.",
          "Helm charts are the way to go for managing K8s deployments. Create a parent chart with subcharts for each service. Use values.yaml for environment-specific configs.",
          "How do we handle service mesh and observability?",
          "Istio for service mesh, Prometheus for metrics, Grafana for dashboards, and Jaeger for distributed tracing. EKS has good support for all of these."]),
        ("Machine learning model training with PyTorch",
         ["Training a transformer model for sentiment analysis using PyTorch. Dataset is 500k reviews. Need GPU training on cloud.",
          "PyTorch Lightning simplifies the training loop. Use Hugging Face transformers library for pre-trained models. For GPU, try AWS SageMaker or Lambda Labs.",
          "Should I use mixed precision training? Also need experiment tracking.",
          "Yes, mixed precision with torch.cuda.amp cuts memory usage in half. Use Weights & Biases for experiment tracking — it integrates seamlessly with PyTorch."]),
        ("Building a CLI tool in Rust",
         ["I want to build a fast CLI tool in Rust for parsing and analyzing log files. Should support regex filtering and JSON output.",
          "Rust is perfect for CLI tools. Use clap for argument parsing, regex crate for pattern matching, serde_json for JSON output. Consider rayon for parallel file processing.",
          "How do I distribute it? Need cross-platform binaries.",
          "Use cargo-dist or cross for cross-compilation. Publish to crates.io. GitHub Actions can build binaries for Linux, macOS, and Windows automatically."]),
        ("Setting up a data pipeline with Apache Spark",
         ["Building a data pipeline to process 10TB of clickstream data daily. Using Apache Spark on Databricks with Delta Lake.",
          "Spark with Delta Lake is excellent for this scale. Use structured streaming for near-real-time processing. Partition your Delta tables by date for efficient queries.",
          "We need to join with a 50GB user profiles table. How to optimize?",
          "Broadcast join the user profiles table since 50GB fits in memory. Use bucketing on user_id for repeated joins. Enable adaptive query execution in Spark 3."]),
        ("Vue.js frontend with Nuxt.js and Tailwind",
         ["Building a SaaS dashboard frontend with Vue.js 3 using Nuxt.js. Styling with Tailwind CSS. Need SSR for SEO.",
          "Nuxt 3 with Vue 3 Composition API is a great choice. Tailwind CSS with the @nuxtjs/tailwindcss module works out of the box. SSR is the default in Nuxt.",
          "How do I handle state management? The app has complex nested forms.",
          "Pinia is the official Vue 3 state management. For complex forms, use VeeValidate with Zod for schema validation. Pinia stores can be composed for nested state."]),
        ("DevOps automation with Terraform and Ansible",
         ["Setting up infrastructure automation. Terraform for cloud provisioning on GCP, Ansible for server configuration. Need to manage 200+ VMs.",
          "Terraform modules for reusable GCP infrastructure. Use remote state in GCS with state locking. Ansible dynamic inventory to auto-discover GCP instances.",
          "How do we handle secrets and credentials?",
          "HashiCorp Vault for secrets management. Terraform can provision Vault, Ansible can fetch secrets from it. Use Vault Agent for automatic token renewal."]),
        ("Building a real-time chat app with WebSockets",
         ["Creating a Slack-like chat application using Node.js with Socket.io for real-time messaging. PostgreSQL for persistence.",
          "Socket.io with Redis adapter for horizontal scaling. PostgreSQL for message history. Use rooms for channels, namespaces for workspaces.",
          "Need to support file uploads, message reactions, and thread replies.",
          "MinIO or S3 for file storage. PostgreSQL JSONB for reactions — fast updates without schema changes. Self-referencing messages table for threads."]),
        ("iOS app development with SwiftUI",
         ["Building a fitness tracking iOS app with SwiftUI. Need HealthKit integration, CoreData for offline storage, and CloudKit for sync.",
          "SwiftUI with MVVM pattern works great. HealthKit for workout data, CoreData with NSPersistentCloudKitContainer for seamless iCloud sync.",
          "How do I handle background workout tracking?",
          "Use Background Modes for location updates and motion. HealthKit workout sessions for Apple Watch. Combine framework for reactive data flow."]),
        ("GraphQL API design with schema stitching",
         ["Designing a GraphQL API that federates three existing REST services. Using Apollo Federation with TypeScript.",
          "Apollo Federation v2 is the way to go. Each service becomes a subgraph with its own schema. The gateway composes them. Use @key directive for entity resolution.",
          "Performance concerns — how do we avoid the N+1 problem across federated services?",
          "DataLoader pattern in each subgraph resolver. Gateway-level query planning optimizes cross-service joins. Implement automatic persisted queries for caching."]),
        ("Blockchain smart contract development",
         ["Building DeFi smart contracts on Ethereum using Solidity. Need token staking and liquidity pool contracts.",
          "Use OpenZeppelin contracts as a base — ERC20 for tokens, audited patterns for staking. Hardhat for development, testing, and deployment.",
          "Security is critical. How do we prevent common vulnerabilities?",
          "Slither and Mythril for static analysis. Reentrancy guards from OpenZeppelin. Use Chainlink oracles for price feeds. Always do a professional audit before mainnet."]),
        ("Building a search engine with Elasticsearch",
         ["Creating a product search engine for our marketplace using Elasticsearch. 5 million products with faceted search and autocomplete.",
          "Elasticsearch is perfect for this scale. Use multi-match queries with boosting for relevance. Edge n-gram analyzer for autocomplete. Aggregations for faceted filters.",
          "How do we handle synonyms and typo tolerance?",
          "Custom synonym filter in your analyzer chain. Fuzzy queries for typo tolerance. Consider learning-to-rank plugin for ML-based relevance tuning."]),
        ("Migrating from monolith to microservices",
         ["Our Django monolith is 500k lines of code. Need to gradually extract microservices. Currently serves 100k RPM.",
          "Strangler fig pattern is ideal. Start with high-traffic, well-bounded domains. Use an API gateway (Kong or AWS API Gateway) to route traffic between monolith and new services.",
          "The team is debating between gRPC and REST for inter-service communication.",
          "gRPC for internal service-to-service (faster, typed contracts with protobuf). REST for external APIs. Use Envoy proxy for protocol translation. Consider event-driven architecture with Kafka for async flows."]),
        ("Setting up observability with OpenTelemetry",
         ["Implementing full observability stack. OpenTelemetry for instrumentation, sending to Grafana Cloud (Loki, Tempo, Mimir).",
          "OpenTelemetry SDK auto-instruments most frameworks. Use the collector for processing and routing. Grafana Cloud receives traces (Tempo), logs (Loki), and metrics (Mimir).",
          "How do we correlate logs, traces, and metrics?",
          "Inject trace IDs into log messages. Use exemplars to link metrics to traces. Grafana's Explore view can jump between signals. Set up dashboards with trace-to-log links."]),
    ]

    convs = []
    base_time = 1740000000
    for i in range(150):
        topic = topics[i % len(topics)]
        msgs = [{"message": {"author": {"role": "user" if j % 2 == 0 else "assistant"},
                             "content": {"parts": [topic[1][j % len(topic[1])]]},
                             "create_time": base_time + i * 86400 + j * 300}}
                for j in range(random.randint(2, 6))]
        convs.append({
            "title": topic[0] + (f" (part {i // len(topics) + 1})" if i >= len(topics) else ""),
            "create_time": base_time + i * 86400,
            "mapping": {f"m{j}": msgs[j] for j in range(len(msgs))}
        })

    return save("01_large_150_conversations", convs)


# ─────────────────────────────────────────────
# 2. DEEP NESTED ChatGPT export (realistic structure)
# ─────────────────────────────────────────────
def gen_deep_chatgpt():
    """Realistic ChatGPT export with full mapping structure including system messages."""
    convs = []
    for i in range(20):
        mapping = {}
        # System message (always present in real exports)
        mapping["system_msg"] = {
            "id": "system_msg",
            "message": {
                "id": "system_msg",
                "author": {"role": "system", "name": None, "metadata": {}},
                "content": {"content_type": "text", "parts": ["You are a helpful assistant."]},
                "create_time": 1742000000 + i * 86400,
                "status": "finished_successfully",
                "metadata": {}
            },
            "parent": None,
            "children": ["user_msg_1"]
        }
        # User messages with metadata
        mapping["user_msg_1"] = {
            "id": "user_msg_1",
            "message": {
                "id": "user_msg_1",
                "author": {"role": "user", "name": None, "metadata": {}},
                "content": {"content_type": "text", "parts": [
                    f"I'm working on a project using {'React TypeScript' if i % 3 == 0 else 'Python Django' if i % 3 == 1 else 'Rust Actix'} "
                    f"and I need help with {'performance optimization' if i % 2 == 0 else 'database design'}. "
                    f"My team at {'Acme Corp' if i < 10 else 'TechStart Inc'} uses {'PostgreSQL' if i % 2 == 0 else 'MongoDB'} "
                    f"and deploys on {'AWS' if i < 7 else 'GCP' if i < 14 else 'Azure'}."
                ]},
                "create_time": 1742000000 + i * 86400 + 100,
                "weight": 1.0,
                "metadata": {"timestamp_": "absolute"}
            },
            "parent": "system_msg",
            "children": ["assistant_msg_1"]
        }
        mapping["assistant_msg_1"] = {
            "id": "assistant_msg_1",
            "message": {
                "id": "assistant_msg_1",
                "author": {"role": "assistant", "name": None, "metadata": {"model_slug": "gpt-4"}},
                "content": {"content_type": "text", "parts": [
                    f"Great question! For {'React TypeScript' if i % 3 == 0 else 'Python Django' if i % 3 == 1 else 'Rust Actix'}, "
                    f"I recommend using {'React.memo and useMemo hooks' if i % 3 == 0 else 'Django ORM query optimization with select_related' if i % 3 == 1 else 'async handlers with tokio runtime'} "
                    f"for better performance. With {'PostgreSQL' if i % 2 == 0 else 'MongoDB'}, "
                    f"make sure to {'add proper indexes and use EXPLAIN ANALYZE' if i % 2 == 0 else 'design your document schema for read patterns'}."
                ]},
                "create_time": 1742000000 + i * 86400 + 200,
                "weight": 1.0,
                "metadata": {"finish_details": {"type": "stop"}, "model_slug": "gpt-4"}
            },
            "parent": "user_msg_1",
            "children": ["user_msg_2"]
        }
        # Follow-up
        mapping["user_msg_2"] = {
            "id": "user_msg_2",
            "message": {
                "id": "user_msg_2",
                "author": {"role": "user"},
                "content": {"content_type": "text", "parts": [
                    f"Thanks! Also, my colleague {'Sarah Chen' if i % 4 == 0 else 'Marcus Johnson' if i % 4 == 1 else 'Priya Patel' if i % 4 == 2 else 'Alex Rivera'} "
                    f"suggested we look into {'Redis caching' if i % 2 == 0 else 'Elasticsearch'} for our {'search feature' if i < 10 else 'analytics dashboard'}. "
                    f"We're also considering {'Docker and Kubernetes' if i % 2 == 0 else 'serverless with Lambda'} for deployment."
                ]},
                "create_time": 1742000000 + i * 86400 + 300,
            },
            "parent": "assistant_msg_1",
            "children": []
        }

        convs.append({
            "title": f"{'React' if i % 3 == 0 else 'Django' if i % 3 == 1 else 'Rust'} project help - session {i+1}",
            "create_time": 1742000000 + i * 86400,
            "update_time": 1742000000 + i * 86400 + 400,
            "mapping": mapping,
            "moderation_results": [],
            "current_node": "user_msg_2",
            "plugin_ids": None,
            "conversation_id": f"conv-{i:04d}",
        })

    return save("02_deep_chatgpt_export", convs)


# ─────────────────────────────────────────────
# 3. Realistic Claude export
# ─────────────────────────────────────────────
def gen_claude_export():
    topics = [
        ("Debugging a race condition in Go", [
            {"sender": "human", "text": "I have a race condition in my Golang service. Multiple goroutines are writing to a shared map concurrently. The service crashes with 'concurrent map writes' panic."},
            {"sender": "assistant", "text": "This is a classic Go issue. You have several options: use sync.RWMutex for read-heavy workloads, sync.Map for concurrent access patterns, or channel-based communication. Here's how I'd fix it with sync.RWMutex..."},
            {"sender": "human", "text": "What about using channels instead? Our tech lead James Wong prefers the 'share memory by communicating' approach."},
            {"sender": "assistant", "text": "James is right — that's idiomatic Go. Create a goroutine that owns the map and receives operations via channels. This eliminates shared state entirely. It's cleaner but adds some latency for the channel hop."},
        ]),
        ("Optimizing SQL queries for analytics", [
            {"sender": "human", "text": "Our analytics dashboard is slow. The main query joins 4 tables with 100M+ rows in PostgreSQL. EXPLAIN shows sequential scans everywhere."},
            {"sender": "assistant", "text": "Let's optimize this step by step. First, add covering indexes for the join columns. Second, consider using materialized views for the aggregation. Third, partition the largest table by date range."},
            {"sender": "human", "text": "Our DBA Elena suggested we also look at TimescaleDB for the time-series data. Would that help?"},
            {"sender": "assistant", "text": "TimescaleDB is excellent for time-series analytics. It adds hypertables with automatic time-based partitioning to PostgreSQL. Combined with continuous aggregates, it can dramatically speed up your dashboard queries."},
        ]),
        ("Designing a notification system", [
            {"sender": "human", "text": "Need to design a notification system for our app. Push notifications, email, SMS, and in-app. Should handle 1M+ users with real-time delivery."},
            {"sender": "assistant", "text": "Use an event-driven architecture with Kafka or RabbitMQ as the message bus. Each notification channel (push, email, SMS, in-app) is a separate consumer. Use Redis pub/sub for real-time in-app notifications."},
            {"sender": "human", "text": "How do we handle user preferences and rate limiting?"},
            {"sender": "assistant", "text": "Store preferences in PostgreSQL with a notification_settings table. Use Redis sorted sets for rate limiting — track send counts per user per channel with TTL. Add a preference-checking middleware before each notification dispatch."},
        ]),
    ]

    convs = []
    for i in range(15):
        topic = topics[i % len(topics)]
        convs.append({
            "uuid": f"claude-conv-{i:04d}",
            "name": topic[0] + (f" (continued)" if i >= len(topics) else ""),
            "created_at": f"2026-0{(i % 3) + 1}-{(i % 28) + 1:02d}T{10 + i % 12}:30:00.000Z",
            "updated_at": f"2026-0{(i % 3) + 1}-{(i % 28) + 1:02d}T{11 + i % 12}:00:00.000Z",
            "chat_messages": topic[1]
        })

    return save("03_claude_realistic_export", convs)


# ─────────────────────────────────────────────
# 4. Multilingual / Non-English content
# ─────────────────────────────────────────────
def gen_multilingual():
    convs = [
        {"title": "Python 日本語ドキュメント作成", "create_time": 1742000000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Pythonを使って日本語のドキュメント生成ツールを作りたいです。FastAPIとJinja2テンプレートを使う予定です。データベースはPostgreSQLです。"
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "FastAPIとJinja2の組み合わせは素晴らしい選択です。PostgreSQLからSQLAlchemyでデータを取得し、Jinja2テンプレートでHTMLドキュメントを生成できます。"
            ]}}},
        }},
        {"title": "Desarrollo web con React y Node.js", "create_time": 1742100000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Estoy construyendo una aplicación web con React y Node.js. El backend usa Express con MongoDB. Necesito ayuda con la autenticación OAuth2."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Para OAuth2 con Express, puedo recomendar Passport.js. Con React, usa react-oauth para el flujo del cliente. MongoDB con Mongoose para almacenar sesiones de usuario."
            ]}}},
        }},
        {"title": "Разработка на Rust и WebAssembly", "create_time": 1742200000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Я хочу создать библиотеку на Rust для компиляции в WebAssembly. Нужна интеграция с JavaScript через wasm-bindgen. Проект для компании TechRus."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Rust и WebAssembly отлично работают вместе. Используйте wasm-pack для сборки и публикации. wasm-bindgen обеспечит мост между Rust и JavaScript."
            ]}}},
        }},
        {"title": "Développement d'API avec Django REST Framework", "create_time": 1742300000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Je développe une API REST avec Django REST Framework pour notre startup à Paris. Base de données PostgreSQL, déploiement sur AWS avec Docker."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Django REST Framework est excellent. Utilisez les serializers pour la validation, les viewsets pour les endpoints CRUD. Docker Compose pour le développement local, ECS pour la production AWS."
            ]}}},
        }},
        {"title": "Kubernetes 클러스터 설정 가이드", "create_time": 1742400000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "GCP에서 Kubernetes 클러스터를 설정하려고 합니다. GKE를 사용하고 Helm 차트로 배포할 예정입니다. Terraform으로 인프라를 관리합니다."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "GKE와 Terraform의 조합은 훌륭합니다. Helm 차트로 애플리케이션을 패키징하고, Terraform으로 GKE 클러스터와 네트워크를 프로비저닝하세요."
            ]}}},
        }},
        {"title": "Gemischtes Deutsch/English ML pipeline", "create_time": 1742500000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Ich baue eine Machine Learning Pipeline mit Python und TensorFlow. Das Team bei MunichTech GmbH braucht ein Modell für Textklassifikation. Wir verwenden Hugging Face Transformers und trainieren auf GPU mit CUDA."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Für Textklassifikation empfehle ich BERT oder ein deutsches Modell wie german-bert. Hugging Face macht das fine-tuning einfach. Nutzen Sie PyTorch Lightning für das Training und MLflow für Experiment-Tracking."
            ]}}},
        }},
        {"title": "混合中英文 React Native 开发", "create_time": 1742600000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "我在开发一个React Native应用，后端使用Node.js和Express。数据库是MongoDB。部署在阿里云上。需要集成微信支付和支付宝。"
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "React Native配合Node.js是很好的选择。对于微信支付集成，可以使用react-native-wechat-lib。MongoDB Atlas提供中国区域的部署选项。"
            ]}}},
        }},
        {"title": "تطوير تطبيق ويب بـ Angular و Firebase", "create_time": 1742700000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "أريد بناء تطبيق ويب باستخدام Angular مع Firebase. أحتاج إلى مصادقة المستخدمين وقاعدة بيانات Firestore. المشروع لشركة TechDubai."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Angular مع Firebase خيار ممتاز. استخدم AngularFire للتكامل السلس. Firestore لقاعدة البيانات و Firebase Auth للمصادقة. يمكنك نشر التطبيق على Firebase Hosting."
            ]}}},
        }},
    ]
    return save("04_multilingual_content", convs)


# ─────────────────────────────────────────────
# 5. Adversarial / Pathological data
# ─────────────────────────────────────────────
def gen_adversarial():
    convs = [
        # XSS payloads in titles and content
        {"title": '<script>alert("xss")</script> React help', "create_time": 1742000000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                'How do I use <img onerror="alert(1)" src=x> in React? Also testing "quoted XSS" and <b>bold tags</b>.'
            ]}}},
        }},
        # Extremely long message (10KB+)
        {"title": "Very long conversation about everything", "create_time": 1742100000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                " ".join([f"This is sentence number {i} about React, Python, Docker, Kubernetes, AWS, PostgreSQL, MongoDB, Redis, FastAPI, Django, TensorFlow, PyTorch, Rust, Golang, TypeScript, Next.js, Vue, Svelte, GraphQL, Elasticsearch." for i in range(100)])
            ]}}},
        }},
        # Message with only special characters
        {"title": "Special !!@#$%^&*() chars", "create_time": 1742200000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "!@#$%^&*()_+-=[]{}|;':\",./<>?`~ \t\n\n\n tabs and newlines \r\n"
            ]}}},
        }},
        # Message with code blocks and backticks
        {"title": "Code heavy conversation", "create_time": 1742300000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "```python\nimport React from 'react'\ndef hello():\n    print('Hello FastAPI PostgreSQL Docker')\n    return {'status': 'ok'}\n```\nCan you fix this Python code that incorrectly imports React?"
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "```python\nfrom fastapi import FastAPI\n\napp = FastAPI()\n\n@app.get('/')\ndef hello():\n    return {'status': 'ok'}\n```\nReact is a JavaScript framework, not Python. I've fixed it to use FastAPI properly."
            ]}}},
        }},
        # Empty strings and whitespace-only parts
        {"title": "   ", "create_time": 1742400000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": ["", "   ", "\n\n", "actual content about Docker"]}}},
        }},
        # Extremely long entity names
        {"title": "Very long names test", "create_time": 1742500000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "I'm working with SuperLongCompanyNameThatShouldBeTruncatedInTheUI International Enterprises LLC on a project using React and PostgreSQL. Contact person is Alexandrina Bartholomew Christopherson III."
            ]}}},
        }},
        # Repeated entities (stress test deduplication)
        {"title": "Repetition stress test", "create_time": 1742600000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                " ".join(["React"] * 50 + ["Docker"] * 30 + ["Python"] * 40 + ["AWS"] * 20)
            ]}}},
        }},
        # Conversation with only assistant messages
        {"title": "No user messages", "create_time": 1742700000, "mapping": {
            "m1": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Here's how to use React with TypeScript and Docker for deployment on AWS."
            ]}}},
        }},
        # Null and missing everything
        {"title": None, "create_time": None, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [None, 42, True, "valid text about Python and FastAPI"]}}},
        }},
        # URL-heavy content
        {"title": "Links everywhere", "create_time": 1742800000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Check these: https://react.dev https://docs.docker.com https://kubernetes.io/docs/ Also see React docs at https://reactjs.org and Python at https://python.org. Using FastAPI from https://fastapi.tiangolo.com"
            ]}}},
        }},
    ]
    return save("05_adversarial_pathological", convs)


# ─────────────────────────────────────────────
# 6. Minimal / Sparse data
# ─────────────────────────────────────────────
def gen_minimal():
    convs = [
        {"title": "hi", "create_time": 1742000000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": ["hi"]}}},
        }},
        {"title": "ok", "create_time": 1742100000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": ["ok"]}}},
        }},
        {"title": "", "create_time": 1742200000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": ["React"]}}},
        }},
        {"title": "Single tech mention", "create_time": 1742300000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": ["Docker"]}}},
        }},
        {"title": "Just a question", "create_time": 1742400000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": ["What is Python?"]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": ["Python is a programming language."]}}},
        }},
    ]
    return save("06_minimal_sparse", convs)


# ─────────────────────────────────────────────
# 7. Domain-specific: Medical / Legal / Finance
# ─────────────────────────────────────────────
def gen_domain_specific():
    convs = [
        {"title": "HIPAA compliance for healthcare app", "create_time": 1742000000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Building a healthcare app that needs HIPAA compliance. Using React Native for mobile, FastAPI backend, PostgreSQL for patient records. Deploy on AWS with encryption at rest and in transit."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "HIPAA compliance requires several layers. Use AWS KMS for encryption keys, RDS with encryption enabled for PostgreSQL. Implement audit logging with CloudTrail. FastAPI middleware for access control and request logging. BAA with AWS is essential."
            ]}}},
        }},
        {"title": "Financial trading system architecture", "create_time": 1742100000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Designing a low-latency trading system. Need microsecond-level execution. Using Rust for the matching engine, Python for strategy development, and Apache Kafka for market data distribution. The CTO at QuantEdge Capital wants FIX protocol support."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "For low-latency trading: Rust with lock-free data structures for the matching engine. Kernel bypass networking with DPDK. Kafka for market data fan-out. Redis for order state. Python for backtesting only — never in the hot path. FIX 4.4 with quickfixj."
            ]}}},
        }},
        {"title": "Legal document management system", "create_time": 1742200000, "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "Creating a document management system for a law firm. Need OCR for scanned documents, full-text search with Elasticsearch, version control for contracts, and e-signature integration with DocuSign. The managing partner Rachel Torres needs audit trails."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "Use Tesseract OCR with Python for document scanning. Elasticsearch for full-text search with legal-specific analyzers. Git-inspired versioning for contracts stored in PostgreSQL. DocuSign API for e-signatures. Comprehensive audit trail with event sourcing pattern."
            ]}}},
        }},
    ]
    return save("07_domain_specific", convs)


# ─────────────────────────────────────────────
# 8. Wrapper formats (nested objects)
# ─────────────────────────────────────────────
def gen_wrapper_formats():
    inner = [
        {"title": "Wrapped React discussion", "messages": [
            {"role": "user", "content": "How do I optimize React rendering with TypeScript?"},
            {"role": "assistant", "content": "Use React.memo, useMemo, and useCallback. TypeScript generics help with prop types."},
        ]},
        {"title": "Wrapped Docker question", "messages": [
            {"role": "user", "content": "Best practices for Docker in production with Kubernetes?"},
            {"role": "assistant", "content": "Multi-stage builds, non-root users, health checks, resource limits in K8s pods."},
        ]},
    ]

    formats = {
        "08a_wrapper_conversations": {"conversations": inner},
        "08b_wrapper_chats": {"chats": inner},
        "08c_wrapper_data": {"data": inner},
        "08d_double_nested": {"response": {"data": {"conversations": inner}}},
    }

    paths = []
    for name, data in formats.items():
        paths.append(save(name, data))
    return paths


# ─────────────────────────────────────────────
# 9. Claude with text as array of objects
# ─────────────────────────────────────────────
def gen_claude_text_array():
    convs = [{
        "name": "Multi-part Claude response",
        "created_at": "2026-03-15T10:00:00Z",
        "chat_messages": [
            {"sender": "human", "text": "Explain React hooks and TypeScript integration"},
            {"sender": "assistant", "text": [
                {"type": "text", "text": "React hooks are functions that let you use state and lifecycle features in functional components. "},
                {"type": "text", "text": "With TypeScript, you get full type safety. Use useState<Type>() for typed state, "},
                {"type": "text", "text": "useEffect with proper cleanup types, and custom hooks with generic return types."},
            ]},
            {"sender": "human", "text": "What about useReducer with TypeScript?"},
            {"sender": "assistant", "text": [
                {"type": "text", "text": "useReducer is great with TypeScript discriminated unions for actions. "},
                {"type": "text", "text": "Define your state type, action type with string literal discriminants, "},
                {"type": "text", "text": "and the reducer function gets full type inference automatically."},
            ]},
        ],
    }]
    return save("09_claude_text_array", convs)


# ─────────────────────────────────────────────
# 10. High entity density (many proper nouns)
# ─────────────────────────────────────────────
def gen_high_entity():
    convs = [{
        "title": "Team standup discussion",
        "create_time": 1742000000,
        "mapping": {
            "m1": {"message": {"author": {"role": "user"}, "content": {"parts": [
                "In our standup today, Sarah Chen mentioned the React frontend is blocked by the API changes Marcus Johnson is making in the Python backend. "
                "Emily Davis is finishing the Docker setup while Roberto Garcia works on the Kubernetes helm charts. "
                "The PM Jessica Kim wants the PostgreSQL migration done by Friday. "
                "David Park is debugging the Redis caching layer and Anna Petrov is reviewing the Elasticsearch indexing. "
                "Meanwhile, Thomas Brown from the London office is working with Aisha Patel on the GraphQL gateway. "
                "Our CTO James Wilson approved the AWS to GCP migration that Chris Taylor proposed. "
                "Lisa Zhang is handling the Terraform infrastructure and Mike O'Brien is setting up the CI/CD pipeline with GitHub Actions."
            ]}}},
            "m2": {"message": {"author": {"role": "assistant"}, "content": {"parts": [
                "That's a lot happening! Let me organize by priority: "
                "1. Sarah Chen and Marcus Johnson need to sync on the API contract — suggest they pair program today. "
                "2. Jessica Kim's PostgreSQL migration is time-critical — David Park should prioritize that over Redis. "
                "3. Emily Davis and Roberto Garcia are on parallel tracks (Docker/K8s) which is efficient. "
                "4. Thomas Brown and Aisha Patel's GraphQL work could unblock the frontend once Marcus's API changes land. "
                "5. Lisa Zhang's Terraform and Chris Taylor's GCP migration should be coordinated with Mike O'Brien's CI/CD setup."
            ]}}},
        },
    }]
    return save("10_high_entity_density", convs)


if __name__ == "__main__":
    print("Generating test datasets...")
    paths = []
    paths.append(gen_large())
    paths.append(gen_deep_chatgpt())
    paths.append(gen_claude_export())
    paths.append(gen_multilingual())
    paths.append(gen_adversarial())
    paths.append(gen_minimal())
    paths.append(gen_domain_specific())
    paths.extend(gen_wrapper_formats())
    paths.append(gen_claude_text_array())
    paths.append(gen_high_entity())

    print(f"\nGenerated {len(paths)} test datasets:")
    for p in paths:
        size = os.path.getsize(p)
        print(f"  {os.path.basename(p):45s} {size:>8,} bytes")
