import os
import json
import faiss
import numpy as np
from tqdm import tqdm
import requests
from sentence_transformers import SentenceTransformer
from system_prompt import system_prompt_for_intention_detection, system_prompt_for_rag, system_prompt_for_part1

def build_faiss_index(input_path, index_path, model_name='all-MiniLM-L6-v2'):
    """
    input_path: the text dataset
    index_path: location to save the encoded vectors
    model_name: encoding models to vectors
    """
    print("Loading model...")
    model = SentenceTransformer(model_name)
    
    ext = os.path.splitext(input_path)[1].lower()
    names, blocks = [], []

    print(f"Reading files：{input_path}")

    if ext == ".txt":
        with open(input_path, 'r', encoding='utf-8') as f:
            all_test = f.read()
            blocks = all_test.split("\n\n")
            for block in blocks:
                names.append(block.split('\n')[0] if block.split('\n')[0].strip()[-1] != '?' else "")
    else:
        raise ValueError(f"Not support file type: {ext}")
    
    # embedding
    embeddings = model.encode(names, show_progress_bar=True, convert_to_numpy=True)
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    # save results
    faiss.write_index(index, index_path)
    meta_path = index_path + ".meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(blocks, f, ensure_ascii=False, indent=2)

def query_problem(query, index_path, model_name='all-MiniLM-L6-v2', top_k=3, vis=True):
    """
    Find the most similar query
    query: the input query to find most similar results
    index_path: vectorized dataset's path
    model_name: vectorization model to encode text
    top_k: number of results to return
    vis: set True if you want to print some results
    """
    model = SentenceTransformer(model_name)
    index = faiss.read_index(index_path)

    meta_path = index_path + ".meta.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        blocks = json.load(f)

    query_emb = model.encode([query], convert_to_numpy=True)
    xq = query_emb / np.linalg.norm(query_emb, axis=1, keepdims=True)
    xb = index.reconstruct_n(0, index.ntotal)  
    xb = xb / np.linalg.norm(xb, axis=1, keepdims=True)

    sims = np.dot(xq, xb.T)[0]
    top_idx = np.argsort(-sims)[:top_k]
    return_infos = ""
    for rank, idx in enumerate(top_idx):
        return_infos += f"[Top {rank + 1}] Similarity: {sims[idx]:.4f}\n"
        return_infos += blocks[idx] + "\n"+ "-" * 20 + '\n\n'
        if vis:
            print(f"[Top {rank + 1}] Similarity: {sims[idx]:.4f}")
            print(blocks[idx])
            print("-" * 100)
    return return_infos

def intention_detect(student_input):
    """
    Use LLM to detect user's intention
    Default use: Qwen3-8B, from SiliconFlow
    """
    url = "https://api.siliconflow.cn/v1/chat/completions"
    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "system",
                "content": system_prompt_for_intention_detection
            },
            {
                "role": "user",
                "content": student_input
            }
        ],
        "stream": False,
        "enable_thinking": False,
    }
    headers = {
        # you may apply for an apikey from https://api.siliconflow.cn
        "Authorization": "Bearer <your token>",
        "Content-Type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    result = response.json()['choices'][0]['message']['content']
    return result

def retrieval_augmented_problem_generation(extracted_results, student_input):
    """
    RAG
    Default use: Qwen3-8B, from SiliconFlow
    """
    
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "system",
                "content": system_prompt_for_rag
            },
            {
                "role": "user",
                "content": "The extracted result is:\n" + extracted_results + "\nAnd the student's input is:\n" + student_input
            }
        ],
        "stream": False,
        "enable_thinking": False,
    }
    headers = {
        "Authorization": "Bearer <your token>",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    result = response.json()['choices'][0]['message']['content']

    return result

def problem_generation(query):
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {
                "role": "system",
                "content": system_prompt_for_part1
            },
            {
                "role": "user",
                "content": "The query is:\n" + query
            }
        ],
        "stream": False,
        "enable_thinking": False,
    }
    headers = {
        "Authorization": "Bearer <your token>",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    result = response.json()['choices'][0]['message']['content']

    return result


def rag_main(student_input, file_path, index_path="problem_index.faiss", update=False):
    if not os.path.exists(index_path) or update:
        build_faiss_index(file_path, index_path)
    
    query = intention_detect(student_input)
    print("intention: ",query)
    part1_problem = problem_generation(query)
    extracted = query_problem(query, index_path)
    final_problem = retrieval_augmented_problem_generation(extracted_results=extracted, student_input=student_input)
    return part1_problem, final_problem



if __name__ == "__main__":
    file_path = "./IELTS.txt"
    student_input = "Last time, my oral performance on answering questions about my experience of grouping with foreign students. What theme should I exercise more?"
    #student_input = input()
    part1_problem, final_problem = rag_main(student_input=student_input, file_path=file_path)
    print("Model's generated problem:")
    print(part1_problem)
    print("===========")
    print(final_problem)









