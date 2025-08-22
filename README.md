# SITool - Speech Intelligibility Toolkit for Subjective Evaluation

**SITool** is a toolkit designed for evaluating speech intelligibility through subjective testing. 
It provides a Flask-based application designed to conduct intelligibility tests like the Diagnostic Rhyme Test (DRT) and Modified Rhyme Test (MRT) as well as a Python script for analyzing the results.

The web application allows participants to listen to audio samples, select answers and submit their responses for analysis.

## Table of Contents
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Language Proficiency Test](#language-proficiency-test)
- [Performance Measurement](#performance-measurement)
- [Evaluation & Analysis](#evaluation--analysis)
- [Citation](#citation)
- [References](#references)
- [License](#license)
- [Contact](#contact)

## Prerequisites

- **Python 3.9 or higher**

## Installation

To install **SITool**, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/audiolabs/SITool.git
   cd SITool
   ```

2. **Set up a Virtual Environment**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
    pip install -r requirements.txt
   ```

4. **Configure the Application** 
- Modify one of the YAML files in ```RhymeTest_webApp/config_files/``` to suit your test.
- Update the path to the YAML file in ```RhymeTest_webApp/config.py```, or use the default configuration.


5. **Create Results Folders**
   
   Ensure that the ```Results_DRT``` and/or ```Results_MRT``` **folders exist before running the tool**. If running on a server, verify that these directories have the necessary read/write permissions.
   
5. **Run the Application**

   ```bash
   flask --app RhymeTest_webApp run 
   ```
   or in debug mode
         
   ```bash
   flask --app RhymeTest_webApp run --debug
   ```
      
The application will be available at http://127.0.0.1:5000

## Project Structure

The repository is organized into two main folders: Evaluation and RhymeTest_webApp

```bash
├── Evaluation/             # Scripts for data analysis
│   ├── Example_Plots/      # Example plots from dummy data
│   ├── plots.py            # Analysis script 
├── Results_DRT/            # DRT results files
├── Results_MRT/            # MRT results files
├── RhymeTest_webApp/       # Main web application
│   ├── __init__.py         # Application factory
│   ├── routes.py           # Flask routes for English test
│   ├── routes_gr.py        # Flask routes for German test
│   ├── utils.py            # Helper functions
│   ├── config.py           # Flask configuration
│   ├── rhymeTest.py        # DRT and MRT logic       
│   ├── static/             # Static assets (CSS, JS, audio)
│   ├── templates/          # HTML templates
│   ├── config_files/       # Yaml config files
|       ├── config_DRT_gr_with_LP.yaml 
|       ├── config_DRT_gr_without_LP.yaml 
│       ├── config_DRT_with_LP.yaml 
│       ├── config_DRT_without_LP.yaml 
|       ├── config_MRT_with_LP.yaml     
|       ├── config_MRT_without_LP.yaml     
├── requirements.txt        # Python dependencies
├── app.wsgi                # WSGI entry point
├── README.md               # Project Documentation
```

### RhymeTest_webApp Folder 

The RhymeTest_webApp folder contains the web application for conducting rhyme tests, i.e., DRT and MRT, for speech intelligibility.

### Evaluation Folder

The Evaluation folder contains scripts for analysing the results obtained by the Web-Application.

### Test Results

Each test (DRT or MRT) generates the following output files per participant: 
- ```SubjectName_UserId_results_trial.txt``` - Trial results including item number, answer chosen by the participant, correct answer
- ```SubjectName_UserId_results.txt``` - Test results including item number, answer chosen by the participant, correct answer
- ```SubjectName_UserId_language_proficiency_results.txt``` - only if language proficiency test is included 

Also included: 
- Summary CSVs (```*_subjectivePerformance.csv```) - Contains participant's details, time taken to complete the test and the accuracy for each condition. For the DRT test, the accuracy for six specific features is also presented for each condition. 

## Configuration

### Yaml Config Files

Located in ```RhymeTest_webApp/config_files/```, choose a YAML file based on:
- Test type: DRT or MRT
- Language: English or German (gr)
- With or without Language Proficiency (LP) test

or create your own config file. 

### Key Parameters

- **`testName`**: Test identifier
- **`language`**: 'en' for English version and 'gr' for German version 
- **`testIterations`**:  Number of times the main test will be repeated for each condition 
  - Example: `For the DRT test, if 1 is selected, the audio for only one word from the word pair will be played during the test. If 2 is selected, both words in the pair will be played during the test. Similarly, for the MRT test, selecting 6 will play the audio for all six words in the set. Selecting 1 will result in only one word's audio being played during the test.` 
- **`testItemNumber`**:  Number of items (i.e., word pairs in case of DRT) in the test 
- **`trapQuestions`**:  Number of trap question - These questions help to filter out non performing participants. Trap questions are only run for the "reference". The reference is always chosen as the first condition in the list in the config file.
- **`trialIterations`**:  Number of times the trial condition is repeated - same as ```testIterations```
- **`trialItemNumber`**:  Number of items used for the trial
- **`trialCondition`**:  Condition used for the trial
- **`trialAudioDirectory`**:  Directory containing the audio files for the trial
- **`conditions`**:  List of test conditions
- **`answer_dir`**:  Where to store results
- **`consent_info`**:  HTML-formatted consent text displayed to participants before the test begins
- **`break`**: True if break included, else False
- **`LanguageProficiency`** (Optional): Include if language proficiency test is required
- **`DRT`**: DRT or MRT Block
   - **`wordItemDirectory`**: Path to the word file associated with the test
   - **`audioDirectory`**:  list of directories containing the condition directories with audio files.
   - **`instructions`**:  Instructions shown to participants before the test begins.


   Example configuration:
   ```bash
   testName: DRT TEST

   language : gr
   testIterations : 2
   testItemNumber : 6
   trapQuestions : 2

   trialIterations: 1
   trialItemNumber: 2
   trialCondition: condition1
   trialAudioDirectory: /static/speechFiles/DRT/German

   conditions:
      - condition1
      - condition2

   answer_dir : Results/

   consent_info : |
      <p>With your consent...</p>

   break: False

   LanguageProficiency:
      audioDirectory: speechFiles/language_proficiency
      imageDirectory: images/language_proficiency
      questions: ["Wohin schlägt der Mann vor, in den Urlaub zu fahren?", "Welches Tier haben die Kinder am liebsten gesehen?", "Wie sind sie nach Frankreich gereist?", "Was will sich der Junge jetzt ausleihen?", "Was wird das Mädchen an diesem Wochenende tun?"]
      correctResponse: ["test1_3.png", "test2_3.png", "test3_1.png", "test4_2.png", "test5_1.png"]
      maxIncorrectAnswers: 1

   DRT:
      wordItemDirectory : RhymeTest_webApp/static/drt_wrdlst_example.txt
      audioDirectory:
         - static/speechFiles/DRT
         - static/speechFiles/DRT

      instructions:
         - Once you play the audio...
   ```
### Python Configuration (```config.py```)

The ```config.py``` file contains core Flask settings that control the behavior of the web application.

Key parameters include:
- DEBUG – Enables debug mode; useful during development.
- SECRET_KEY – A secret key for securely signing the session cookie. Should be a long random bytes or str. 
- SESSION_TYPE – Defines the type of session interface to use (e.g., 'filesystem', 'redis', etc. ).

You will also need to define the path to your YAML configuration file in this script.

For more information about Flask application configuration, refer to the official [Flask documentation](https://flask.palletsprojects.com/en/stable/) and [Flask-Session documentation](https://flask-session.readthedocs.io/en/latest/#).


## Language Proficiency Test

You may include an optional Language Proficiency Test (LPT) to screen participants. 
Structure of the Language Proficiency Test was adapted from [Cambridge Listening Exams](https://www.cambridgeenglish.org/learning-english/activities-for-learners/b1l054-listening-to-dialogues).

### How It Works

- Participants answer a series of listening comprehension questions using visual cues.
- Only participants who pass this screening will proceed to the main test.
- This helps ensure that participants have sufficient language ability for subjective testing.

### Required Files

- ```audioDirectory```: Audio prompts for each question.
- ```imageDirectory```: Images corresponding to each question (3 images per question). 
- ```questions```: The comprehension questions.
- ```correctResponse```: Filenames of correct images.
- ```maxIncorrectAnswers```: Maximum number of incorrect answers allowed.

## Performance Measurement
As per [ANSI standard](#references):

```performance_value = (R - W / (num_response_alternatives - 1)) / (R + W) * 100```

where:
- R = Number of correct responses
- W = Number of incorrect responses
- num_response_alternatives = 2 for DRT and 6 for MRT 
- ```R - (W / (num_response_alternatives - 1))``` gives the number of correct answers after adjusting for chance guessing.

## Evaluation & Analysis

The ```Evaluation/``` folder contains tools to help you visualize and interpret test results.

### Running Evaluation
1. Ensure you have result files in ```Results_DRT/``` or ```Results_MRT/``` (you may use the provided dummy files).
2. Run the analysis script:

   ```bash
   python Evaluation/plots.py
   ```

### Output
- **Boxplots**: Compare intelligibility scores across conditions.
- **Heatmaps**: Visualize confusions or feature-level accuracy (e.g., voicing, nasality).

Dummy result data is provided to help you explore the analysis pipeline.


## Citation

If you use SITool in academic work, please cite: 

```bash
Leschanowsky, A., Kayyar Lakshminarayana, K., Rajasekhar, A., Behringer, L., Kilinc, I., Fuchs, G., Habets, E.A.P. (2025) Benchmarking Neural Speech Codec Intelligibility with SITool. Proc. Interspeech 2025, 5488-5492, doi: 10.21437/Interspeech.2025-984
```
```bash
@inproceedings{leschanowsky25_interspeech,
  title     = {{Benchmarking Neural Speech Codec Intelligibility with SITool}},
  author    = {{Anna Leschanowsky and Kishor {Kayyar Lakshminarayana} and Anjana Rajasekhar and Lyonel Behringer and Ibrahim Kilinc and Guillaume Fuchs and Emanuël A. P. Habets}},
  year      = {{2025}},
  booktitle = {{Interspeech 2025}},
  pages     = {{5488--5492}},
  doi       = {{10.21437/Interspeech.2025-984}},
  issn      = {{2958-1796}},
}
```

## References
- ANSI-ASA S3. 2, “Method for Measuring the Intelligibility of Speech Over Communication Systems”, American National Standards Institute New York, 2009.

## License 

See License file.

## Contact

For questions or further information, please contact:

**Email**: anna.leschanowsky@iis.fraunhofer.de
