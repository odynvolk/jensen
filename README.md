# jensen

A LLM powered Telegram bot.

### Prerequisites:

First you need to create a Telegram bot to interact with. 

- Telegram bot

See instructions (here)[https://core.telegram.org/bots].

You need Python 3 on your machine.

- Miniconda (optional)

For handling the packages needed.

```bash
$ curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh -o Miniconda3-latest-MacOSX-arm64.sh
$ chmod +x Miniconda3-latest-MacOSX-arm64.sh
$ ./Miniconda3-latest-MacOSX-arm64.sh -b -p $HOME/miniconda
$ source ~/miniconda/bin/activate
```

- LLM models, Telegram etc

For using Llama 2 models, Telegram API etc

```bash
$ pip install -r requirements.txt
```

- Configuration

Create a `.env` file with the following properties.

```
# LLM
MODEL_PATH=<path to model file>
N_CTX=<number of context>
MAX_TOKENS=<max tokens>

# Telegram
API_KEY=<api key>
```

### Usage

Start the application:

```bash
python ./jensen/app.py
```
