# jensen

A LLaMA 2 powered Telegram bot.

## Prerequisites:

### Telegram bot

First you need to create a Telegram bot to interact with. See instructions [here](https://core.telegram.org/bots).

### LLaMA 2 model

You need a LLaMA 2 model in GGML format. You can find quite a few through [TheBloke on HuggingFace](https://huggingface.co/TheBloke)
who has done an enormous service to the community by converting different models to GGML and quantized them. Pick one that suits your
needs and hardware requirements.

### Python

You need Python 3 on your machine.

- Micromamba (optional)

For handling the packages needed for different enivronments. Easy to install with asdf.

```bash
$ asdf install
$ micromamba create -n jensen python=3.13
$ micromamba activate jensen
```

- LLaMA 2, Telegram etc

For using LLaMA 2 models, Telegram API etc

```bash
$ pip install -r requirements.txt
```

## Configuration

Create a `.env` file with the following properties.

```
# LLM
MODEL_PATH=<path to model file, string> (mandatory)
MAX_TOKENS=<max tokens, int>
N_CTX=<number of context, int>
N_GPU_LAYERS<how many layers to offload to the GPU, int>
N_THREADS=<number of threads to use for Llama usage, int>
USE_MLOCK=<force the system to keep the model in RAM., bool>

PROMPT_FORMAT=<which prompt format to use, string>

# Telegram
API_KEY=<api key, string> (mandatory)
POLL_INTERVAL=<interval to use when polling Telegram as seconds, float>
```

## Usage

Start the application:

```bash
python ./jensen/app.py
```
