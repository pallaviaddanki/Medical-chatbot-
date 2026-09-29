import json
import os

import faiss
import numpy as np

from sentence_transformers import SentenceTransformer
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)


class MedicalRAG:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        print()
        print("Starting Medical RAG system...")

        # ----------------------------------------------------
        # FIND PROJECT DIRECTORY
        # ----------------------------------------------------

        base_dir = os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )

        # ----------------------------------------------------
        # MEDICAL DATA FILE
        # ----------------------------------------------------

        data_path = os.path.join(
            base_dir,
            "data",
            "medical_faq.json"
        )

        if not os.path.exists(data_path):

            raise FileNotFoundError(
                f"Medical knowledge base not found:\n{data_path}"
            )

        # ----------------------------------------------------
        # LOAD MEDICAL DATA
        # ----------------------------------------------------

        with open(
            data_path,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(file)

        print(
            f"Loaded {len(self.documents)} medical documents."
        )

        # ====================================================
        # LOAD EMBEDDING MODEL
        # ====================================================

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print(
            "Embedding model loaded successfully."
        )

        # ====================================================
        # CREATE DOCUMENT TEXT
        # ====================================================

        texts = []

        for item in self.documents:

            question = item.get(
                "question",
                ""
            )

            answer = item.get(
                "answer",
                ""
            )

            combined_text = (
                question
                + " "
                + answer
            )

            texts.append(
                combined_text
            )

        # ====================================================
        # CREATE EMBEDDINGS
        # ====================================================

        embeddings = self.embedding_model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embeddings = embeddings.astype(
            "float32"
        )

        # ====================================================
        # CREATE FAISS INDEX
        # ====================================================

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings
        )

        print(
            f"FAISS index created with {len(texts)} documents."
        )

        # ====================================================
        # LOAD FLAN-T5
        # ====================================================

        print("Loading FLAN-T5 model...")

        self.tokenizer = AutoTokenizer.from_pretrained(
            "google/flan-t5-base"
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            "google/flan-t5-base"
        )

        # Avoid the tied-weight warning
        self.model.config.tie_word_embeddings = False

        print(
            "FLAN-T5 model loaded successfully."
        )

        print(
            "Medical RAG system loaded successfully."
        )

    # ========================================================
    # RETRIEVE RELEVANT DOCUMENTS
    # ========================================================

    def retrieve(
        self,
        query,
        top_k=3
    ):

        # ----------------------------------------------------
        # CREATE QUERY EMBEDDING
        # ----------------------------------------------------

        query_embedding = self.embedding_model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = query_embedding.astype(
            "float32"
        )

        # ----------------------------------------------------
        # SEARCH FAISS
        # ----------------------------------------------------

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        # ----------------------------------------------------
        # COLLECT RESULTS
        # ----------------------------------------------------

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < len(self.documents):

                document = self.documents[index]

                results.append({
                    "score": float(score),

                    "question": document.get(
                        "question",
                        ""
                    ),

                    "answer": document.get(
                        "answer",
                        ""
                    )
                })

        return results

    # ========================================================
    # GENERATE MEDICAL RESPONSE
    # ========================================================

    def generate_response(
        self,
        query
    ):

        # ----------------------------------------------------
        # RETRIEVE INFORMATION
        # ----------------------------------------------------

        retrieved = self.retrieve(
            query,
            top_k=3
        )

        if not retrieved:

            return (
                "I could not find relevant information "
                "in my medical knowledge base."
            )

        # ----------------------------------------------------
        # CREATE CONTEXT
        # ----------------------------------------------------

        context_parts = []

        for item in retrieved:

            context_parts.append(
                "Question: "
                + item["question"]
                + "\n"
                + "Information: "
                + item["answer"]
            )

        context = "\n\n".join(
            context_parts
        )

        # ----------------------------------------------------
        # CREATE PROMPT
        # ----------------------------------------------------

        prompt = f"""
You are MedAI, a medical information assistant.

Your job is to provide simple and educational
medical information.

IMPORTANT RULES:

1. Use only the information provided in the context.
2. Do not diagnose diseases.
3. Do not prescribe medicines.
4. Do not recommend specific medication doses.
5. Do not invent medical information.
6. If the answer is not available in the context,
   clearly say that you do not have enough information.
7. Encourage the user to consult a qualified healthcare
   professional when appropriate.
8. Keep the answer short and easy to understand.

Medical knowledge context:

{context}

User question:

{query}

Answer:
"""

        # ====================================================
        # TOKENIZE
        # ====================================================

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=512
        )

        # ====================================================
        # GENERATE ANSWER
        # ====================================================

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=150,
            do_sample=False
        )

        # ====================================================
        # DECODE
        # ====================================================

        answer = self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

        answer = answer.strip()

        # ====================================================
        # FALLBACK
        # ====================================================

        if not answer:

            return (
                "I could not generate a response. "
                "Please try asking your question again."
            )

        return answer