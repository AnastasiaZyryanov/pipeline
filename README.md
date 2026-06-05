## **Descrizione del progetto** 

Questo progetto implementa una pipeline configurabile per l'analisi dei sentimenti e l'estrazione di parole chiave da recensioni degli utenti. 

La pipeline è composta da quattro moduli eseguiti in sequenza (ogni modulo riceve in input il risultato prodotto dal modulo precedente e lo elabora ulteriormente): 

1. Chunker 

2. Cleaner 

3. Sentiment Analyzer 

4. Keyword Extractor 

La realizzazione concreta dei moduli (e dei runner corrispondenti se siano necessari) viene scelta dall’utente in un file di configurazione JSON. 

Il file di input, contenente recensioni, deve essere fornito in formato CSV e collocato nella cartella `data/comments.csv` . 

Al termine dell'esecuzione viene generato il file `data/output.json` . 

## **Avvio del progetto** 

Per eseguire la pipeline: `uv run python scripts/user_script.py` 

Il programma richiede all'utente di fornire il path del file di configurazione JSON, che viene validata automaticamente. Il file deve contenere i parametri per ciascun modulo e runner corrispondenti. 

Alcuni modelli Hugging Face richiedono autenticazione. In tal caso è necessario esportare il token prima dell'avvio: `export HF_TOKEN="hf_your_token_here"` 

## **Moduli** 

## **1. Chunker** 

Il modulo Chunker divide le recensioni in segmenti più piccoli per facilitarne l'elaborazione successiva. 

## **SentenceChunkerFunction** 

Utilizza `nltk.tokenize.sent_tokenize()` per suddividere il testo in frasi secondo regole linguistiche specifiche. 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|max_tokens|No|lunghezza massima di chunk|
|language|No|lingua utilizzata dal tokenizer di NLTK|

Il  parametro `max_tokens` ,  viene  utilizzato  come  meccanismo  preventivo  per  limitare  la dimensione dell'input destinato ai moduli successivi, in particolare SawithAttention. Il valore predefinito è 350 tokens che è inferiore al limite massimo supportato dai modelli Transformer (512 token) per lasciare un margine di sicurezza durante la tokenizzazione e l'elaborazione del prompt. Il valore 350 è calcolato in base alla seguente estimazione: 1 token ≈ 0.75 words,  1 word ≈ 1.33 tokens 


## **SemanticChunkerFunction** 

Suddivide il testo in frasi e successivamente raggruppa le frasi semanticamente correlate in chunk più ampi. 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|embedding_model|Sì|modello per generare gli embedding|
|percentile|Sì|soglia per individuare i punti di separazione tra chunk|
|overlap|Sì|numero di token ripetuti in chunk consecutivi|
|max_tokens|No|lunghezza massima di chunk|
|language|No|lingua utilizzata dal tokenizer di NLTK|



Il  parametro `max_tokens` ,  viene  utilizzato  come  meccanismo  preventivo  per  limitare  la dimensione dell'input destinato ai moduli successivi, in particolare SawithAttention. Il valore predefinito è 350 tokens che è inferiore al limite massimo supportato dai modelli Transformer (512 token) per lasciare un margine di sicurezza durante la tokenizzazione e l'elaborazione del prompt. Il valore 350 è calcolato in base alla seguente estimazione: 1 token ≈ 0.75 words,  1 word ≈ 1.33 tokens 

Valori più bassi di `percentile` producono generalmente un numero maggiore di chunk, mentre valori più elevati generano chunk più grandi. 

## **2. Cleaner** 

Il modulo Cleaner esegue eventuali operazioni di pulizia del testo. 

## **NoClean** 

Non esegue alcuna elaborazione e restituisce il testo invariato. Non richiede parametri. 

## **CleanerWithScript** 

Esegue uno script Python fornito dall'utente. 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|script|Sì|path dello script Python|
|entrypoint|Sì|nome della funzione da eseguire|



## **3. Sentiment Analyzer** 

## **SAwithLLM** 

Esegue l'analisi dei sentimenti utilizzando un LLM. 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|runner|Sì|configurazione del runner|
|generated_responses|Sì|numero di risposte generate per ogni chunk|
|system_prompt|No|istruzioni fornite a LLM|
|user_template|No|template di risposta fornito a LLM|
|max_tokens|No|numero massimo di token generati|
|temperature|No|controlla il livello di casualità della generazione|



Il prompt predefinito è progettato per produrre una classificazione a cinque livelli: molto negativo, negativo, neutro, positivo e molto positivo. 

Il parametro `generated_responses` si utilizza per ridurre la variabilità delle risposte generate da LLM, calcolando il valore medio dei risultati ottenuti (per queso le etichette vengono convertite in valori numerici e, dopo averne calcolato la media, il risultato viene riconvertito in una stringa). 

Il parametro `temperature` controlla la variabilità delle risposte generate dal modello. Se il valore di `generated_responses` > 1, la `temperature` deve essere diversa da 0. 

## **SAwithAttention** 

Esegue l'analisi dei sentimenti utilizzando un modello Transformer di Hugging Face. 

**Parametro Obbligatorio Descrizione** model No nome del modello Hugging Face 

Modello predefinito: `cardiffnlp/twitter-roberta-base-sentiment-latest` 

I modelli Transformer supportano una lunghezza massima di input pari a 512 token. 

Sequenze più lunghe vengono automaticamente troncate. Per ridurre il rischio di perdita di informazione i moduli Chunker limitano la dimensione dei chunk generati. 

## **4. Keyword Extractor** 

## **KEwithLLM** 

Estrae parole chiave utilizzando LLM. 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|runner|Sì|configurazione del runner|
|system_prompt|No|istruzioni fornite a LLM|
|user_template|No|template di risposta fornito a LLM|
|max_tokens|No|numero massimo di token generati|



## **KEwithKeyBERT** 

Il modulo utilizza un approccio ibrido: estrae parole chiave utilizzando KeyBERT e passa i rusultati ottenuta a LLM per il raffinamento. 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|runner|Sì|configurazione del runner|
|embedding_model|Sì|modello utilizzato da KeyBERT|
|top_n|Sì|numero massimo di keyword restituite|
|keyphrase_size|Sì|lunghezza massima delle keyphrase|
|stopwords|Sì|lista di stopword|
|min_df|Sì|frequenza minima richiesta per considerare un termine<br>candidato|
|system_prompt|No|istruzioni fornite a LLM|



|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|user template|No|Template di risposta fornito a LLM|
|seed_keywords|No|esempi per orientare la ricerca delle keyword|
|use_maxsum|No|favorisce keyword più diverse tra loro|
|use_mmr|No|bilancia rilevanza e diversità|
|diversity|No|intensità della diversificazione (se use_mmr=True) ,<br>valore di default uguale a 0.5|
|nr_candidates|No|numero di candidati valutati da KeyBERT, valore di<br>default uguale a 20|



L’ `embedding_model` ha i parametri `name` (obbligatorio), `dtype` (prende i valori float16 or float32) e `device` (prende i valori cuda o cpu). 

Le  keyword  generate  dal  modello  vengono  filtrate  mantenendo  esclusivamente  i  termini effettivamente presenti nel documento originale. 

## **Runner** 

I moduli basati su LLM richiedono un runner per l'esecuzione del modello. 

## **OllamaRunner** 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|model|Sì|modello LLM|
|api_key|No|chiave di autenticazione|
|seed|No|inizializza il generatore di numeri casuali (per generare le risposte più<br>variate)|



## **VllmRunner** 

|**Parametro**|**Obbligatorio**|**Descrizione**|
|---|---|---|
|model|Sì|modello LLM|
|api_key|No|chiave di autenticazione|
|seed|No|inizializza il generatore di numeri casuali (per generare le risposte più<br>variate)|
|gpu|No|scheda video utilizzare|
|port|No|porta di rete|



# Struttura del progetto

## `src/pipeline_lib/`

- **`config/`**
  - `schema.py`: JSON-schema utilizzata per validare la configurazione fornita dall’utente.
  - `validator.py`: valida la configurazione fornita dall’utente a base di JSON-schema
- **`core/`**
  - `builder.py`: costruisce la pipeline sulla base della configurazione validata.
  - `factory.py`: crea le istanze di ogni modulo a base di configurazione fornita.
  - `module_base.py`: classe astratta per tutti i moduli.
- **`modules/`**
  - `Chunker.py`
  - `Cleaner.py`
  - `SentimentAnalyzer.py`
  - `KeywordExtractor.py`
  - `LLMRunner.py`
- **`servers/`**
  - `ollama_server.py`: avvia e ferma automaticamente un server Ollama quando almeno un modulo utilizza un OllamaRunner.
  - `vllm_server.py`: avvia e ferma automaticamente un server vLLM per ogni modulo che utilizza VLLMRunner.
- `runner.py`
- `__init__.py`

## `scripts/`

Contiene alcuni esempi di configurazione utilizzabili come riferimento per costruire nuove pipeline.