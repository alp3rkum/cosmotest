import json
import re
import os

META_CONSTRAINTS = ["no_excessive_repetition", "no_prompt_copying", "is_not_a_list_of_constraints"]
# Cosmotest v2 - Kısıt Haritası
CONSTRAINTS_MAP = {
    0: ["is_not_empty","all_planets_listed"],
    1: ["is_not_empty", "no_earth","all_planets_listed"],
    2: ["no_earth", "is_json", "no_outside_text","json_planets_listed"],
    3: ["no_earth", "is_json", "has_5_items", "all_10_words","json_planets_listed"],
    4: ["no_earth", "is_json", "has_5_items", "all_10_words", "starts_with_g","json_planets_listed"],
    5: ["no_earth", "is_json", "has_5_items", "all_10_words", "starts_with_g", "correct_s_count","json_planets_listed"],
    6: ["no_earth", "is_json", "has_5_items", "all_10_words", "starts_with_g", "is_reverse_ordered", "json_planets_listed"],
    7: ["no_earth", "is_json", "has_5_items", "all_12_words", "has_double_name_caps", "uppercase_keys", "correct_moon_count", "even_word_count", "json_planets_listed"],
    8: ["no_earth", "is_json", "has_5_items", "all_10_words", "is_alphabetical_order", "planets_reversed", "correct_vowel_count","json_planets_listed"],
    9: ["is_not_empty", "no_earth", "exact_50_words", "unique_sentence_starts", "no_letter_e", "three_exclamations", "last_word_z", "no_digits"],
    10: ["is_not_empty", "no_earth", "exact_100_words", "four_sentences", "all_sentences_start_s", "has_3_planets", "no_commas", "ends_with_void", "one_color_per_sentence"]
}
SOLAR_SYSTEM_PLANETS = {"mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune","earth"}

class CosmotestEvaluator:
    def __init__(self, response_text):
        self.text = response_text.strip()
        self.json_data = None
        self.is_valid_json = self._check_json()
        self.planets_reference = ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"]

    def _check_json(self):
        try:
            clean_text = re.sub(r'```json|```', '', self.text).strip()
            self.json_data = json.loads(clean_text)
            return True
        except:
            return False

    def check_specific_constraint(self, name, key=None):
        text_l = self.text.lower()
        if name == "is_not_empty": return len(self.text) > 10
        if name == "no_earth": return "earth" not in text_l
        if name == "is_json": return self.is_valid_json
        
        # JSON verisini normalleştirme
        descriptions = []
        planet_names = []
        
        if self.is_valid_json:
            if isinstance(self.json_data, dict):
                # Eğer anahtar-değer yapısıysa
                for k, v in self.json_data.items():
                    if isinstance(v, str): descriptions.append(v)
                    planet_names.append(str(k).lower())
            elif isinstance(self.json_data, list):
                # Liste içindeki objeleri tara
                for item in self.json_data:
                    if isinstance(item, dict):
                        # 'name', 'planet' gibi anahtarları veya tüm string değerleri ara
                        vals = [str(v) for v in item.values() if isinstance(v, str)]
                        descriptions.extend(vals)
                        if 'name' in item: planet_names.append(str(item['name']).lower())
                        elif 'planet' in item: planet_names.append(str(item['planet']).lower())
                    elif isinstance(item, str):
                        descriptions.append(item)

        if name == "no_outside_text":
            c = re.sub(r'```json|```', '', self.text).strip()
            return c.startswith(('{', '[')) and c.endswith(('}', ']'))
        
        if name == "has_5_items": 
            return self.is_valid_json and len(self.json_data) >= 5
            
        if name == "all_10_words":
            if not descriptions: return False
            return all(len(d.split()) == 10 for d in descriptions)

        if name == "all_12_words":
            if not descriptions: return False
            return all(len(d.split()) == 12 for d in descriptions)
            
        if name == "starts_with_g":
            if not descriptions: return False
            return all(d.strip().upper().startswith('G') for d in descriptions)
            
        if name == "correct_s_count":
            if not self.is_valid_json: return False
            claimed = -1
            if isinstance(self.json_data, dict):
                claimed = self.json_data.get('s_count', -1)
            elif isinstance(self.json_data, list) and len(self.json_data) > 0:
                last_item = self.json_data[-1]
                if isinstance(last_item, dict):
                    claimed = last_item.get('s_count', -1)
            
            actual = text_l.count('s') - str(claimed).count('s')
            return str(claimed) == str(actual)
        
        if name == "no_excessive_repetition":
            words = self.text.lower().split()
            if len(words) < 20: return True
            # Basit bir n-gram kontrolü (ardışık 5 kelime tekrarı)
            for i in range(len(words) - 10):
                if words[i:i+5] == words[i+5:i+10]:
                    return False
            return True

        if name == "no_prompt_copying":
            banned_phrases = ["the story should", "must be exactly", "forbidden from using", "instruction:"]
            return not any(phrase in self.text.lower() for phrase in banned_phrases)

        if name == "is_not_a_list_of_constraints":
            # 1. Instruction Sızıntısı: Prompt'taki ana talimatın kopyalanması
            instruction_match = re.search(r"### Instruction:\n(.*?)\n", self.text, re.DOTALL)
            if instruction_match:
                instr_text = instruction_match.group(1).strip()
                # Eğer talimat metni (belli bir uzunluktaysa) cevapta aynen geçiyorsa
                if len(instr_text) > 15 and instr_text.lower() in self.text.lower():
                    return False

            constraints_raw = re.findall(r"-\s*(.*?)\n", self.text)
            for cons in constraints_raw:
                cons_clean = cons.strip()
                if len(cons_clean) > 20:
                    sample = cons_clean[:25].lower()
                    if sample in self.text.lower():
                        return False

            # 3. Papağan Kontrolü: Eğer cevap "The paragraph should be..." veya 
            # "The JSON object should..." gibi kısıtların açıklamasını yaparak başlıyorsa
            meta_leak_patterns = [
                "the paragraph should", "the json object should", 
                "write a short text", "must be exactly", "is forbidden"
            ]
            if any(pattern in self.text.lower() for pattern in meta_leak_patterns):
                return False
            
            return True
        
        if name == "is_alphabetical_order":
            if not descriptions: return False
            def is_sorted(text):
                words = [re.sub(r'[^\w]', '', w).lower() for w in text.split() if re.sub(r'[^\w]', '', w)]
                return all(words[i] <= words[i+1] for i in range(len(words)-1)) if len(words) > 1 else True
            return all(is_sorted(d) for d in descriptions)

        if name == "planets_reversed":
            if not planet_names: return False
            # Gezegen listesindeki isimlerin ters hallerini kontrol et (örn: 'yrucrem')
            reversed_refs = [p[::-1] for p in self.planets_reference]
            return any(p in planet_names for p in reversed_refs)

        if name == "correct_vowel_count":
            if not self.is_valid_json: return False
            vowels = "aeiou"
            results = []
            # Hem list hem dict yapısında 'vowel_count' ara
            items = self.json_data if isinstance(self.json_data, list) else self.json_data.get('planets', [self.json_data])
            for item in items:
                if isinstance(item, dict) and 'vowel_count' in item:
                    desc = str(item.get('description', ''))
                    actual = sum(1 for char in desc.lower() if char in vowels)
                    results.append(int(item['vowel_count']) == actual)
            return len(results) >= 5 and all(results)

        if name == "is_reverse_ordered":
            if not planet_names: return False
            # Sadece bilinen gezegenleri filtrele (mesafeyi ölçmek için)
            detected = [p for p in planet_names if p in self.planets_reference]
            if len(detected) < 2: return False
            # Referans listesindeki indekslerini bul
            indices = [self.planets_reference.index(p) for p in detected]
            # Ters sıralı mı? (İndeksler azalıyor olmalı)
            return all(indices[i] > indices[i+1] for i in range(len(indices)-1))
        
        if name == "uppercase_keys":
            if not self.is_valid_json: return False
            def check_keys(d):
                if isinstance(d, dict):
                    for k, v in d.items():
                        if not str(k).isupper(): return False
                        if not check_keys(v): return False
                elif isinstance(d, list):
                    for item in d:
                        if not check_keys(item): return False
                return True
            return check_keys(self.json_data)

        if name == "correct_moon_count":
            if not self.is_valid_json: return False
            # Referans uydu sayıları
            moons_ref = {
                "mercury": 0, "venus": 0, "mars": 2, 
                "jupiter": 95, "saturn": 146, "uranus": 28, "neptune": 16
            }
            results = []
            # JSON yapısını tarayıp MOON_COUNT değerlerini kontrol et
            items = self.json_data if isinstance(self.json_data, list) else self.json_data.get('PLANETS', [self.json_data])
            for item in items:
                if isinstance(item, dict) and 'MOON_COUNT' in item:
                    # Gezegen ismini bul (NAME veya PLANET anahtarından)
                    p_name = str(item.get('NAME') or item.get('PLANET') or "").lower()
                    if p_name in moons_ref:
                        results.append(int(item['MOON_COUNT']) == moons_ref[p_name])
            return len(results) >= 5 and all(results)

        if name == "even_word_count":
            # JSON string halindeki toplam kelime sayısını say
            raw_content = re.sub(r'```json|```', '', self.text).strip()
            word_count = len(raw_content.split())
            return word_count % 2 == 0

        if name == "exact_50_words":
            return len(self.text.split()) == 50

        if name == "unique_sentence_starts":
            sentences = [s.strip() for s in re.split(r'[.!?]+', self.text) if s.strip()]
            starts = [s[0].upper() for s in sentences]
            return len(starts) == len(set(starts))

        if name == "no_letter_e":
            return "e" not in self.text.lower()

        if name == "three_exclamations":
            return self.text.count('!') == 3

        if name == "last_word_z":
            words = re.sub(r'[^\w\s]', ' ', self.text).split()
            return words[-1].upper().startswith('Z') if words else False

        if name == "no_digits":
            return not any(char.isdigit() for char in self.text)

        if name == "exact_100_words":
            return len(self.text.split()) == 100

        if name == "four_sentences":
            sentences = [s for s in re.split(r'[.!?]+', self.text) if s.strip()]
            return len(sentences) == 4

        if name == "all_sentences_start_s":
            sentences = [s.strip() for s in re.split(r'[.!?]+', self.text) if s.strip()]
            return all(s.upper().startswith('S') for s in sentences) if sentences else False

        if name == "has_3_planets":
            found = sum(1 for p in self.planets_reference if p in text_l)
            return found >= 3

        if name == "no_commas":
            return "," not in self.text

        if name == "ends_with_void":
            clean_text = re.sub(r'[^\w\s]', '', self.text).strip().split()
            return clean_text[-1].lower() == "void" if clean_text else False

        if name == "one_color_per_sentence":
            colors = ["red", "blue", "green", "yellow", "black", "white", "silver", "golden", "purple", "orange", "brown", "grey"]
            sentences = [s.lower() for s in re.split(r'[.!?]+', self.text) if s.strip()]
            if not sentences: return False
            
            results = []
            for s in sentences:
                count = sum(1 for color in colors if f" {color} " in f" {s} ")
                results.append(count == 1)
            return all(results)
        
        if name == "all_planets_listed":
            res_low = self.text.lower()
            all_p = {"mercury", "venus", "earth", "mars", "jupiter", "saturn", "uranus", "neptune"}
            
            found = [p for p in all_p if p in res_low]
            
            if key == 0:
                return len(found) == 8
            if key == 8:
                return len(found) == 3
            
            seven_p = all_p - {"earth"}
            found_seven = [p for p in seven_p if p in res_low]
            
            return len(found_seven) == 7
        
        if name == "json_planets_listed":
            if not self.is_valid_json or not planet_names: 
                return False
            
            # JSON içinden çekilen gezegen isimlerini temizleyelim
            # planet_names listesi zaten check_specific_constraint başında doluyor
            all_p_no_earth = {"mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune"}
            found_in_json = [p for p in all_p_no_earth if p in planet_names]

            # Key 2: Dünya hariç tüm liste (7 adet) şart
            if key == 2:
                return len(found_in_json) == 7
            
            # Diğer JSON keyleri (3, 4, 5, 6, 7, 8): Prompt 5 adet istiyor
            return len(found_in_json) == 5

        if name == "has_double_name_caps":
            if not self.is_valid_json: return False
            # Hem dict hem list yapısında kontrol
            items_to_check = []
            if isinstance(self.json_data, list): items_to_check = self.json_data
            elif isinstance(self.json_data, dict):
                if 'planets' in self.json_data: items_to_check = self.json_data['planets']
                else: items_to_check = [self.json_data]

            results = []
            for item in items_to_check:
                if not isinstance(item, dict): continue
                name_val = str(item.get('name') or item.get('planet') or "").lower()
                desc_val = str(item.get('description') or "")
                if not name_val or not desc_val: continue
                
                # İsim desc içinde geçiyor mu?
                first_match = name_val in desc_val.lower()
                # ALL CAPS versiyonu geçiyor mu?
                second_match = name_val.upper() in desc_val
                results.append(first_match and second_match)
            
            return len(results) >= 5 and all(results)
            
        return False
        
def run_report():
    if not os.path.exists('test_outputs.json'):
        print("test_outputs.json bulunamadı.")
        return

    with open('test_outputs.json', 'r', encoding='utf-8') as f:
        results = json.load(f)

    print(f"\n{'KEY':<5} | {'SUCCESS':<10} | {'POINTS'}")
    print("-" * 35)

    # SKOR -1'DEN BAŞLIYOR (Cosmotest v1 mantığı korunuyor)
    total_cosmoscore = -1.0
    
    for res in results:
        ev = CosmotestEvaluator(res['response'])
        key = res['key']
        if key not in CONSTRAINTS_MAP: continue
        
        cons = CONSTRAINTS_MAP[key]
        meta_cons = META_CONSTRAINTS
        if not all(ev.check_specific_constraint(c, key=key) for c in meta_cons):
            passed = 0
        else:
            passed = sum(1 for c in cons if ev.check_specific_constraint(c, key=key))
        
        points_added = passed / len(cons)
        total_cosmoscore += points_added
        
        print(f"{key:<5} | {passed}/{len(cons):<8} | +{points_added:<6.2f}")

    print("-" * 35)
    print(f"FINAL COSMOSCORE: {total_cosmoscore:.2f}")
    print("=" * 35)

if __name__ == "__main__":
    run_report()