# jensen

A LLM powered Telegram bot.

## Prerequisites:

### Telegram bot

First you need to create a Telegram bot to interact with. See instructions [here](https://core.telegram.org/bots).

### LLM model

You need a LLM in GGUF format. You can find quite a few through [TheBloke on HuggingFace](https://huggingface.co/TheBloke)
who has done an enormous service to the community by converting different models to GGUF and quantized them. Pick one that suits your
needs and hardware requirements.

### Llama.cpp

You need [Llama.cpp](https://github.com/ggml-org/llama.cpp) in order to be able to run a model on your machine. There are other 
alternatives out there like Ollama and LM Studio, but I prefer llama.cpp due to it being lightweight. It's easy to install through Brew.

```bash
$ brew install lama.cpp
```

### Python

You need Python 3 on your machine.

- Micromamba (optional)

For handling the packages needed for different enivronments. Easy to install with asdf.

```bash
$ asdf install
$ micromamba create -n jensen python=3.13
$ micromamba activate jensen
```

- LLMs, Telegram etc

For using LLM models, Telegram API etc

```bash
$ pip install -r requirements.txt
```

## Configuration

Copy ./start-llama-cpp-server-example.sh to ./start-llama-cpp-server.sh and enter the model and settings you want.

Create a `.env` file with the following properties.

```
# Telegram
API_KEY=<api key, string> (mandatory)
POLL_INTERVAL=<interval to use when polling Telegram as seconds, float>
```

## Usage

Start the llama.cpp server:

```bash
./start-llama-cpp-server.sh
```

Start the application:

```bash
python ./jensen/app.py
```

And you're off to the races.
