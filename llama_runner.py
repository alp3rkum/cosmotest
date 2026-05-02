import json
import requests
import time

def run_progressive_test(jsonl_path, server_url="http://localhost:8080/completion"):
    """
    Llama.cpp server üzerinden progressive testleri koşturan modül.
    """
    results = []
    
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            key = data['key']
            instruction = data['instruction']
            constraints = "\\n- ".join(data['constraints'])
            
            # Prompt hazırlama (Llama.cpp formatı)
            prompt = f"""### Instruction:
{instruction}

### Constraints:
- {constraints}

### Response:
"""
            
            payload = {
                "prompt": prompt,
                "temperature": 0.0, # Deterministic sonuç için kritik
                "n_predict": 600,
                "stop": ["###", "</s>", "Description:"]
            }
            
            print(f"Testing Key {key}...")
            start_time = time.time()
            
            try:
                response = requests.post(server_url, json=payload)
                response.raise_for_status()
                output = response.json().get('content', '').strip()
                
                duration = time.time() - start_time
                
                results.append({
                    "key": key,
                    "prompt": prompt,
                    "response": output,
                    "duration": round(duration, 2)
                })
                
                print(f"Done. (Time: {round(duration, 2)}s)")
                print("-" * 30)
                
            except Exception as e:
                print(f"Error at Key {key}: {e}")
                
    return results

if __name__ == "__main__":
    # Testi başlat
    test_results = run_progressive_test('cosmotest.jsonl')
    
    # Sonuçları kaydet
    with open('test_outputs.json', 'w', encoding='utf-8') as out_f:
        json.dump(test_results, out_f, indent=4, ensure_ascii=False)
    
    print("\nTest tamamlandı. Çıktılar 'test_outputs.json' dosyasına kaydedildi.")