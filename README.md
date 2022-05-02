# Progetto software cyberscurity (gruppo 9)

## Table of contents
1. [Prerequisites](#prerequisites)
2. [Setup](#setup)
3. [Usage](#usage)

## Prerequisites

To run this program you must have the following installed:
- [Node.js/npm](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) 10 or higher
- Java 11 or higher
- Python 3.6 or higher

## Setup
Clone this repo:

```
git clone https://github.com/alema-r/progetto-software-cybersecurity.git
cd progetto-software-cybersecurity
```

In order to compile contracts you have to 
- download @openzeppelin contracts 
- install the solidity compiler. 

You can download @openzeppelin contracts by executing the command:

`npm install @openzeppelin/contracts`

To install the compiler, follow the instructions for your OS.

### Linux
1. Download the compiler and save it in /usr/local/bin/ with the name solc:

`sudo curl -L https://github.com/ethereum/solidity/releases/download/v0.8.12/solc-static-linux -o /usr/local/bin/solc`

2. Make it executable:

`chmod +x /usr/local/bin/solc`

Then you can execute the `setup.sh` script and specify flags.
```
usage: setup.sh [-dmr] [-s|-t]
  -d, --deploy            deploy a new blockchain
  -m, --model-checker     compile with SMTCHECKER
  -s, --seeding           creates a demo scenario in the blockchain, 
                          only use with -d option
  -t, --run-test          run all python tests (do not use with -s)
  -r, --req               install python requirements
  -v, --venv              initialize a python virtual environment
  -h, --help              shows this message and exit
```

For example you can run:

`./setup.sh -v -r -d -s`

This will create a python virtual environment under the env folder, install all python requirements, create a test blockchain, compile all contracts and then it will run the seeding script.

### Windows
1. Download the compiler from https://github.com/ethereum/solidity/releases.
2. Either add it to PATH or move it in the project directory

Then you'll have to deploy a test blockchain by executing:

`npx quorum-wizard -q`

Then start the blockchain and execute the following (from within the scripts folder):

```
python3 compile.py
python3 deploy_contracts.py
python3 seeding.py
```

## Usage
To start the application execute the `main.py` script.

`python3 main.py`
