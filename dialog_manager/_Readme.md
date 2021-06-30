## Notes
*Intent* and *dialogue act* are more or less synonymous.

## actions
actions.py contains the communication to the bot brain

Depending on the latest detected intent, slots are set with the detected entities and send to the bot brain.

## domain
The domain contains every action, intents, entities and slots. It's also where the bot responses are defined.

## data
nlu.yml contains the language dataset that is used to detect the intents \
rules.yml contains the basic rules the dialogue manager should follow \
stories.yml contains user stories the model can be trained on. The dialogue manager decides whether to fallback on the rules or use the conversation paths in the stories.
## models
Contains the trained models

## config
Contains configurations for the NLU pipeline and dialogue management classification


## Usage

* Start Rasa action server by running `rasa run actions`
* Run `rasa shell` to interact with the bot
    - it should be able to detect the intents specified in nlu.yml
* You can also run `rasa interactive` to train a model interactively

## Example

Your input: *Can you move the stone block here*? \
Intent that should be detected: **ask_move_block** \
Entities that should be detected are: *stone*, *here* \
The action **MoveBlock** with the filled slots **which_block** and **position** are send to the bot brain.



