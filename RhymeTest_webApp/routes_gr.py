from flask import Blueprint, render_template, redirect, request, session, current_app, url_for
from .rhymeTest import DRT, MRT
import datetime
import os
import random
bp = Blueprint('main', __name__)

@bp.route('/', methods=["POST", "GET"])
def home():
    return render_template('home_gr.html',
                           home_header=current_app.config["home_header"],
                           home_info=current_app.config["home_info"],
                           consent_info=current_app.config['consent_info'], info="")


@bp.route('/demographic', methods=["POST", "GET"])
def demographic():
    return render_template('demographic_gr.html',
                           home_header=current_app.config["home_header"])


@bp.route('/initialization', methods=["POST", 'GET'])
def initialize():
    if request.method == "POST":
        if len(request.form["age"]) == 0 or len(request.form["gender"]) == 0 or len(request.form["name"]) == 0:
            return render_template('demographic_gr.html', info='Leere Felder ausfüllen!')

        age = int(request.form["age"])
        if age < 18:
            return render_template('demographic_gr.html', info='Sie müssen mindestens 18 Jahre alt sein, um an dem Test teilnehmen zu können!')

        subject_name = request.form['name'].strip()
        user_id = request.form['userid']
        gender = request.form["gender"]
        lang = request.form['lang']
        session['username'] = f"{subject_name}_{user_id}_{age}_{gender}"
        completion_code = random.randint(10000, 99999)

        session["user_data"] = {
            'subject_name': subject_name,
            'code': completion_code,
            'user_id': user_id,
            'age': age,
            'lang': lang,
            'current_index': 0,
            'current_test': 1,
            'gender': gender,
            'condition_index': 0,
            'temp_data': {},
            'trial_temp_data': {},
            'trial_current_index': 0,
            'start_timer': True,
            'durations': []
            }

        if current_app.config.get("DRT"):
            session['user_data']['method'] = DRT(current_app.config['testIterations'],
                                                 current_app.config['testItemNumber'],
                                                 current_app.config['numberOfConditions'],
                                                 current_app.config['testName'],
                                                 current_app.config['trapQuestions'])
            session['user_data']['trial'] = DRT(current_app.config['trialIterations'],
                                                current_app.config['trialItemNumber'],
                                                1,
                                                current_app.config['testName'],
                                                0)
        elif current_app.config.get('MRT'):
            session['user_data']['method'] = MRT(current_app.config['testIterations'],
                                                 current_app.config['testItemNumber'],
                                                 current_app.config['numberOfConditions'],
                                                 current_app.config['testName'],
                                                 current_app.config['trapQuestions'])
            session['user_data']['trial'] = MRT(current_app.config['trialIterations'],
                                               current_app.config['trialItemNumber'],
                                               1,
                                               current_app.config['testName'],
                                               0)

        session['user_data']['trial'].startTest(current_app.config[current_app.config['key']]['wordItemDirectory'])
        session['user_data']['trial_overall'] = session['user_data']['trial'].testItemNumber * session['user_data']['trial'].testIterations
        session['user_data']['method'].startTest(current_app.config[current_app.config['key']]['wordItemDirectory'])
        session['user_data']['overall'] = (session['user_data']['method'].testItemNumber - session['user_data']['method'].trapConditions + 1) * session['user_data']['method'].testIterations

        print(f"Testdata Session username: {session['user_data']}")
        print(f"Session username Initialization: {session.get('username')}")

        try:
            if current_app.config['LanguageProficiency']:
                # Initialize counters in the session if not already set
                session['user_data']["language_proficiency_correct_count"] = 0
                session['user_data']["language_proficiency_incorrect_count"] = 0
                # Render the instructions page first
                return render_template('language_proficiency_instructions_gr.html')
        except KeyError:
            return render_template('initial_gr.html', instructions=current_app.config['instructions'],
                                   buttonName="Trial Test starten")

    return render_template('home_gr.html',
                           home_header=current_app.config["home_header"],
                           home_info=current_app.config["home_info"],
                           consent_info=current_app.config['consent_info'],
                           info="")


def save_lp_test_result(subject_name, user_id, path, test_number, question, user_answer, correct_answer, is_correct):
    """Saves language proficiency test results"""
    filename = os.path.join(path, f"{subject_name}_{user_id}_language_proficiency_results.txt")
    # Check if the file exists to add a header only for new files
    file_exists = os.path.isfile(filename)

    with open(filename, 'a') as file:
        # Write header if file is new
        if not file_exists:
            file.write("Test Number;Question;User Answer;Correct Answer;Result\n")

        # Write test results in a tabular format
        file.write(f"{test_number};{question};{user_answer};{correct_answer};{'Correct' if is_correct else 'Incorrect'}\n")


@bp.route("/language_proficiency/<test_number>", methods=["POST", "GET"])
def language_proficiency(test_number):
    config = current_app.config["LanguageProficiency"]
    audio_dir, image_dir, questions, correct_responses = config["audioDirectory"], config["imageDirectory"], config["questions"], config["correctResponse"]
    last_test_number = len(correct_responses) + 1

    show_overlay = False
    # If it's the last test, render the initial page
    if int(test_number) == last_test_number:
        # Check if the test should end
        if session['user_data']["language_proficiency_incorrect_count"] > config["maxIncorrectAnswers"]:
            return render_template("language_proficiency_failure_gr.html")
        else:
            return render_template('initial_gr.html', instructions=current_app.config['instructions'],
                                   buttonName="Trial Test starten")

    # Get correct answers from config
    correct_answer = correct_responses[int(test_number) - 1]

    # Process POST request for user's answer
    if request.method == "POST":
        user_answer = request.form.get("user_answer").split("/")[-1]
        is_correct = user_answer == correct_answer
        # Update counters
        if is_correct:
            session['user_data']["language_proficiency_correct_count"] += 1
        else:
            session['user_data']["language_proficiency_incorrect_count"] += 1

        # Save results to the CSV file
        save_lp_test_result(
            session['user_data']['subject_name'],
            session['user_data']['user_id'],
            current_app.config['answer_dir'],
            test_number,
            questions[int(test_number) - 1],
            user_answer,
            correct_answer,
            is_correct
        )

        # Redirect to next test or complete
        next_test_number = int(test_number) + 1
        next_test_url = url_for("main.language_proficiency", test_number=next_test_number)

        show_overlay = True
        # Pass the result and next URL to the template
        return render_template(
            'language_proficiency_gr.html',
            test_number=test_number,
            audio_path=url_for('static', filename=f"{audio_dir}/test{test_number}.mp3"),
            image_paths=[url_for('static', filename=f"{image_dir}/test{test_number}_{i}.png") for i in range(1, 4)],
            question=questions[int(test_number) - 1],
            correct_answer=correct_answer,
            is_correct=is_correct,
            next_test_url=next_test_url,
            show_overlay=show_overlay
        )

    # Generate paths for audio and images
    audio_path = url_for('static', filename=f"{audio_dir}/test{test_number}.mp3")
    image_paths = [url_for('static', filename=f"{image_dir}/test{test_number}_{i}.png") for i in range(1, 4)]

    # Render the language proficiency test page
    return render_template(
        'language_proficiency_gr.html',
        test_number=test_number,
        audio_path=audio_path,
        image_paths=image_paths,
        question=questions[int(test_number) - 1],
        correct_answer=correct_answer,
        show_overlay=show_overlay
    )


@bp.route("/trial", methods=["POST", "GET"])
def trial():
    if request.method == "POST":
        if request.args.get('f') is not None:
            print(f"Session username Trial: {session.get('username')}")
            answer = request.form["item" + request.args.get('f')]
            session['user_data']['trial'].storeAnswers(1,
                                                       current_app.config['trialCondition'],
                                                       session['user_data']['trial_temp_data']['wordItemIndex'],
                                                       session['user_data']['trial_temp_data']['wordIndex'],
                                                       answer)

        # Next item to display
        item, wordIndex, wordItemIndex, condition_index = session['user_data']['trial'].getItemToDisplay(1)

        if item is not None:
            session['user_data']['trial_temp_data']['wordIndex'] = wordIndex
            session['user_data']['trial_temp_data']['wordItemIndex'] = wordItemIndex

            audioDirectory = current_app.config['trialAudioDirectory'] + f"/{current_app.config['trialCondition']}/{current_app.config['trialCondition']}_{wordItemIndex}_{wordIndex}.wav"
            session['user_data']['trial_current_index'] += 1
            return render_template(current_app.config['trial_temp'],
                                   item=item,
                                   itemIndex=wordItemIndex + 1,
                                   audioDirectory=audioDirectory,
                                   currentItem=session['user_data']['trial_current_index'],
                                   overall=session['user_data']['trial_overall'],
                                   ends=False,
                                   test="Trial Test")
        else:
            # End of Trial, Calculate Performance
            performance = session['user_data']['trial'].calculatePerformance(
                subject_name=session['user_data']['subject_name'],
                code=session['user_data']['code'],
                user_id=session['user_data']['user_id'],
                gender=session['user_data']['gender'],
                age=session['user_data']['age'], lang=session['user_data']['lang'],
                answerDir=current_app.config['answer_dir'],
                is_trial=True,
                durations=[],
                num_response_alternatives=2 if current_app.config.get("DRT") else 6)
            session['user_data']['trial'].saveTestQuestionsAndAnswers(session['user_data']['subject_name'],
                                                                      session['user_data']['user_id'],
                                                                      current_app.config['answer_dir'],
                                                                      is_trial=True)
            info = "Sie können den Test starten"
            return render_template(current_app.config['trial_temp'],
                                   performance=performance,
                                   info=info,
                                   ends=True,
                                   buttonName=current_app.config['startButtonname'])
    else:
        return render_template('home_gr.html',
                               home_header=current_app.config["home_header"],
                               home_info=current_app.config["home_info"],
                               consent_info=current_app.config['consent_info'],
                               info="")


@bp.route("/test", methods=['POST', 'GET'])
def test():
    if request.method == "POST":
        if request.args.get('f') is not None:
            if session['user_data']['start_timer']:
                session['user_data']['start_time'] = datetime.datetime.now()
                session['user_data']['start_timer'] = False
            answer = request.form["item" + request.args.get('f')]
            session['user_data']['method'].storeAnswers(session['user_data']['current_test'],
                                                        current_app.config['conditions'][session['user_data']['temp_data']['condition_index']],
                                                        session['user_data']['temp_data']['wordItemIndex'],
                                                        session['user_data']['temp_data']['wordIndex'],
                                                        answer)

        item, wordIndex, wordItemIndex, condition_index = session['user_data']['method'].getItemToDisplay(session['user_data']['current_test'])

        show_timer = False
        if item is not None:
            session['user_data']['temp_data']['wordIndex'] = wordIndex
            session['user_data']['temp_data']['wordItemIndex'] = wordItemIndex
            session['user_data']['temp_data']['condition_index'] = condition_index

            audioDirectory = current_app.config[current_app.config['key']]['audioDirectory'][condition_index] + f"/{current_app.config['conditions'][condition_index]}/{current_app.config['conditions'][condition_index]}_{wordItemIndex}_{wordIndex}.wav"
            session['user_data']['current_index'] += 1

            return render_template(current_app.config['testHTML'],
                                   item=item,
                                   itemIndex=wordItemIndex + 1,
                                   audioDirectory=audioDirectory,
                                   currentItem=session['user_data']['current_index'],
                                   overall=session['user_data']['overall'],
                                   test_number=session['user_data']['current_test'],
                                   numberOfConditions=current_app.config['numberOfConditions'],
                                   test=current_app.config['testName'],
                                   show_timer=show_timer)
        else:
            session['user_data']['end_time'] = datetime.datetime.now()
            session['user_data']['durations'].append((session['user_data']['end_time'] -
                                                      session['user_data']['start_time']).total_seconds())
            session['user_data']['start_timer'] = True
            if session['user_data']['condition_index'] == current_app.config['numberOfConditions'] - 1:
                session['user_data']['method'].calculatePerformance(session['user_data']['subject_name'],
                                                                    session['user_data']['code'],
                                                                    session['user_data']['user_id'],
                                                                    session['user_data']['gender'],
                                                                    session['user_data']['age'],
                                                                    session['user_data']['lang'],
                                                                    current_app.config['answer_dir'],
                                                                    is_trial=False,
                                                                    durations=session['user_data']['durations'],
                                                                    num_response_alternatives=2 if current_app.config.get("DRT") else 6)
                session['user_data']['method'].saveTestQuestionsAndAnswers(session['user_data']['subject_name'],
                                                                            session['user_data']['user_id'],
                                                                            current_app.config['answer_dir'],
                                                                            is_trial=False
                                                                           )
                del session['username']
                completion_code = session['user_data']['code']
                return render_template('complete_gr.html',completion_code=completion_code)
            else:
                session['user_data']['condition_index'] += 1
                session['user_data']['current_index'] = 1
                session['user_data']['current_test'] += 1
                session['user_data']['method'].reset()
                item, wordIndex, wordItemIndex, condition_index = session['user_data']['method'].getItemToDisplay(session['user_data']['current_test'])
                session['user_data']['temp_data']['wordIndex'] = wordIndex
                session['user_data']['temp_data']['wordItemIndex'] = wordItemIndex
                session['user_data']['temp_data']['condition_index'] = condition_index
                audioDirectory = current_app.config[current_app.config['key']]['audioDirectory'][condition_index] + f"/{current_app.config['conditions'][condition_index]}/{current_app.config['conditions'][condition_index]}_{wordItemIndex}_{wordIndex}.wav"

                if current_app.config["break"]:
                    halfway_point = current_app.config["numberOfConditions"] // 2
                    show_timer = session['user_data']['current_test'] == halfway_point + 1

                return render_template(current_app.config['testHTML'],
                                       item=item,
                                       itemIndex=wordItemIndex + 1,
                                       audioDirectory=audioDirectory,
                                       currentItem=session['user_data']['current_index'],
                                       overall=session['user_data']['overall'],
                                       test=current_app.config['testName'],
                                       test_number=session['user_data']['current_test'],
                                       numberOfConditions=current_app.config['numberOfConditions'],
                                       show_timer=show_timer)
    else:
        return render_template('home_gr.html',
                               home_header=current_app.config["home_header"],
                               home_info=current_app.config["home_info"],
                               consent_info=current_app.config['consent_info'],
                               info="")
