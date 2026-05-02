# CosmoTest: An Experiment on an Effective LLM Benchmark

## Version: v0Proto

### Türkçe (TR)
Günümüzün son derece hareketli teknolojik dünyalarından olan metin tabanlı üretken yapay zekaların testinde kullanılan güncel genel kullanım benchmarkı **IFEVal**'ın yetersiz kaldığı noktalarda bu modelleri sınamak için geliştirmekte olduğum benchmark.

Talimatlara şekilsel olarak birebir uyma ve genel görevleri yapmayı ölçen IFEVal'de, 2026 itibariyle "frontier" modeller **%95** ve üzeri skorlar alabilmektedir, ancak IFEVal gibi benchmarklarda elde edilen bu yüksek başarılar gerçek hayata her zaman yansımamaktadır. Halüsinasyonlar, eksik aşamalar, çok kompleks görevleri yerine getirmede zorlanmalar gibi durumlar, IFEVal gibi benchmarkların, metin tabanlı yapay zeka modellerin gerçek hayatta kendilerinden beklenen işlerdeki performanslarını tam olarak ölçemediğini göstermektedir.

Bu yüzden, özellikle lokal yapay zeka modellerine ilgi duyan bir yazılım geliştirici olarak, küçük (SLM) ve büyük (LLM) dil modellerini sadece talimat takibi konusunda değil, cevaplarındaki bilgilerin doğruluğu, mantıksal tutarlılık ve gerçek dünyada kendilerinden beklenen kadar sayıdaki kısıtlara karşı gösterdiği performans konularında da test edip bu modellerin "gerçek dünya"da nerede olduğunu kısa sürede test etmemize yarayabilecek bir benchmark geliştirmeye karar verdim. Yapay zeka eğitim setlerinde en çok kullanılan konulardan birisi de Güneş Sistemi olduğu için, bu konularda modelleri test eden bir eğitim setiyle bunu yapmayı amaçladım. "CosmoTest" ismi de tam olarak buradan geliyor.

#### Artıları

CosmoTest'i oluştururken, IFEVal gibi 500'ün üstünde prompta gerek kalmadan, çok kısa sürede bir modelin kapasitesinin ortaya çıkmasını da amaçladığım için, Güneş Sistemi konusunda farklı farklı yüzlerce prompt yerine, sıfırdan başlayıp birbirinden zorlayıcı ve daha fazla kısıt içeren on bir prompttan oluşan bir test seti hazırladım. Bu sürümünde puanlama mantığı olarak, 0'dan başlayan key'lerin her biri için bütün kısıtlara tam uyması 1 puan, hiçbir kısıta uymaması 0 puan, en az bir kısıta uyması ise uyulan kısıt sayısının toplam kısıt sayısına oranı (örneğin 4/6) kadar puanlık bir sistem öngördüm. Bu sayede modelin sadece bir görevi tam yapıp yapamaması değil, o görevde nereleri yapabildiği ve nerelerde bocaladığı, hatta kendi ürettiği cevapları kontrol edebilip edemediği (Key 5) konuları da ön plana çıkabiliyor. IFEVal gibi bir modelin ne kadar "deterministik" davrandığını ölçerken, bunu modelin stokastik doğasını, verdiği bilgiler ve mantıkların yanlış olabileceği olasılığını da göz önünde bulundurarak yapmayı amaçlaması sebebiyle, IFEVal'den daha sağlam bir prensibe dayanan bir benchmark oluşturmaya çalıştım. Bu şekilde, IFEVal'de günümüzde ayyukaya çıkmış olan "plato"dan kaçınmayı, ya da en azından ileride onu kolayca öteleyebilmeyi hedefledim.

#### Eksikleri

Ancak CosmoTest'in bu sürümündeki doğrulama fonksiyonunda bazı kısıtlarla ilgili sıkıntılar yaşanıyor gibi gözüküyor, bunu Qwen3.6-Plus'ın testlerde Google Gemini 3 Flash'ten bile daha düşük sonuç alması sonrası verdiği cevapları incelerken fark ettim. Dolayısıyla CosmoTest benchmarkının bu sürümünü "faulty" olarak kabul ediyor, ancak yapay zeka dünyasının ihtiyaç duyduğuna inandığım bu projenin bu sürümünü, başlangıç noktasını belirtmesi açısından bu repoya yüklüyorum.
Ve CosmoTest IFEVal'ın aksine sadece Güneş Sistemi temalı promptlar içeriyor, ayrıca prompt ve senaryo sayısının azlığı da o modelin _genel performansı_ hakkında tam olarak bilgi vermeyebilir. Bu yüzden bir sonraki sürümünde daha fazla farklı senaryo içeren daha fazla prompt kullanarak ve yapay zekanın çıktı formatındaki olası değişiklikleri (özellikle modelden modele) göz önünde bulundurarak daha isabetli ve kapsamlı bir benchmark geliştireceğim.

### English (EN)

This is a benchmark I'm developing to test text-based generative AI models, a highly dynamic technology sector today, where the current general-purpose benchmark **IFEVal** falls short.

While IFEVal measures the ability to follow instructions precisely and perform general tasks, "frontier" models are achieving scores of **95%** and above by 2026. However, these high scores achieved in benchmarks like IFEVal don't always translate to real-world performance. Situations like hallucinations, missing steps, and difficulties in completing highly complex tasks demonstrate that benchmarks like IFEVal fail to fully measure the performance of text-based AI models in real-world tasks.

Therefore, as a software developer particularly interested in local AI models, I decided to develop a benchmark that would allow us to quickly test where small (SLM) and large (LLM) language models stand in the "real world," not only in terms of instruction following, but also in terms of the accuracy of the information in their responses, logical consistency, and their performance against a sufficient number of constraints expected of them in the real world. Since one of the most frequently used topics in AI training sets is the Solar System, I aimed to do this with a training set that tests models on this topic. The name "CosmoTest" comes from this.

#### Advantages

While creating CosmoTest, I also aimed to reveal a model's capabilities very quickly, without the need for over 500 prompts like in IFEVal. Therefore, instead of hundreds of different prompts on the Solar System, I prepared a test set consisting of eleven prompts, starting from scratch and containing increasingly challenging and more constrained elements. In this version, I envisioned a scoring system where, for each key starting from 0, 1 point is awarded for fully complying with all constraints, 0 points for not complying with any constraints, and a score equal to the ratio of the number of constraints met to the total number of constraints (e.g., 4/6). This allows the system to highlight not only whether the model can fully complete a task, but also where it succeeds and falters, and even whether it can verify its own generated responses (Key 5). Because IFEVal aims to measure how "deterministically" a model behaves by considering the stochastic nature of the model and the possibility that the information and logic it provides may be incorrect, I tried to create a benchmark based on a more robust principle. In this way, I aimed to avoid the "plateau" that has become prevalent in IFEVal today, or at least to easily postpone it in the future.

#### Deficiencies

However, it seems there are some issues with the validation function in this version of CosmoTest, related to certain limitations. I noticed this while examining the responses of Qwen3.6-Plus after it scored even lower than Google Gemini 3 Flash in tests. Therefore, I consider this version of the CosmoTest benchmark "faulty," but I am uploading this version of the project to this repository as a starting point, as I believe the AI ​​world needs this project. And unlike IFEVal, CosmoTest only includes prompts with a Solar System theme; the limited number of prompts and scenarios may not provide complete information about the overall performance of the model. Therefore, in the next version, I will develop a more accurate and comprehensive benchmark by using more prompts with more different scenarios and considering possible changes in the AI ​​output format (especially from model to model).

### Test Results

SmolLM-135M-Instruct.Q8_0 => CosmoTest 0
gemma-3-270m-it-Q8_0 => CosmoTest 1.18
smollm2-360m-instruct-q8_0 => CosmoTest 1.9
Qwen2.5-0.5B-Instruct-Q6_K_L => CosmoTest 3.46
Qwen3-0.6B-Q4_0 => CosmoTest 5.08
google_gemma-3-1b-it-IQ4_XS => CosmoTest 5.06

Google Gemini 3 Flash => CosmoTest 6.66 (non-local)
Google Gemini 3 Thinking => CosmoTest 7.16 (non-local)
Google Gemini 3.1 Pro => CosmoTest 7.41 (non-local)
ChatGPT (Standard) => CosmoTest 6.96 (non-local)
Qwen3.6-Plus => CosmoTest 5.89 (non-local)

TR: Bu test sonuçları, Qwen2.5 üzerinde yaptığım farklı kuantizasyonlarla yapılan testlerde de aynı skorda çıkmıştır. Dolayısıyla CosmoTest'i yapan bir modelin vereceği sonuç kuantizasyondan bağımsızdır denilebilir.
EN: These test results were the same as those obtained in tests I conducted with different quantizations on Qwen2.5. Therefore, it can be said that the result given by a model performing CosmoTest is independent of the quantization.

### How To Test

TR: Bu benchmarkı geliştirirken lokalde Llama.cpp ile elimdeki lokal GGUF modelleriyle llama-server açtıktan sonra llama_runner.py'yi komut isteminde çalıştırdım. Ardından çıkan sonucu llama_valer.py çalıştırarak değerlendirdim. ChatGPT, Gemini, Qwen Chat gibi İnternet tabanlı chatbot uygulamalarında, deneme için cosmotest.jsonl (Qwen Chat için .json) ve test_outputs.json dosyalarını mesaja eklenti olarak iliştirerek modele cosmotest dosyasındaki promptları işleyip sonuçları aynen test_outputs.json'daki gibi vermesini isteyerek testinizi gerçekleştirebilirsiniz.
EN: While developing this benchmark, I created a llama-server locally using Llama.cpp with my existing local GGUF models, then ran llama_runner.py in the command prompt. Afterwards, I evaluated the output by running llama_valer.py. For web-based chatbot applications like ChatGPT, Gemini, and Qwen Chat, you can perform your test by attaching cosmotest.jsonl (or .json for Qwen Chat) and test_outputs.json files as attachments to messages, instructing the model to process the prompts from the cosmotest file and return the results exactly as in test_outputs.json.
