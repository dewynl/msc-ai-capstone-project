# RAG-Enhanced T5 Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing a Retrieval-Augmented Generation (RAG) system that enhances T5 syllabus generation using the educational components we previously generated. The system will intelligently retrieve relevant components and use them to guide T5 in creating pedagogically sound syllabi.

## Prerequisites

You should have completed:
- ✅ Synthetic data generation (18MB+ educational components in `data/components/`)
- ✅ T5 baseline implementation and evaluation
- ✅ Branch `rag-enhanced-generation` created and checked out

## System Architecture

```
Course Requirements → Query Encoder → Component Retrieval → RAG-Enhanced T5 → Generated Syllabus
                                            ↓
                      Educational Component Vector Store
                      (activities, assessments, modules)
```

## Implementation Steps

### Phase 1: Set Up Vector Store Infrastructure

#### Step 1.1: Install Required Dependencies

**For initial implementation (ChromaDB approach):**

```bash
pip install sentence-transformers chromadb
```

**Dependencies explanation:**
- `sentence-transformers`: For creating embeddings of educational components
- `chromadb`: Vector database with built-in persistence (easier to start with)

#### Step 1.2: Create Vector Store Module (ChromaDB Implementation)

Create `src/rag/vector_store.py`:

```python
import json
import uuid
from pathlib import Path
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings

class SyllabusComponentStore:
    """Storage and retrieval system for syllabus components using ChromaDB"""

    def __init__(self,
                 model_name: str = "all-MiniLM-L6-v2",
                 persist_directory: str = "./chroma_db"):
        self.encoder = SentenceTransformer(model_name)

        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=persist_directory)

        # Create or get collection for syllabus components
        self.collection = self.client.get_or_create_collection(
            name="syllabus_components",
            metadata={"description": "Syllabus modules, activities, and assessments"}
        )

    def encode_component(self, component: Dict[str, Any]) -> str:
        """Convert educational component to searchable text"""
        # Combine title, description, and key educational fields
        text_parts = [
            component.get("title", ""),
            component.get("description", ""),
            # Add domain and learning objectives for better search
            component.get("domain", ""),
            " ".join(component.get("learning_objectives", [])),
        ]
        return " ".join(filter(None, text_parts))

    def add_components(self, components: List[Dict[str, Any]], component_type: str):
        """Add educational components to ChromaDB collection"""
        print(f"Adding {len(components)} {component_type} to vector store...")

        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []

        for component in components:
            # Create searchable text
            doc_text = self.encode_component(component)
            documents.append(doc_text)

            # Add metadata (ChromaDB will store this alongside vectors)
            metadata = {
                "component_type": component_type,
                "title": component.get("title", ""),
                "domain": component.get("domain", ""),
                "original_data": json.dumps(component)  # Store full component data
            }
            metadatas.append(metadata)

            # Use existing ID or generate new one
            component_id = component.get(f"{component_type[:-1]}_id", str(uuid.uuid4()))
            ids.append(f"{component_type}_{component_id}")

        # Add to ChromaDB (it handles embedding generation automatically)
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(f"✅ Added {len(components)} {component_type} successfully")

    def search(self, query: str, k: int = 5,
               component_type: str = None) -> List[Tuple[Dict[str, Any], float]]:
        """Search for relevant components"""

        # Build query filters if component type specified
        where_filter = {}
        if component_type:
            where_filter = {"component_type": component_type}

        # Search ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=k,
            where=where_filter if where_filter else None
        )

        # Format results as (component_data, similarity_score)
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # Parse original component data from metadata
                original_data = json.loads(metadata['original_data'])
                # ChromaDB returns distance (lower = more similar)
                # Convert to similarity score (higher = more similar)
                similarity_score = 1.0 - distance
                formatted_results.append((original_data, similarity_score))

        return formatted_results

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the stored components"""
        count = self.collection.count()
        return {"total_components": count}
```

**Key advantages of ChromaDB approach:**
- ✅ **Automatic persistence** - Data saved automatically to disk
- ✅ **Built-in embedding** - ChromaDB handles vector generation
- ✅ **Simpler API** - Less code to write and maintain
- ✅ **Metadata storage** - Easy to store and filter by component properties

#### Step 1.3: Load and Index Educational Components

Create `src/rag/component_indexer.py`:

```python
import json
from pathlib import Path
from typing import Dict, List
from .vector_store import SyllabusComponentStore

def load_all_components() -> Dict[str, List[Dict]]:
    """Load all syllabus components from data/components/"""
    components = {}

    # Define component file mappings
    component_files = {
        "modules": "data/components/modules.json",
        "activities": "data/components/learning_activities.json",
        "assessments": "data/components/assessments.json"
    }

    for component_type, file_path in component_files.items():
        print(f"Loading {component_type} from {file_path}...")
        with open(file_path) as f:
            component_list = json.load(f)
            components[component_type] = component_list
            print(f"✅ Loaded {len(component_list)} {component_type}")

    return components

def build_component_store(persist_directory: str = "./chroma_db") -> SyllabusComponentStore:
    """Build complete vector store from all components"""
    print("🚀 Building syllabus component store...")

    # Initialize component store
    store = SyllabusComponentStore(persist_directory=persist_directory)

    # Check if already populated
    stats = store.get_collection_stats()
    if stats["total_components"] > 0:
        print(f"📊 Component store already contains {stats['total_components']} components")
        print("   Use store.collection.delete() to rebuild if needed")
        return store

    # Load and index all components
    components = load_all_components()

    total_added = 0
    for component_type, component_list in components.items():
        store.add_components(component_list, component_type)
        total_added += len(component_list)

    print(f"🎉 Component store built successfully with {total_added} components!")
    return store

def test_component_store():
    """Test the component store with sample queries"""
    print("🧪 Testing component store...")

    store = build_component_store()

    # Test queries for different component types
    test_queries = [
        ("machine learning algorithms", "modules"),
        ("group project activities", "activities"),
        ("final exam assessment", "assessments"),
        ("python programming", None)  # Search all types
    ]

    for query, component_type in test_queries:
        print(f"\n🔍 Query: '{query}' (type: {component_type or 'all'})")
        results = store.search(query, k=3, component_type=component_type)

        for i, (component, score) in enumerate(results, 1):
            print(f"   {i}. {component.get('title', 'N/A')} (score: {score:.3f})")
            print(f"      Domain: {component.get('domain', 'N/A')}")

if __name__ == "__main__":
    test_component_store()
```

**To test your implementation:**
```bash
cd /path/to/your/project
python -m src.rag.component_indexer
```

### Phase 2: Implement RAG Query Processing

#### Step 2.1: Create Query Understanding Module

Create `src/rag/query_processor.py`:

```python
from typing import Dict, List, Any

def extract_search_terms(requirements: Dict[str, Any]) -> List[str]:
    """Extract key search terms from course requirements"""
    # TODO: Extract domain, level, learning objectives, etc.
    terms = []
    if requirements.get('domain'):
        terms.append(requirements['domain'])
    if requirements.get('level'):
        terms.append(requirements['level'])
    return terms

def generate_component_queries(requirements: Dict[str, Any]) -> Dict[str, str]:
    """Generate specific queries for each component type"""
    return {
        "modules": f"course modules for {requirements.get('domain', '')} at {requirements.get('level', '')} level",
        "activities": f"learning activities for {requirements.get('domain', '')} students",
        "assessments": f"assessments for {requirements.get('domain', '')} course"
    }
```

#### Step 2.2: Implement Component Retrieval Pipeline

Create `src/rag/retrieval_pipeline.py`:

```python
from typing import Dict, List, Any
from .vector_store import SyllabusComponentStore
from .query_processor import generate_component_queries

class ComponentRetrievalPipeline:
    """Retrieve relevant educational components for course requirements"""

    def __init__(self, component_store: SyllabusComponentStore):
        self.component_store = component_store

    def retrieve_components(self, requirements: Dict[str, Any], k_per_type: int = 3) -> Dict[str, List]:
        """Retrieve relevant components for each type"""
        queries = generate_component_queries(requirements)
        retrieved = {}

        for component_type, query in queries.items():
            # Search component store
            results = self.component_store.search(query, k=k_per_type, component_type=component_type)
            retrieved[component_type] = [result[0] for result in results]  # Extract components

        return retrieved

    def filter_by_domain_and_level(self, components: Dict[str, List], requirements: Dict[str, Any]) -> Dict[str, List]:
        """Apply domain and difficulty level filtering"""
        # TODO: Filter components based on course requirements
        filtered = {}
        target_domain = requirements.get('domain', '').lower()

        for comp_type, comp_list in components.items():
            filtered[comp_type] = []
            for comp in comp_list:
                comp_domain = comp.get('domain', '').lower()
                if not target_domain or target_domain in comp_domain or comp_domain in target_domain:
                    filtered[comp_type].append(comp)

        return filtered
```

### Phase 3: Enhance T5 with RAG Context

#### Step 3.1: Create RAG-Enhanced T5 Generator

Create `src/rag/rag_t5_generator.py`:

```python
from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch

class RAGEnhancedT5Generator:
    """T5 generator enhanced with retrieved educational components"""

    def __init__(self, model_name: str = "t5-base"):
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.device = torch.device("cpu")  # or "cuda" if available

    def create_prompt(self, requirements: Dict[str, Any], retrieved_components: Dict[str, List]) -> str:
        """Create T5 input prompt with retrieved component context"""

        # Base course requirements
        prompt = f"Generate syllabus for: {requirements.get('title', '')}\n"
        prompt += f"Domain: {requirements.get('domain', '')} Level: {requirements.get('level', '')}\n"
        prompt += f"Description: {requirements.get('description', '')}\n\n"

        # Add retrieved component context
        prompt += "Available Educational Components:\n"

        # Add modules
        if "modules" in retrieved_components:
            prompt += "Relevant Modules:\n"
            for i, module in enumerate(retrieved_components["modules"][:2], 1):
                prompt += f"{i}. {module.get('title', '')}: {module.get('description', '')[:200]}...\n"

        # Add activities
        if "activities" in retrieved_components:
            prompt += "\nRelevant Activities:\n"
            for i, activity in enumerate(retrieved_components["activities"][:2], 1):
                prompt += f"{i}. {activity.get('title', '')}: {activity.get('description', '')[:200]}...\n"

        # Add assessments
        if "assessments" in retrieved_components:
            prompt += "\nRelevant Assessments:\n"
            for i, assessment in enumerate(retrieved_components["assessments"][:2], 1):
                prompt += f"{i}. {assessment.get('title', '')}: {assessment.get('description', '')[:200]}...\n"

        return prompt

    def generate_syllabus(self, prompt: str, max_length: int = 1024) -> str:
        """Generate syllabus using prompt with retrieved components"""
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            max_length=512,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
                do_sample=False
            )

        # Decode output
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text
```

### Phase 4: Create RAG System Integration

#### Step 4.1: Build Complete RAG System

Create `src/rag/rag_system.py`:

```python
from typing import Dict, Any
from .vector_store import SyllabusComponentStore
from .component_indexer import build_component_store
from .retrieval_pipeline import ComponentRetrievalPipeline
from .rag_t5_generator import RAGEnhancedT5Generator

def generate_rag_syllabus(course_requirements: Dict[str, Any],
                         persist_directory: str = "./chroma_db") -> Dict[str, Any]:
    """Generate syllabus using complete RAG pipeline"""

    # Step 1: Load component store
    print("Loading component store...")
    component_store = build_component_store(persist_directory)

    # Step 2: Initialize retrieval pipeline
    print("Setting up retrieval pipeline...")
    retrieval_pipeline = ComponentRetrievalPipeline(component_store)

    # Step 3: Initialize T5 generator
    print("Loading T5 generator...")
    generator = RAGEnhancedT5Generator()

    # Step 4: Retrieve relevant components
    print("Retrieving relevant components...")
    retrieved = retrieval_pipeline.retrieve_components(course_requirements)

    # Step 5: Create prompt with retrieved components
    print("Creating prompt with retrieved components...")
    prompt = generator.create_prompt(course_requirements, retrieved)

    # Step 6: Generate syllabus
    print("Generating syllabus with T5...")
    generated_syllabus = generator.generate_syllabus(prompt)

    return {
        "syllabus_content": generated_syllabus,
        "retrieved_components": retrieved,
        "prompt": prompt
    }
```

#### Step 4.2: Create Test Script

Create `scripts/test_rag_system.py`:

```python
from src.rag.rag_system import generate_rag_syllabus

def test_rag_generation():
    """Test the complete RAG system"""

    # Test course requirements
    test_requirements = {
        "title": "Introduction to Machine Learning",
        "domain": "Computer Science",
        "level": "undergraduate",
        "description": "Fundamentals of machine learning algorithms and applications"
    }

    # Generate syllabus using RAG
    result = generate_rag_syllabus(test_requirements)

    print("Generated Syllabus:")
    print("=" * 50)
    print(result["syllabus_content"])

    print("\nRetrieved Components:")
    print("=" * 50)
    for comp_type, components in result["retrieved_components"].items():
        print(f"{comp_type.title()}: {len(components)} components")

if __name__ == "__main__":
    test_rag_generation()
```

### Phase 5: Evaluation and Comparison

#### Step 5.1: Create RAG vs Baseline Comparison

Create `scripts/evaluate_rag_vs_baseline.py`:

```python
def compare_rag_vs_baseline():
    """Compare RAG-enhanced generation with baseline T5"""

    # Test cases
    test_cases = [
        {
            "title": "Data Structures and Algorithms",
            "domain": "Computer Science",
            "level": "undergraduate"
        },
        {
            "title": "Project Management Fundamentals",
            "domain": "Leadership",
            "level": "professional"
        }
        # Add more test cases
    ]

    # Initialize baseline generator
    baseline_generator = BaselineT5Generator()  # Your existing T5

    results = []
    for test_case in test_cases:
        print(f"Testing: {test_case['title']}")

        # Generate with both systems
        rag_result = generate_rag_syllabus(test_case)
        baseline_result = baseline_generator.generate_syllabus(test_case)

        # Store for comparison
        results.append({
            "requirements": test_case,
            "rag_output": rag_result["syllabus_content"],
            "baseline_output": baseline_result,
            "retrieved_components": rag_result["retrieved_components"]
        })

    return results
```

## Learning Exercises

As you implement each phase, try these exercises to deepen your understanding:

### Exercise 1: Component Embedding Analysis
- Generate embeddings for 10 similar components
- Use cosine similarity to see how closely related they are
- Experiment with different embedding models

### Exercise 2: Query Processing Improvement
- Try different ways to extract search terms from course requirements
- Implement domain-specific query expansion
- Add filtering by Bloom's taxonomy level

### Exercise 3: Prompt Engineering
- Experiment with different ways to present retrieved components to T5
- Try structured vs. narrative component descriptions
- Test different numbers of retrieved components (1-5 per type)

### Exercise 4: Evaluation Metrics
- Implement automated quality scoring
- Compare component relevance between queries
- Measure generation diversity vs. baseline

## Troubleshooting Tips

**Common Issues:**

1. **Memory Issues with Large Vector Store**
   - Use `faiss.IndexIVFPQ` for larger datasets
   - Consider clustering components before indexing

2. **Poor Retrieval Quality**
   - Experiment with different embedding models
   - Add more context to component encoding
   - Try query expansion techniques

3. **T5 Generation Quality**
   - Adjust prompt structure and length
   - Fine-tune retrieval-generation balance
   - Experiment with different T5 model sizes

**Debugging Steps:**
1. Test each component independently
2. Log intermediate outputs (embeddings, retrieved components, prompts)
3. Start with small datasets and scale up
4. Compare outputs at each pipeline stage

## Success Metrics

You'll know your implementation is working when:

- ✅ Vector store can retrieve semantically similar components
- ✅ Retrieved components are relevant to course requirements
- ✅ Generated syllabi reference specific retrieved components
- ✅ RAG output shows less repetition than baseline T5
- ✅ Generated content is more pedagogically coherent

## Advanced: FAISS Implementation (Optional Performance Upgrade)

If you need better performance for larger datasets or want to optimize memory usage, you can switch to FAISS:

### When to Consider FAISS:
- ✅ Dataset grows beyond 10k+ components
- ✅ Need sub-millisecond search times
- ✅ Memory usage becomes a concern
- ✅ Moving to production deployment

### FAISS Implementation:

**Install FAISS:**
```bash
pip install faiss-cpu  # or faiss-gpu for GPU acceleration
```

**Alternative Component Store (replace ChromaDB implementation):**
```python
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

class FAISSSyllabusComponentStore:
    """FAISS-based storage system for syllabus components"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.encoder = SentenceTransformer(model_name)
        self.embedding_dim = self.encoder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatIP(self.embedding_dim)  # Inner product similarity
        self.components = []
        self.component_metadata = []

    def add_components(self, components: List[Dict[str, Any]], component_type: str):
        """Add components to FAISS index"""
        print(f"Encoding {len(components)} {component_type}...")

        # Generate embeddings
        texts = [self.encode_component(comp) for comp in components]
        embeddings = self.encoder.encode(texts, convert_to_numpy=True)

        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)

        # Add to FAISS index
        self.index.add(embeddings.astype('float32'))

        # Store metadata
        for comp in components:
            self.components.append(comp)
            self.component_metadata.append({"type": component_type})

    def search(self, query: str, k: int = 5) -> List[Tuple[Dict[str, Any], float]]:
        """Search using FAISS"""
        # Encode query
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), k)

        # Format results
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.components):
                results.append((self.components[idx], float(score)))

        return results

    def save(self, path: str):
        """Save FAISS index and metadata"""
        faiss.write_index(self.index, f"{path}.index")
        with open(f"{path}.metadata", "wb") as f:
            pickle.dump({
                "components": self.components,
                "metadata": self.component_metadata
            }, f)

    def load(self, path: str):
        """Load FAISS index and metadata"""
        self.index = faiss.read_index(f"{path}.index")
        with open(f"{path}.metadata", "rb") as f:
            data = pickle.load(f)
            self.components = data["components"]
            self.component_metadata = data["metadata"]
```

**Performance Comparison:**

| Metric | ChromaDB | FAISS |
|--------|----------|-------|
| **Setup Time** | Fast | Moderate |
| **Search Speed (4k components)** | ~5-10ms | ~1-2ms |
| **Memory Usage** | Higher | Lower |
| **Persistence** | Automatic | Manual save/load |
| **Learning Curve** | Easy | Moderate |

## Next Steps After Implementation

1. **Performance Optimization**: Switch to FAISS if needed for speed
2. **Advanced Retrieval**: Implement re-ranking and query expansion
3. **Component Quality**: Add filtering for higher-quality components
4. **Pedagogical Enhancement**: Integrate educational progression rules
5. **Evaluation Framework**: Develop comprehensive evaluation metrics

This implementation will give you hands-on experience with:
- Vector embeddings and similarity search
- RAG system architecture and design
- Educational AI and domain-specific applications
- System integration and evaluation

Good luck with your implementation! Start with ChromaDB for simplicity, then consider FAISS if you need performance optimization.
