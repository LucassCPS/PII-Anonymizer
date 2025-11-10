# PII-Anonymizer

Este projeto implementa um conjunto de testes para modelos de linguagem em ambiente local utilizando o **Docker Desktop** com o **Model Runner**.  A aplicação foi desenvolvida em Python e utiliza os modelos hospedados no **Model Hub do Docker**.

---

## Requisitos

Antes de iniciar, verifique se você possui os seguintes componentes instalados:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Docker Model Runner](https://docs.docker.com/ai/model-runner/)

---

## Instalação

### 1. Clonar o repositório

```bash
git clone https://github.com/LucassCPS/PII-Anonymizer.git
cd PII-Anonymizer
```
---

## Configuração do Model Runner

Certifique-se de que o **Docker Desktop** está em execução e que o **Model Runner** está instalado. Siga as instruções oficiais:  
[Documentação do Model Runner (Docker)](https://docs.docker.com/ai/model-runner/)

---

## Modelos Necessários

Baixe e registre os modelos listados abaixo diretamente do **Model Hub**:

| Variável de ambiente    | Nome do modelo                           | Link para o Docker Hub                                                                             |
| ----------------------- | ---------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `MODEL_GEMMA3_QAT_4B`   | `ai/gemma3-qat:4B-UD-Q4_K_XL`            | [🔗 Docker Hub - Gemma3 QAT 4B](https://hub.docker.com/r/ai/gemma3-qat)                            |
| `MODEL_GEMMA3_QAT_270M` | `ai/gemma3-qat:270M-UD-Q4_K_XL`          | [🔗 Docker Hub - Gemma3 QAT 270M](https://hub.docker.com/r/ai/gemma3-qat)                          |
| `MODEL_SMOLL3_Q4`       | `ai/smollm3:Q4_K_M`                      | [🔗 Docker Hub - SmolLM3 Q4](https://hub.docker.com/r/ai/smollm3)                                  |
| `MODEL_SMOLL3_Q8`       | `ai/smollm3:Q8_0`                        | [🔗 Docker Hub - SmolLM3 Q8](https://hub.docker.com/r/ai/smollm3)                                  |
| `MODEL_QWEN3_06B`       | `ai/qwen3:0.6B-Q4_K_M`                   | [🔗 Docker Hub - Qwen3 0.6B](https://hub.docker.com/r/ai/qwen3)                                    |
| `MODEL_QWEN3_8B`        | `ai/qwen3:8B-Q4_K_M`                     | [🔗 Docker Hub - Qwen3 8B](https://hub.docker.com/r/ai/qwen3)                                      |
| `MODEL_GRANITE4_TINY`   | `ai/granite-4.0-h-tiny:7B`               | [🔗 Docker Hub - Granite 4.0 Tiny](https://hub.docker.com/r/ai/granite-4.0-h-tiny)                 |
| `MODEL_MISTRAL_NEMO`    | `ai/mistral-nemo:12B-Q4_K_M`             | [🔗 Docker Hub - Mistral Nemo 12B](https://hub.docker.com/r/ai/mistral-nemo)                       |
| `MODEL_DEEPSEEK`        | `ai/deepseek-r1-distill-llama:8B-Q4_K_M` | [🔗 Docker Hub - DeepSeek R1 Distill LLaMA](https://hub.docker.com/r/ai/deepseek-r1-distill-llama) |
| `MODEL_LLAMA32_3B_Q4`   | `ai/llama3.2:3B-Q4_K_M`                  | [🔗 Docker Hub - LLaMA 3.2 3B Q4](https://hub.docker.com/r/ai/llama3.2)                            |
| `MODEL_LLAMA32_1B_Q8`   | `ai/llama3.2:1B-Q8_0`                    | [🔗 Docker Hub - LLaMA 3.2 1B Q8](https://hub.docker.com/r/ai/llama3.2)                            |

Baixe cada modelo executando o comando abaixo (substitua pelo nome do modelo):

```bash
docker pull ai/gemma3-qat:270M-UD-Q4_K_XL
```

---

## Execução

Após configurar o ambiente, inicie o **Model Runner** com os modelos carregados e execute a aplicação através de:

```bash
docker compose build && docker compose up -d && docker compose run --rm -T app python -u main.py
```

Desligue o ambiente através do comando:
```bash
docker compose down
```


**Obs. 1: Certifique-se de que o Model Runner está rodando no Docker Desktop. A aplicação consumirá os modelos através das chamadas configuradas via API local.**

**Obs. 2: Altere os parâmetros de execução diretamente no main.py (modelo, prompt, temperatura, numero de linhas do dataset e etc.)**
