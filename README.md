# jensen

A Llama 2 powered Telegram bot.

## Prerequisites:

### Telegram bot

First you need to create a Telegram bot to interact with. See instructions [here](https://core.telegram.org/bots).

### Llama 2 model

You need a Llama 2 model in GGML format. You can find quite a few through [TheBloke on HuggingFace](https://huggingface.co/TheBloke)
who has done an enormous service to the community by converting different models to GGML and quantized them. Pick one that suits your
needs and hardware requirements.

### Python

You need Python 3 on your machine.

- Miniconda (optional)

For handling the packages needed for different enivronments.

```bash
$ curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o Miniconda3-latest-MacOSX-arm64.sh
$ chmod +x Miniconda3-latest-MacOSX-arm64.sh
$ ./Miniconda3-latest-MacOSX-arm64.sh -b -p $HOME/miniconda
$ source ~/miniconda/bin/activate
```

- Llama 2, Telegram etc

For using Llama 2 models, Telegram API etc

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

# Telegram
API_KEY=<api key, string> (mandatory)
POLL_INTERVAL=<interval to use when polling Telegram as seconds, float>
```

## Usage

Start the application:

```bash
python ./jensen/app.py
```
