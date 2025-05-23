import os
import yaml


def parse_yaml(config_path):
    """
    Reads and parses a YAML configuration file.
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        if not config:
            raise ValueError(f"Configuration file {config_path} is empty or invalid.")
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file {config_path} not found.")
    except yaml.YAMLError as e:
        raise ValueError(f"Error parsing YAML file {config_path}: {e}")

    return config


def validate_config(config):
    """
    Validates the base structure of the configuration file.
    Ensures required keys are present and correctly formatted.
    """
    required_keys = [
        'testIterations', 'numberOfConditions', 'testItemNumber', 'testName',
        'trialIterations', 'trialItemNumber', 'trialCondition', 'trialAudioDirectory',
        'conditions', 'answer_dir', 'consent_info', 'break','trapQuestions','language'
    ]

    missing_keys = [key for key in required_keys if key not in config]
    if missing_keys:
        raise ValueError(f"Missing required configuration keys: {missing_keys}")

    if ('DRT' in config) and ('MRT' in config):
        raise ValueError("Configuration must define only one test type: 'DRT' or 'MRT', not both.")

    if 'DRT' not in config and 'MRT' not in config:
        raise ValueError("Configuration must contain either 'DRT' or 'MRT'.")

    # Additional validation for nested fields
    if 'DRT' in config:
        if 'wordItemDirectory' not in config['DRT'] or 'audioDirectory' not in config['DRT'] or "instructions" not in config["DRT"]:
            raise ValueError("Missing required DRT configuration keys.")
    if 'MRT' in config:
        if 'wordItemDirectory' not in config['MRT'] or 'audioDirectory' not in config['MRT'] or "instructions" not in config["MRT"]:
            raise ValueError("Missing required MRT configuration keys.")
    return True


def augment_config(config):
    """
    Adds additional configuration details based on DRT or MRT mode.
    """
    # Get language from config (default to 'en' if not set)
    language = config.get("language", "en")

    # Translations for different languages (DRT & MRT)
    translations = {
        "en": {
            "DRT": {
                "home_info": (
                    "Today, you will participate in an experiment designed to evaluate the intelligibility "
                    "of processed speech samples. During the test, you will see a pair of words displayed "
                    "side-by-side while listening to a single word. Your task is to indicate which of the two "
                    "words was spoken by the talker. Please use headphones to complete the task. Thank you for your participation!"
                ),
                "startButtonname": "Start DRT Test",
                "testHTML": "dtest.html",
                "trial_temp": "triald.html"
            },
            "MRT": {
                "home_info": (
                    "In this experiment, you will listen to a word and select the correct word from a set of choices. "
                    "This helps assess how clearly speech can be understood. Please wear headphones for accurate results."
                ),
                "startButtonname": "Start MRT Test",
                "testHTML": "mtest.html",
                "trial_temp": "trialm.html"
            }
        },
        "gr": {
            "DRT": {
                "home_info": (
                    "Heute werden Sie an einem Experiment teilnehmen, bei dem die Verständlichkeit von kodierten Sprachaufnahmen bewertet werden soll. Während des Tests werden Sie ein Wortpaar nebeneinander sehen, während Sie ein einzelnes Wort hören. Ihre Aufgabe ist es, zu erkennen, welches der beiden Wörter von dem Sprecher gesprochen wurde. Bitte benutzen Sie Kopfhörer für den Test. Vielen Dank für Ihre Teilnahme!"
                ),
                "startButtonname": "DRT Test starten",
                "testHTML": "dtest_gr.html",
                "trial_temp": "triald_gr.html"
            },
            "MRT": {
                "home_info": (
                    "Dieser Test wird als modifizierter Reimtest bezeichnet. Dieser Test wurde entwickelt, um die Verständlichkeit von Sprache zu bewerten."
                ),
                "startButtonname": "MRT Test starten",
                "testHTML": "mtest_gr.html",
                "trial_temp": "trialm_gr.html"
            }
        }
    }

    # Default to English if the selected language is not available
    lang_config = translations.get(language, translations["en"])

    # Check for mode (DRT or MRT) and update config accordingly
    if "DRT" in config:
        mode = "DRT"
    elif "MRT" in config:
        mode = "MRT"
    else:
        raise ValueError("Unknown test mode. Expected 'DRT' or 'MRT' in config.")

    config.update({
        "key": mode,
        "home_info": lang_config[mode]["home_info"],
        "home_header": "DIAGNOSTIC RHYME TEST" if mode == "DRT" else "MODIFIED RHYME TEST",
        "instructions": config[mode]["instructions"],
        "startButtonname": lang_config[mode]["startButtonname"],
        "testHTML": lang_config[mode]["testHTML"],
        "trial_temp": lang_config[mode]["trial_temp"],
        mode: {
            "wordItemDirectory": config[mode]["wordItemDirectory"],
            "audioDirectory": config[mode]["audioDirectory"]
        }
    })

    # Ensure answer directory exists
    answer_dir_path = os.path.join(config['answer_dir'])
    if not os.path.isdir(answer_dir_path):
        raise FileNotFoundError(f"The directory {answer_dir_path} does not exist.")

    config['answer_dir'] = answer_dir_path

    return config


def load_config(config_path):
    """
    Main function to parse, validate, and augment configuration.
    """
    try:
        config = parse_yaml(config_path)
        validate_config(config)
        config = augment_config(config)
    except Exception as e:
        raise RuntimeError(f"Failed to load configuration: {e}")
    return config
