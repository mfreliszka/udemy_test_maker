# Domain keyword mappings for auto-suggestion
# Based on Google Professional Cloud Developer Certification Exam Guide
# Each domain has keywords with different weights (higher = more important)

DOMAIN_KEYWORDS = {
    'google_cloud_developer': {
        'Section 1: Designing highly scalable, available, and reliable cloud-native applications': {
            'high_weight': [
                # 1.1 Designing high-performing applications and APIs
                'compute engine', 'gke', 'cloud run', 'choosing platform', 'use case', 'requirements',
                'building', 'refactoring', 'deploying', 'application containers', 'cloud run', 'gke',
                'google cloud services', 'geographically distributed', 'latency', 'regional services', 'zonal services',
                'load balancers', 'load balancing', 'session affinity', 'performant content delivery',
                'memorystore', 'caching solutions', 'caching',
                'apis', 'http rest', 'grpc', 'google remote procedure call',
                'application rate limiting', 'authentication', 'observability', 'apigee', 'cloud api gateway',
                'asynchronous', 'event-driven approaches', 'eventarc', 'pub/sub', 'pubsub',
                'cost optimization', 'resource usage', 'optimizing cost',
                'data replication', 'zonal failover', 'regional failover', 'failover models',
                'traffic splitting', 'gradual rollouts', 'rollbacks', 'a/b testing', 'cloud run', 'gke',
                'workflows', 'eventarc', 'cloud tasks', 'cloud scheduler', 'orchestrating application services',
                
                # 1.2 Designing secure applications
                'data retention', 'organization policies', 'cloud storage object lifecycle management',
                'cloud storage retention policies', 'lock retention policies',
                'security mechanisms', 'vulnerabilities', 'identity-aware proxy', 'iap', 'web security scanner',
                'artifact analysis', 'security command center',
                'application secrets', 'credentials', 'encryption keys', 'secret manager',
                'cloud key management service', 'workload identity federation',
                'application default credentials', 'json web token', 'jwt', 'oauth 2.0', 'cloud sql auth proxy', 'alloydb auth proxy',
                'identity platform', 'end-user accounts',
                'identity and access management', 'iam roles', 'service accounts',
                'cloud service mesh', 'kubernetes network policies', 'service-to-service communications',
                'least privileged access', 'principle of least privilege',
                'binary authorization', 'application artifacts',
                
                # 1.3 Storing and accessing data
                'storage system', 'volume of data', 'performance requirements',
                'schemas', 'structured databases', 'alloydb', 'spanner', 'unstructured databases', 'bigtable', 'datastore',
                'eventual consistency', 'strongly consistent replication', 'alloydb', 'bigtable', 'cloud sql', 'spanner', 'cloud storage',
                'signed urls', 'cloud storage objects', 'grant access',
                'bigquery', 'analytics', 'ai/ml workloads', 'writing data'
            ],
            'medium_weight': [
                'microservices', 'architecture', 'design patterns', 'scalable', 'scalability',
                'availability', 'reliable', 'cloud-native', 'designing', 'application design',
                'system design', 'distributed systems', 'fault tolerance', 'resilience',
                'auto scaling', 'serverless architecture', 'performance', 'optimization',
                'best practices', 'design principles', 'cloud architecture', 'solution design',
                'application structure', 'service mesh', 'event-driven', 'asynchronous programming',
                'security', 'compliance', 'data protection', 'encryption', 'access control',
                'database design', 'data modeling', 'storage solutions', 'data access patterns'
            ],
            'low_weight': [
                'application', 'service', 'system', 'cloud', 'google cloud',
                'efficiency', 'maintainable', 'extensible', 'performance optimization',
                'cloud services', 'managed services', 'platform services'
            ]
        },
        
        'Section 2: Building and testing applications': {
            'high_weight': [
                # 2.1 Setting up development environment
                'google cloud cli', 'local application development', 'local unit testing', 'emulating google cloud services',
                'google cloud console', 'cloud sdk', 'cloud code', 'gemini cloud assist', 'gemini code assist',
                'cloud shell', 'cloud workstations',
                
                # 2.2 Building
                'cloud build', 'artifact registry', 'build and store containers', 'source code',
                'provenance', 'cloud build', 'binary authorization',
                
                # 2.3 Testing
                'unit tests', 'gemini code assist', 'writing unit tests',
                'automated integration tests', 'cloud build', 'executing integration tests'
            ],
            'medium_weight': [
                'testing', 'unit test', 'integration test', 'debugging', 'build process',
                'ci/cd', 'continuous integration', 'continuous deployment', 'pipeline',
                'code quality', 'test automation', 'build tools', 'compilation',
                'development environment', 'local development', 'development tools',
                'sdk', 'api development', 'version control', 'code review',
                'static analysis', 'linting', 'development workflow', 'containers', 'docker',
                'container registry', 'artifact management', 'build automation'
            ],
            'low_weight': [
                'development', 'coding', 'programming', 'software development',
                'testing framework', 'development setup', 'build configuration',
                'development best practices', 'code organization'
            ]
        },
        
        'Section 3: Deploying applications': {
            'high_weight': [
                # 3.1 Deploying applications to Cloud Run
                'cloud run', 'deploying applications', 'source code', 'deploying from source',
                'cloud run services', 'triggers', 'eventarc', 'pub/sub', 'pubsub',
                'event receivers', 'eventarc', 'pub/sub',
                'apis', 'applications', 'apigee', 'exposing apis', 'securing apis',
                'api version', 'cloud endpoints', 'backward compatibility', 'deploying new api version',
                
                # 3.2 Deploying containers to GKE
                'gke', 'google kubernetes engine', 'deploying containerized applications',
                'resource requirements', 'container workloads', 'defining resource requirements',
                'kubernetes health checks', 'application availability', 'health checks',
                'horizontal pod autoscaler', 'cost optimization', 'hpa'
            ],
            'medium_weight': [
                'deployment', 'deploy', 'containers', 'docker', 'kubernetes',
                'container deployment', 'rolling deployment', 'blue-green deployment', 'canary deployment',
                'production deployment', 'staging', 'environment management', 'release management',
                'configuration management', 'infrastructure', 'compute engine',
                'managed services', 'serverless deployment', 'container orchestration',
                'application hosting', 'runtime environment', 'platform services'
            ],
            'low_weight': [
                'hosting', 'runtime', 'platform', 'cloud platform',
                'deployment strategy', 'release', 'launch', 'application deployment',
                'service deployment', 'infrastructure deployment'
            ]
        },
        
        'Section 4: Integrating applications with Google Cloud services': {
            'high_weight': [
                # 4.1 Integrating applications with data and storage services
                'google cloud datastores', 'cloud sql', 'firestore', 'cloud storage', 'managing connections',
                'reading data', 'writing data', 'google cloud datastores',
                'pub/sub', 'pubsub', 'publish data', 'consume data', 'publishing and consuming',
                
                # 4.2 Consuming Google Cloud APIs
                'google cloud services', 'enabling google cloud services',
                'api calls', 'cloud client libraries', 'rest api', 'grpc', 'api explorer',
                'batching requests', 'restricting return data', 'paginating results', 'caching results',
                'handling errors', 'exponential backoff', 'error handling',
                'service accounts', 'cloud api calls', 'making api calls',
                
                # 4.3 Troubleshooting and observability
                'metrics', 'logs', 'traces', 'google cloud observability', 'instrumenting code', 'troubleshooting',
                'google cloud observability', 'identifying issues', 'resolving issues',
                'error reporting', 'managing application issues',
                'trace ids', 'correlate trace spans', 'tracing across services',
                'gemini cloud assist'
            ],
            'medium_weight': [
                'integration', 'service integration', 'data integration', 'api integration',
                'database integration', 'storage integration', 'messaging', 'message queues',
                'data processing', 'etl', 'data pipeline', 'data flow',
                'authentication', 'authorization', 'iam', 'security integration',
                'monitoring', 'logging', 'observability', 'performance monitoring',
                'error tracking', 'troubleshooting', 'debugging', 'application monitoring',
                'service communication', 'inter-service communication'
            ],
            'low_weight': [
                'backend services', 'third-party integration', 'external services',
                'data access', 'data storage', 'cloud services', 'managed services',
                'application integration', 'system integration', 'service connectivity'
            ]
        }
    }
}